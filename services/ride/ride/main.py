"""Ride service entry point.

Startup sequence
----------------
1. Logging & observability
2. DB engine
3. Redis cache
4. Kafka publisher (optional — skipped if KAFKA_BOOTSTRAP_SERVERS is unset)
5. WebSocket manager
6. Webhook client  (notification/dispatch service)
7. Geospatial client
8. Notification client
9. Prometheus metrics middleware
"""
from __future__ import annotations

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

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
from sp.infrastructure.messaging.outbox import GenericOutboxWorker
from sp.infrastructure.messaging.publisher import EventPublisher

from .api.router import router
from .infrastructure.geospatial_client import GeospatialClient, NullGeospatialClient
from .infrastructure.notification_client import NotificationClient, NullNotificationClient
from .infrastructure.orm_models import RideOutboxEventORM
from .infrastructure.storage import S3StorageProvider
from .infrastructure.webhook_client import NullWebhookClient, WebhookClient
from .infrastructure.websocket_manager import WebSocketManager

SERVICE_NAME = "ride"
KAFKA_TOPIC = "ride-events"


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    settings = get_settings()

    # ── Logging ───────────────────────────────────────────────────────────────
    setup_logging(SERVICE_NAME, level=settings.LOG_LEVEL, log_format=settings.LOG_FORMAT)

    # ── Database ──────────────────────────────────────────────────────────────
    app.state.db_engine = get_db_engine(
        settings.POSTGRES_DB_URI, settings.POSTGRES_POOL_SIZE
    )
    app.state.session_factory = get_session_factory(settings)

    # ── Redis ─────────────────────────────────────────────────────────────────
    cache = get_cache_manager_factory(settings)
    await cache.connect()
    app.state.cache = cache

    # ── Metrics ───────────────────────────────────────────────────────────────
    app.state.metrics = MetricsCollector(SERVICE_NAME)

    # ── Kafka publisher ───────────────────────────────────────────────────────
    app.state.publisher = None
    app.state.outbox_worker = None
    if settings.KAFKA_BOOTSTRAP_SERVERS:
        producer = KafkaProducerWrapper(
            settings.KAFKA_BOOTSTRAP_SERVERS,
            client_id=f"{SERVICE_NAME}-producer",
        )
        app.state.publisher = EventPublisher(topic=KAFKA_TOPIC, producer=producer)
        app.state.outbox_worker = GenericOutboxWorker(
            app.state.session_factory,
            app.state.publisher,
            RideOutboxEventORM,
            default_topic=KAFKA_TOPIC,
        )
        await app.state.outbox_worker.start()

    # ── WebSocket manager ─────────────────────────────────────────────────────
    app.state.ws_manager = WebSocketManager()

    # ── Webhook client ────────────────────────────────────────────────────────
    notification_url = getattr(settings, "NOTIFICATION_SERVICE_URL", "")
    if notification_url:
        webhook = WebhookClient(notification_url)
        await webhook.start()
        app.state.webhook_client = webhook
    else:
        app.state.webhook_client = NullWebhookClient()

    # ── Geospatial client ─────────────────────────────────────────────────────
    geo_url = getattr(settings, "GEOSPATIAL_SERVICE_URL", "")
    if geo_url:
        geo = GeospatialClient(geo_url)
        await geo.start()
        app.state.geo_client = geo
    else:
        app.state.geo_client = NullGeospatialClient()

    # ── Notification client ───────────────────────────────────────────────────
    if notification_url:
        notif = NotificationClient(notification_url)
        await notif.start()
        app.state.notification_client = notif
    else:
        app.state.notification_client = NullNotificationClient()

    # ── S3 Storage provider (presigned URLs for proof images) ─────────────────
    # boto3 resolves credentials from env vars / IAM / ~/.aws automatically.
    # If AWS credentials are absent (local dev) boto3 will raise only when a
    # URL is actually generated, not at startup — so this is safe to always init.
    app.state.storage = S3StorageProvider()

    # ── Kafka consumer ────────────────────────────────────────────────────────
    app.state.consumer = None
    if settings.KAFKA_BOOTSTRAP_SERVERS:
        from .infrastructure.kafka_consumer import RideKafkaConsumer
        consumer = RideKafkaConsumer(
            bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
            session_factory=app.state.session_factory,
            cache=app.state.cache,
            ws=app.state.ws_manager,
            publisher=app.state.publisher,
        )
        await consumer.start()
        app.state.consumer = consumer

    # ── Ready ─────────────────────────────────────────────────────────────────
    yield

    # ── Teardown ──────────────────────────────────────────────────────────────
    if getattr(app.state, "consumer", None):
        try:
            await app.state.consumer.stop()
        except Exception as e:
            import logging
            logging.getLogger("ride.main").error("Failed to stop consumer: %s", e)

    if getattr(app.state, "outbox_worker", None):
        try:
            await app.state.outbox_worker.stop()
        except Exception as e:
            import logging
            logging.getLogger("ride.main").error("Failed to stop outbox worker: %s", e)

    try:
        await app.state.cache.close()
    except Exception as e:
        import logging
        logging.getLogger("ride.main").error("Failed to close cache: %s", e)

    try:
        await app.state.db_engine.dispose()
    except Exception as e:
        import logging
        logging.getLogger("ride.main").error("Failed to dispose db engine: %s", e)

    if app.state.publisher:
        try:
            await app.state.publisher.close()
        except Exception as e:
            import logging
            logging.getLogger("ride.main").error("Failed to close publisher: %s", e)

    webhook_client = app.state.webhook_client
    if hasattr(webhook_client, "close"):
        try:
            await webhook_client.close()
        except Exception as e:
            import logging
            logging.getLogger("ride.main").error("Failed to close webhook client: %s", e)

    geo_client = app.state.geo_client
    if hasattr(geo_client, "close"):
        try:
            await geo_client.close()
        except Exception as e:
            import logging
            logging.getLogger("ride.main").error("Failed to close geo client: %s", e)

    notif_client = app.state.notification_client
    if hasattr(notif_client, "close"):
        try:
            await notif_client.close()
        except Exception as e:
            import logging
            logging.getLogger("ride.main").error("Failed to close notif client: %s", e)


def create_app() -> FastAPI:
    app = FastAPI(
        title="SafarPay Ride Service",
        description=(
            "Manages the full lifecycle of passenger ride requests: "
            "creation, matching, acceptance, tracking, stops, verification, "
            "proof-of-service, Kafka events, Redis caching, and WebSocket delivery."
        ),
        version="1.0.0",
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
    )

    app.add_middleware(ObservabilityMiddleware, service_name=SERVICE_NAME)
    app.include_router(router, prefix="/api/v1")

    @app.get("/health", tags=["ops"])
    async def health() -> dict:
        return {"status": "ok", "service": SERVICE_NAME}

    @app.get("/metrics", tags=["ops"])
    async def metrics(request: Request) -> PlainTextResponse:
        return PlainTextResponse(request.app.state.metrics.expose_prometheus())

    return app


app = create_app()
