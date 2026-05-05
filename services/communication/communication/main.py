"""Communication service entry point."""
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
from .infrastructure.storage import S3StorageProvider
from .infrastructure.websocket_manager import WebSocketManager

SERVICE_NAME = "communication"
KAFKA_TOPIC = "communication-events"


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    settings = get_settings()
    app.state.settings = settings
    setup_logging(SERVICE_NAME, level=settings.LOG_LEVEL, log_format=settings.LOG_FORMAT)

    app.state.db_engine = get_db_engine(settings.POSTGRES_DB_URI, settings.POSTGRES_POOL_SIZE)
    app.state.session_factory = get_session_factory(settings)

    app.state.cache = get_cache_manager_factory(settings)
    await app.state.cache.connect()
    app.state.metrics = MetricsCollector(SERVICE_NAME)
    app.state.ws_manager = WebSocketManager()
    app.state.storage = S3StorageProvider()

    app.state.publisher = None
    app.state.consumer = None
    app.state.outbox = None
    if settings.KAFKA_BOOTSTRAP_SERVERS:
        producer = KafkaProducerWrapper(
            settings.KAFKA_BOOTSTRAP_SERVERS,
            client_id=f"{SERVICE_NAME}-producer",
        )
        app.state.publisher = EventPublisher(topic=KAFKA_TOPIC, producer=producer)

        from .infrastructure.kafka_consumer import CommunicationKafkaConsumer
        from .infrastructure.orm_models import CommunicationEventORM

        app.state.consumer = CommunicationKafkaConsumer(
            bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
            session_factory=app.state.session_factory,
            cache=app.state.cache,
            ws=app.state.ws_manager,
        )
        await app.state.consumer.start()

        app.state.outbox = GenericOutboxWorker(
            app.state.session_factory,
            app.state.publisher,
            CommunicationEventORM,
            default_topic=KAFKA_TOPIC,
            batch_size=100,
            interval_seconds=2.0,
        )
        await app.state.outbox.start()

    yield

    if app.state.outbox:
        await app.state.outbox.stop()
    if app.state.consumer:
        await app.state.consumer.stop()
    if app.state.publisher:
        await app.state.publisher.close()
    await app.state.cache.close()
    await app.state.db_engine.dispose()


def create_app() -> FastAPI:
    app = FastAPI(
        title="SafarPay Communication Service",
        description="Ride-scoped real-time chat, S3 media uploads, and WebRTC signaling.",
        version="1.0.0",
        lifespan=lifespan,
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
