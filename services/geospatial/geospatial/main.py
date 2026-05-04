"""Geospatial Service application entrypoint.

Follows the ``create_app()`` factory pattern used by Location and other services.

Lifespan wires:
  1. LocationClient      (HTTP → Location Service)
  2. MapboxClient        (HTTP → Mapbox Directions/Matrix APIs)
  3. H3IndexAdapter      (in-process spatial indexing)
  4. KafkaProducerWrapper + EventPublisher (geospatial-events topic)
  5. GeospatialKafkaConsumer (ride-events → driver matching)
  6. MetricsCollector     (Prometheus-compatible)
"""
from __future__ import annotations

import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse, PlainTextResponse
from sp.core.config import get_settings
from sp.core.observability.logging import setup_logging
from sp.core.observability.metrics import MetricsCollector
from sp.core.observability.middleware import ObservabilityMiddleware
from sp.infrastructure.db.engine import get_db_engine
from sp.infrastructure.db.session import get_session_factory
from sp.infrastructure.messaging.kafka import KafkaProducerWrapper
from sp.infrastructure.messaging.publisher import EventPublisher
from sqlalchemy import text

from .api.router import router
from .application.use_cases import FindNearbyDriversUseCase
from .infrastructure.h3_index import H3IndexAdapter
from .infrastructure.kafka_consumer import GeospatialKafkaConsumer
from .infrastructure.location_client import LocationClient
from .infrastructure.mapbox_client import MapboxClient

SERVICE_NAME = "geospatial"

logger = logging.getLogger("geospatial.main")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan: start/stop clients, consumers, producers."""
    settings = get_settings()
    setup_logging(SERVICE_NAME, level=settings.LOG_LEVEL, log_format=settings.LOG_FORMAT)

    # 1. PostgreSQL engine + session factory (for PostGIS zone queries)
    engine = get_db_engine(settings.POSTGRES_DB_URI, settings.POSTGRES_POOL_SIZE)
    session_factory = get_session_factory(settings)

    # 2. External HTTP clients
    location_client = LocationClient(
        base_url=settings.LOCATION_SERVICE_URL,
        jwt_secret=settings.JWT_SECRET,
        jwt_algorithm=settings.JWT_ALGORITHM,
    )
    await location_client.start()

    routing_client = MapboxClient(settings.MAPBOX_ACCESS_TOKEN)
    await routing_client.start()

    # 3. H3 spatial indexing (in-process, no startup needed)
    h3_index = H3IndexAdapter()

    # 4. Kafka producer → EventPublisher
    producer: KafkaProducerWrapper | None = None
    publisher: EventPublisher | None = None
    consumer: GeospatialKafkaConsumer | None = None

    if settings.KAFKA_BOOTSTRAP_SERVERS:
        producer = KafkaProducerWrapper(
            bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
            client_id="geospatial-producer",
        )
        publisher = EventPublisher(
            topic="geospatial-events",
            producer=producer,
        )

        # 5. Build use cases for the Kafka consumer
        find_nearby_uc = FindNearbyDriversUseCase(
            location_provider=location_client,
            routing_client=routing_client,
            h3_index=h3_index,
            h3_resolution=settings.GEOSPATIAL_H3_RESOLUTION,
        )

        consumer = GeospatialKafkaConsumer(
            bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
            session_factory=session_factory,
            find_nearby_uc=find_nearby_uc,
            publisher=publisher,
            dlq_producer=producer,
        )
        await consumer.start()
    else:
        logger.warning("KAFKA_BOOTSTRAP_SERVERS not set — messaging disabled")

    # 6. Expose on app.state for DI providers
    app.state.engine = engine
    app.state.session_factory = session_factory
    app.state.location_client = location_client
    app.state.routing_client = routing_client
    app.state.h3_index = h3_index
    app.state.publisher = publisher
    app.state.metrics = MetricsCollector(SERVICE_NAME)

    logger.info("Geospatial Service started")
    yield

    # Graceful shutdown
    logger.info("Geospatial Service shutting down...")
    if consumer:
        await consumer.stop()
    if producer:
        await producer.close()
    await routing_client.close()
    await location_client.close()
    logger.info("Geospatial Service stopped")


def create_app() -> FastAPI:
    """Application factory — consistent with other SafarPay services."""
    application = FastAPI(
        title="SafarPay Geospatial Service",
        version="1.0.0",
        description=(
            "Spatial intelligence layer: driver matching, routing, "
            "surge zones, and geofencing for the SafarPay platform."
        ),
        lifespan=lifespan,
    )
    application.add_middleware(ObservabilityMiddleware, service_name=SERVICE_NAME)
    application.include_router(router, prefix="/api/v1")

    @application.get("/health", tags=["ops"])
    async def health(request: Request) -> JSONResponse:
        """Readiness probe with PostGIS connectivity check."""
        postgis_status = "unknown"
        try:
            sf = getattr(request.app.state, "session_factory", None)
            if sf:
                async with sf() as session:
                    await session.execute(text("SELECT PostGIS_Version()"))
                postgis_status = "ok"
            else:
                postgis_status = "not_configured"
        except Exception:  # noqa: BLE001
            postgis_status = "degraded"

        return JSONResponse(
            content={
                "status": "ok",
                "service": SERVICE_NAME,
                "postgis": postgis_status,
                "environment": request.app.state.metrics._service_name,
            },
            status_code=status.HTTP_200_OK,
        )

    @application.get("/metrics", tags=["ops"])
    async def metrics(request: Request) -> PlainTextResponse:
        return PlainTextResponse(request.app.state.metrics.expose_prometheus())

    return application


app = create_app()
