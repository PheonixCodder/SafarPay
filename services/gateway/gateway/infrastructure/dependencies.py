"""Gateway infrastructure DI providers."""
from __future__ import annotations

from typing import Annotated

import httpx
from fastapi import Depends, HTTPException, Request, status
from sp.infrastructure.cache.manager import CacheManager

from ..application.use_cases import CheckRateLimitUseCase, ProxyRequestUseCase
from ..domain.models import UpstreamService


def get_cache(request: Request) -> CacheManager:
    return request.app.state.cache


def get_http_client(request: Request) -> httpx.AsyncClient:
    return request.app.state.http_client


def get_upstream_registry(request: Request) -> dict[str, UpstreamService]:
    return request.app.state.upstream_registry


def get_rate_limit_use_case(
    cache: Annotated[CacheManager, Depends(get_cache)],
) -> CheckRateLimitUseCase:
    return CheckRateLimitUseCase(cache)


def get_proxy_use_case(
    http_client: Annotated[httpx.AsyncClient, Depends(get_http_client)],
    registry: Annotated[dict[str, UpstreamService], Depends(get_upstream_registry)],
) -> ProxyRequestUseCase:
    return ProxyRequestUseCase(http_client, registry)


async def enforce_rate_limit(
    request: Request,
    rate_limit_uc: Annotated[CheckRateLimitUseCase, Depends(get_rate_limit_use_case)],
) -> None:
    """Dependency that raises 429 if the client is rate-limited."""
    client_ip = request.client.host if request.client else "unknown"
    allowed = await rate_limit_uc.execute(client_ip)
    if not allowed:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Try again in 60 seconds.",
        )
