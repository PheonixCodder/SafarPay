"""Verification service entry point."""
from __future__ import annotations

import asyncio
import uuid
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
from sp.infrastructure.messaging.inbox import process_inbox_message
from sp.infrastructure.messaging.kafka import KafkaConsumerWrapper, KafkaProducerWrapper
from sp.infrastructure.messaging.outbox import GenericOutboxWorker
from sp.infrastructure.messaging.publisher import EventPublisher
from sp.infrastructure.messaging.subscriber import EventSubscriber

from .api.router import router
from .application.services.identity_verification_engine import IdentityVerificationEngine
from .application.services.rejection_resolver import RejectionResolver
from .application.use_cases import VerificationUseCases
from .infrastructure.orm_models import VerificationInboxMessageORM, VerificationOutboxEventORM
from .infrastructure.outbox_publisher import VerificationOutboxPublisher
from .infrastructure.repositories import (
    DocumentRepository,
    DriverRepository,
    DriverVehicleRepository,
    VehicleRepository,
    VerificationRejectionRepository,
)
from .infrastructure.storage import S3StorageProvider

SERVICE_NAME = "verification"


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    settings = get_settings()
    setup_logging(SERVICE_NAME, level=settings.LOG_LEVEL, log_format=settings.LOG_FORMAT)
    app.state.db_engine = get_db_engine(settings.POSTGRES_DB_URI, settings.POSTGRES_POOL_SIZE)
    # Avoid lru_cache unhashable Settings error by creating the factory once
    app.state.session_factory = get_session_factory(settings)

    app.state.cache = get_cache_manager_factory(settings)
    await app.state.cache.connect()
    app.state.metrics = MetricsCollector(SERVICE_NAME)

    # ML Engine
    app.state.identity_engine = IdentityVerificationEngine(metrics_collector=app.state.metrics)

    # Messaging
    if settings.KAFKA_BOOTSTRAP_SERVERS:
        producer = KafkaProducerWrapper(settings.KAFKA_BOOTSTRAP_SERVERS)
        app.state.publisher = EventPublisher(settings.VERIFICATION_EVENTS_TOPIC, producer)
        app.state.outbox_worker = GenericOutboxWorker(
            app.state.session_factory,
            app.state.publisher,
            VerificationOutboxEventORM,
            default_topic=settings.VERIFICATION_EVENTS_TOPIC,
        )
        await app.state.outbox_worker.start()

        consumer = KafkaConsumerWrapper(
            settings.KAFKA_BOOTSTRAP_SERVERS,
            group_id=settings.VERIFICATION_CONSUMER_GROUP,
            topics=[
                settings.AUTH_EVENTS_TOPIC,
                settings.AUTH_EVENTS_LEGACY_TOPIC,
                settings.VERIFICATION_EVENTS_TOPIC,
            ],
        )

        subscriber = EventSubscriber(consumer)

        async def review_handler(event):
            driver_id_str = event.payload.get("driver_id")
            if not driver_id_str:
                return
            driver_id = uuid.UUID(driver_id_str)

            factory = app.state.session_factory
            # Correctly manage session lifecycle in background task
            async with factory() as session:
                try:
                    async def handle() -> None:
                        driver_repo = DriverRepository(session)
                        rejection_repo = VerificationRejectionRepository(session)
                        use_cases = VerificationUseCases(
                            driver_repo=driver_repo,
                            vehicle_repo=VehicleRepository(session),
                            document_repo=DocumentRepository(session),
                            driver_vehicle_repo=DriverVehicleRepository(session),
                            storage_provider=S3StorageProvider(),
                            rejection_resolver=RejectionResolver(rejection_repo),
                            identity_engine=app.state.identity_engine,
                            event_publisher=VerificationOutboxPublisher(session),
                            rejection_repo=rejection_repo,
                            cache_manager=app.state.cache,
                        )
                        await use_cases.execute_verification_review(driver_id)

                    raw_msg = {
                        "topic": settings.VERIFICATION_EVENTS_TOPIC,
                        "value": event.model_dump(mode="json"),
                    }
                    await process_inbox_message(session, VerificationInboxMessageORM, raw_msg, handle)
                    await session.commit()
                except Exception:
                    await session.rollback()
                    raise

        subscriber.register("verification.review_requested", review_handler)
        app.state.subscriber_task = asyncio.create_task(subscriber.start())

    yield

    if settings.KAFKA_BOOTSTRAP_SERVERS:
        app.state.subscriber_task.cancel()
        with suppress(asyncio.CancelledError):
            await app.state.subscriber_task
        await subscriber.stop()
        await app.state.outbox_worker.stop()
    if settings.KAFKA_BOOTSTRAP_SERVERS:
        await app.state.publisher.close()
    await app.state.cache.close()
    await app.state.db_engine.dispose()


def create_app() -> FastAPI:
    app = FastAPI(title="SafarPay Verification Service", version="1.0.0", lifespan=lifespan)
    app.add_middleware(ObservabilityMiddleware, service_name=SERVICE_NAME)
    app.include_router(router, prefix="/api")

    @app.get("/health", tags=["ops"])
    async def health():
        return {"status": "ok", "service": SERVICE_NAME}

    @app.get("/metrics", tags=["ops"])
    async def metrics(request: Request):
        return PlainTextResponse(request.app.state.metrics.expose_prometheus())

    return app


app = create_app()
