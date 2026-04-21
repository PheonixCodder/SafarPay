"""Geospatial service entry point."""
from __future__ import annotations

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse
from sp.core.config import get_settings
from sp.core.observability.logging import setup_logging
from sp.core.observability.metrics import MetricsCollector
from sp.core.observability.middleware import ObservabilityMiddleware
from sp.infrastructure.db.engine import get_db_engine

from .api.router import router

SERVICE_NAME = "geospatial"


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    settings = get_settings()
    setup_logging(SERVICE_NAME, level=settings.LOG_LEVEL, log_format=settings.LOG_FORMAT)
    app.state.db_engine = get_db_engine(settings.POSTGRES_DB_URI, settings.POSTGRES_POOL_SIZE)
    app.state.metrics = MetricsCollector(SERVICE_NAME)
    yield
    await app.state.db_engine.dispose()


def create_app() -> FastAPI:
    app = FastAPI(
        title="SafarPay Geospatial Service",
        version="1.0.0",
        description="PostGIS-backed place management and radius search.",
        lifespan=lifespan,
    )
    app.add_middleware(ObservabilityMiddleware, service_name=SERVICE_NAME)
    app.include_router(router, prefix="/api/v1/geospatial")

    @app.get("/health", tags=["ops"])
    async def health():
        return {"status": "ok", "service": SERVICE_NAME}

    @app.get("/metrics", tags=["ops"])
    async def metrics(request: Request):
        return PlainTextResponse(request.app.state.metrics.expose_prometheus())

    return app


app = create_app()
