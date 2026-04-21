"""Auth service entry point.

Lifespan manages all resource lifecycle (DB engine, Redis, Kafka producer).
ObservabilityMiddleware is automatically active for every request.
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
from sp.infrastructure.messaging.kafka import KafkaProducerWrapper
from sp.infrastructure.messaging.publisher import EventPublisher

from .api.router import router

SERVICE_NAME = "auth"


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    settings = get_settings()
    setup_logging(SERVICE_NAME, level=settings.LOG_LEVEL, log_format=settings.LOG_FORMAT)

    # DB — cached engine, shared connection pool
    app.state.db_engine = get_db_engine(
        settings.POSTGRES_DB_URI, settings.POSTGRES_POOL_SIZE
    )

    # Cache — lifespan-managed Redis pool
    cache = get_cache_manager_factory(settings)
    await cache.connect()
    app.state.cache = cache

    # Metrics collector
    app.state.metrics = MetricsCollector(SERVICE_NAME)

    # Messaging — optional (Kafka may not run in dev)
    app.state.publisher = None
    if settings.KAFKA_BOOTSTRAP_SERVERS:
        producer = KafkaProducerWrapper(
            settings.KAFKA_BOOTSTRAP_SERVERS,
            client_id=f"{SERVICE_NAME}-producer",
        )
        app.state.publisher = EventPublisher(topic="auth-events", producer=producer)

    yield  # ← service runs here

    # Shutdown — clean resource teardown
    await app.state.cache.close()
    await app.state.db_engine.dispose()
    if app.state.publisher:
        await app.state.publisher.close()


def create_app() -> FastAPI:
    app = FastAPI(
        title="SafarPay Auth Service",
        version="1.0.0",
        description="Authentication, registration, and JWT token issuance.",
        lifespan=lifespan,
    )

    app.add_middleware(ObservabilityMiddleware, service_name=SERVICE_NAME)
    app.include_router(router, prefix="/api/v1/auth")

    @app.get("/health", tags=["ops"])
    async def health():
        return {"status": "ok", "service": SERVICE_NAME}

    @app.get("/metrics", tags=["ops"])
    async def metrics(request: Request):
        return PlainTextResponse(request.app.state.metrics.expose_prometheus())

    return app


app = create_app()
