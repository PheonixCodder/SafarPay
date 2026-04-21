"""Gateway use cases — rate limiting and request proxying."""
from __future__ import annotations

import asyncio
import logging

import httpx
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from sp.infrastructure.cache.manager import CacheManager
from sp.infrastructure.security.jwt import TokenPayload

from .models import UpstreamService

logger = logging.getLogger("gateway.use_cases")

RATE_LIMIT_MAX = 100       # requests per window
RATE_LIMIT_WINDOW_S = 60   # window size in seconds


class CheckRateLimitUseCase:
    """Distributed rate limiting using atomic Redis INCR.

    Uses a sliding window keyed by client_ip + minute-bucket.
    Atomic INCR with TTL is safe for concurrent requests across multiple
    gateway instances — no in-memory dict, no race conditions.
    """

    def __init__(self, cache: CacheManager) -> None:
        self._cache = cache

    async def execute(self, client_ip: str) -> bool:
        """Returns True if the request is allowed, False if rate-limited."""
        import time
        bucket = int(time.time() / RATE_LIMIT_WINDOW_S)
        key = f"{client_ip}:{bucket}"
        count = await self._cache.increment("ratelimit", key, ttl=RATE_LIMIT_WINDOW_S)
        return count <= RATE_LIMIT_MAX


class ProxyRequestUseCase:
    """Forward HTTP requests to upstream services with retry and header propagation."""

    def __init__(
        self,
        http_client: httpx.AsyncClient,
        upstream_registry: dict[str, UpstreamService],
    ) -> None:
        self._client = http_client
        self._registry = upstream_registry

    async def execute(
        self,
        service_name: str,
        path: str,
        request: Request,
        user: TokenPayload | None,
    ) -> Response:
        upstream = self._registry.get(service_name)
        if not upstream:
            return JSONResponse(
                {"detail": f"Unknown service: '{service_name}'"}, status_code=404
            )

        target_url = f"{upstream.url}/{path}"
        if request.url.query:
            target_url = f"{target_url}?{request.url.query}"

        # Build forwarded headers — propagate auth + tracing
        forward_headers = {
            k: v
            for k, v in request.headers.items()
            if k.lower()
            not in ("host", "content-length", "transfer-encoding", "connection")
        }
        if user:
            forward_headers["X-User-ID"] = str(user.user_id)
            forward_headers["X-User-Role"] = user.role
            forward_headers["X-User-Email"] = user.email

        body = await request.body()

        for attempt in range(1, upstream.max_retries + 2):
            try:
                upstream_resp = await self._client.request(
                    method=request.method,
                    url=target_url,
                    headers=forward_headers,
                    content=body,
                    timeout=upstream.timeout_seconds,
                )
                return Response(
                    content=upstream_resp.content,
                    status_code=upstream_resp.status_code,
                    headers=dict(upstream_resp.headers),
                    media_type=upstream_resp.headers.get("content-type"),
                )
            except (httpx.TimeoutException, httpx.ConnectError) as exc:
                if attempt <= upstream.max_retries:
                    wait = 2 ** (attempt - 1)
                    logger.warning(
                        "Upstream %s unreachable (attempt %d/%d), retrying in %ds: %s",
                        service_name,
                        attempt,
                        upstream.max_retries + 1,
                        wait,
                        exc,
                    )
                    await asyncio.sleep(wait)
                else:
                    logger.error("Upstream %s failed after retries: %s", service_name, exc)
                    return JSONResponse(
                        {"detail": f"Upstream service '{service_name}' is unavailable"},
                        status_code=503,
                    )
        # Should not reach here
        return JSONResponse({"detail": "Proxy error"}, status_code=502)
