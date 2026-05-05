"""Location Service entry point — upgraded from cache-only stub.

Lifespan wires:
  1. CacheManager       (Redis — existing)
  2. RedisLocationStore (live location — Redis Geo + Hash)
  3. PostGISLocationRepository (history — PostgreSQL + PostGIS)
  4. LocationRateLimiter (Redis INCR)
  5. WebSocketManager   (in-process broadcast hub)
  6. KafkaProducerWrapper + EventPublisher (location-events topic)
  7. LocationEventPublisher (domain → Kafka)
  8. LocationKafkaConsumer  (ride-events → subscription management)
  9. MapboxClient        (geocoding — httpx + cache)
"""
from __future__ import annotations

import asyncio
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager, suppress

from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse
from sp.core.config import get_settings
from sp.core.observability.logging import setup_logging
from sp.core.observability.metrics import MetricsCollector
from sp.core.observability.middleware import ObservabilityMiddleware
from sp.infrastructure.cache.manager import get_cache_manager_factory
from sp.infrastructure.db.engine import get_db_engine
from sp.infrastructure.db.session import get_session_factory
from sp.infrastructure.messaging.kafka import KafkaProducerWrapper
from sp.infrastructure.messaging.publisher import EventPublisher
from sqlalchemy import text

from .api.router import router
from .infrastructure.event_publisher import LocationEventPublisher
from .infrastructure.kafka_consumer import LocationKafkaConsumer
from .infrastructure.mapbox_client import MapboxClient
from .infrastructure.postgis_repository import PostGISLocationRepository
from .infrastructure.rate_limiter import LocationRateLimiter
from .infrastructure.redis_store import RedisLocationStore
from .infrastructure.websocket_manager import WebSocketManager

SERVICE_NAME = "location"


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    settings = get_settings()
    setup_logging(SERVICE_NAME, level=settings.LOG_LEVEL, log_format=settings.LOG_FORMAT)

    # 1. Redis cache (existing)
    cache = get_cache_manager_factory(settings)
    await cache.connect()

    # 2. PostgreSQL engine + session factory (new — for PostGIS history)
    engine = get_db_engine(settings.POSTGRES_DB_URI, settings.POSTGRES_POOL_SIZE)
    session_factory = get_session_factory(settings)

    # 3. Core infrastructure singletons
    redis_store = RedisLocationStore(cache=cache)
    history_repo = PostGISLocationRepository(session_factory=session_factory)
    rate_limiter = LocationRateLimiter(cache=cache)
    ws_manager = WebSocketManager()

    # 4. Kafka producer (best-effort — gracefully no-ops if KAFKA_BOOTSTRAP_SERVERS unset)
    producer: KafkaProducerWrapper | None = None
    platform_publisher: EventPublisher | None = None

    if settings.KAFKA_BOOTSTRAP_SERVERS:
        producer = KafkaProducerWrapper(
            bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
            client_id="location-producer",
        )
        platform_publisher = EventPublisher(
            topic="location-events",
            producer=producer,
        )

    # Always create a concrete publisher — LocationEventPublisher guards publish
    # calls with `if self._publisher is None: return` so it's a safe no-op when
    # Kafka is not configured. This keeps app.state.event_publisher non-nullable.
    event_publisher = LocationEventPublisher(publisher=platform_publisher)

    # 5. Kafka consumer (subscribes to ride-events)
    kafka_consumer: LocationKafkaConsumer | None = None
    if settings.KAFKA_BOOTSTRAP_SERVERS:
        kafka_consumer = LocationKafkaConsumer(
            bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
            store=redis_store,
            ws_manager=ws_manager,
            settings=settings,
        )
        await kafka_consumer.start()

    # 6. Mapbox geocoding client
    mapbox = MapboxClient(
        access_token=settings.MAPBOX_ACCESS_TOKEN,
        cache=cache,
    )

    # 7. Expose all singletons on app.state for DI providers
    app.state.cache = cache
    app.state.engine = engine
    app.state.session_factory = session_factory
    app.state.redis_store = redis_store
    app.state.history_repo = history_repo
    app.state.rate_limiter = rate_limiter
    app.state.ws_manager = ws_manager
    app.state.event_publisher = event_publisher
    app.state.mapbox = mapbox
    app.state.metrics = MetricsCollector(SERVICE_NAME)

    # 8. Daily PostGIS history cleanup background task
    _cleanup_task = asyncio.create_task(
        _run_history_cleanup(session_factory, settings.LOCATION_HISTORY_RETENTION_DAYS),
        name="location_history_cleanup",
    )

    yield  # ── service is running ────────────────────────────────────────

    # Graceful shutdown
    _cleanup_task.cancel()
    with suppress(asyncio.CancelledError):
        await _cleanup_task
    if kafka_consumer:
        await kafka_consumer.stop()
    if producer:
        await producer.close()
    await mapbox.close()
    await cache.close()
    # engine is cached by get_db_engine (@lru_cache) — do not dispose here


def create_app() -> FastAPI:
    app = FastAPI(
        title="SafarPay Location Service",
        version="2.0.0",
        description=(
            "Real-time GPS tracking, live ride location broadcasting, "
            "and Mapbox geocoding for the SafarPay platform."
        ),
        lifespan=lifespan,
    )
    app.add_middleware(ObservabilityMiddleware, service_name=SERVICE_NAME)
    app.include_router(router, prefix="/api/v1/location")

    @app.get("/health", tags=["ops"])
    async def health(request: Request):
        ws_stats = request.app.state.ws_manager.stats if hasattr(request.app.state, "ws_manager") else {}

        # PostGIS health probe
        postgis_status = "unknown"
        try:
            sf = getattr(request.app.state, "session_factory", None)
            if sf:
                async with sf() as session:
                    await session.execute(text("SELECT 1"))
                postgis_status = "ok"
            else:
                postgis_status = "not_configured"
        except Exception:  # noqa: BLE001
            postgis_status = "degraded"

        return {
            "status": "ok",
            "service": SERVICE_NAME,
            "postgis": postgis_status,
            "websockets": ws_stats,
        }

    @app.get("/metrics", tags=["ops"])
    async def metrics(request: Request):
        return PlainTextResponse(request.app.state.metrics.expose_prometheus())

    return app


# ---------------------------------------------------------------------------
# Background tasks
# ---------------------------------------------------------------------------


async def _run_history_cleanup(
    session_factory,
    retention_days: int,
    interval_seconds: int = 86_400,  # once per day
) -> None:
    """Delete PostGIS location_history rows older than retention_days.

    Runs as a long-lived asyncio.Task in the service lifespan.  CancelledError
    is expected on shutdown and is re-raised normally by the task machinery.
    """
    import logging
    _log = logging.getLogger("location.cleanup")

    while True:
        await asyncio.sleep(interval_seconds)
        try:
            async with session_factory() as session:
                result = await session.execute(
                    text("""
                        DELETE FROM location.location_history
                        WHERE ingested_at < now() - make_interval(days => :days)
                    """),
                    {"days": retention_days},
                )
                await session.commit()
                _log.info(
                    "History cleanup: deleted %d rows older than %d days",
                    result.rowcount, retention_days,
                )
        except asyncio.CancelledError:
            raise
        except Exception as exc:  # noqa: BLE001
            _log.exception("History cleanup failed: %s", exc)


app = create_app()
