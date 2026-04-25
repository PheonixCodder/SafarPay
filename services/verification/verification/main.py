"""Verification service entry point."""
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
import asyncio
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sp.infrastructure.db.engine import get_db_engine
from sp.infrastructure.db.session import get_async_session
from sp.infrastructure.messaging.kafka import KafkaProducerWrapper, KafkaConsumerWrapper
from sp.infrastructure.messaging.publisher import EventPublisher
from sp.infrastructure.messaging.subscriber import EventSubscriber

from .api.router import router
from .application.services.identity_verification_engine import IdentityVerificationEngine
from .application.use_cases import VerificationUseCases
from .infrastructure.repositories import (
    DriverRepository, VehicleRepository, DocumentRepository, 
    DriverVehicleRepository, VerificationRejectionRepository
)
from .infrastructure.storage import S3StorageProvider
from .application.services.rejection_resolver import RejectionResolver

SERVICE_NAME = "verification"


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    settings = get_settings()
    setup_logging(SERVICE_NAME, level=settings.LOG_LEVEL, log_format=settings.LOG_FORMAT)
    app.state.db_engine = get_db_engine(settings.POSTGRES_DB_URI, settings.POSTGRES_POOL_SIZE)
    cache = get_cache_manager_factory(settings)
    await cache.connect()
    app.state.cache = cache
    app.state.metrics = MetricsCollector(SERVICE_NAME)

    # ML Engine
    app.state.identity_engine = IdentityVerificationEngine(metrics_collector=app.state.metrics)

    # Messaging
    producer = KafkaProducerWrapper(settings.KAFKA_BOOTSTRAP_SERVERS)
    app.state.publisher = EventPublisher("verification.events", producer)

    consumer = KafkaConsumerWrapper(
        settings.KAFKA_BOOTSTRAP_SERVERS, 
        group_id="verification-service",
        topics=["auth.events", "verification.events"]
    )
    
    subscriber = EventSubscriber(consumer)
    
    async def review_handler(event):
        driver_id_str = event.payload.get("driver_id")
        if not driver_id_str: return
        driver_id = uuid.UUID(driver_id_str)
        
        # Correctly manage session lifecycle in background task
        async with AsyncSession(app.state.db_engine, expire_on_commit=False) as session:
            try:
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
                    event_publisher=app.state.publisher,
                    rejection_repo=rejection_repo,
                    cache_manager=app.state.cache,
                )
                await use_cases.execute_verification_review(driver_id)
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            
    subscriber.register("verification.review_requested", review_handler)
    app.state.subscriber_task = asyncio.create_task(subscriber.start())

    yield
    
    app.state.subscriber_task.cancel()
    await subscriber.stop()
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
