"""Gateway service entry point."""
from __future__ import annotations

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse
from sp.core.config import get_settings
from sp.core.observability.logging import setup_logging
from sp.core.observability.metrics import MetricsCollector
from sp.core.observability.middleware import ObservabilityMiddleware
from sp.infrastructure.cache.manager import get_cache_manager_factory

from .api.router import router
from .domain.models import build_upstream_registry

SERVICE_NAME = "gateway"


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    settings = get_settings()
    setup_logging(SERVICE_NAME, level=settings.LOG_LEVEL, log_format=settings.LOG_FORMAT)

    # Cache — for rate limiting
    cache = get_cache_manager_factory(settings)
    await cache.connect()
    app.state.cache = cache

    # Shared httpx client — connection pooled, reused across all requests
    app.state.http_client = httpx.AsyncClient(
        limits=httpx.Limits(max_connections=200, max_keepalive_connections=50),
        timeout=httpx.Timeout(30.0, connect=5.0),
        follow_redirects=False,
    )

    # Upstream service registry — built from settings
    app.state.upstream_registry = build_upstream_registry(settings)
    app.state.metrics = MetricsCollector(SERVICE_NAME)

    yield

    await app.state.cache.close()
    await app.state.http_client.aclose()


def create_app() -> FastAPI:
    app = FastAPI(
        title="SafarPay API Gateway",
        version="1.0.0",
        description="Single entry point — rate limiting, auth propagation, and reverse proxy.",
        lifespan=lifespan,
    )

    app.add_middleware(ObservabilityMiddleware, service_name=SERVICE_NAME)
    app.include_router(router)

    @app.get("/health", tags=["ops"])
    async def health():
        return {"status": "ok", "service": SERVICE_NAME}

    @app.get("/metrics", tags=["ops"])
    async def metrics(request: Request):
        return PlainTextResponse(request.app.state.metrics.expose_prometheus())

    return app


app = create_app()
