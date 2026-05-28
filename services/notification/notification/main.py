"""Notification service entry point — event-driven, no DB."""
from __future__ import annotations

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse
from sp.core.config import get_settings
from sp.core.observability.logging import setup_logging
from sp.core.observability.metrics import MetricsCollector
from sp.core.observability.middleware import ObservabilityMiddleware
from sp.infrastructure.db.session import get_session_factory
from sp.infrastructure.messaging.kafka import KafkaProducerWrapper, ensure_kafka_topics
from sp.infrastructure.messaging.publisher import EventPublisher

from .api.router import router
from .infrastructure.kafka_consumer import NotificationKafkaConsumer
from .infrastructure.push_client import PushClient

SERVICE_NAME = "notification"

NOTIFICATION_KAFKA_TOPICS = [
    "notification-events",
    "ride-events",
    "bidding-events",
    "payment-events",
    "communication-events",
    "geospatial-events",
]


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    settings = get_settings()
    setup_logging(SERVICE_NAME, level=settings.LOG_LEVEL, log_format=settings.LOG_FORMAT)
    app.state.metrics = MetricsCollector(SERVICE_NAME)
    app.state.publisher = None
    app.state.consumer = None
    app.state.push_client = PushClient(
        server_key=settings.FCM_SERVER_KEY,
        send_url=settings.FCM_SEND_URL,
        service_account_json=settings.FCM_SERVICE_ACCOUNT_JSON,
        service_account_json_base64=settings.FCM_SERVICE_ACCOUNT_JSON_BASE64,
        service_account_file=settings.FCM_SERVICE_ACCOUNT_FILE,
        project_id=settings.FCM_PROJECT_ID,
    )
    if settings.KAFKA_BOOTSTRAP_SERVERS:
        await ensure_kafka_topics(
            settings.KAFKA_BOOTSTRAP_SERVERS,
            NOTIFICATION_KAFKA_TOPICS,
            client_id=f"{SERVICE_NAME}-topic-admin",
        )
        producer = KafkaProducerWrapper(
            settings.KAFKA_BOOTSTRAP_SERVERS,
            client_id=f"{SERVICE_NAME}-producer",
        )
        app.state.publisher = EventPublisher(topic="notification-events", producer=producer)
        app.state.consumer = NotificationKafkaConsumer(
            settings.KAFKA_BOOTSTRAP_SERVERS,
            get_session_factory(settings),
            push_client=app.state.push_client,
        )
        await app.state.consumer.start()
    yield
    if app.state.consumer:
        await app.state.consumer.stop()
    if app.state.publisher:
        await app.state.publisher.close()


def create_app() -> FastAPI:
    app = FastAPI(
        title="SafarPay Notification Service",
        version="1.0.0",
        lifespan=lifespan,
    )
    app.add_middleware(ObservabilityMiddleware, service_name=SERVICE_NAME)
    app.include_router(router, prefix="/api/v1/notification")
    app.include_router(router, prefix="/api/v1")

    @app.get("/health", tags=["ops"])
    async def health():
        return {"status": "ok", "service": SERVICE_NAME}

    @app.get("/metrics", tags=["ops"])
    async def metrics(request: Request):
        return PlainTextResponse(request.app.state.metrics.expose_prometheus())

    return app


app = create_app()
