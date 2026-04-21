"""Gateway API router — catch-all proxy with auth, rate limiting, header propagation."""
from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Request, Response
from sp.core.observability.logging import get_logger
from sp.infrastructure.security.dependencies import get_optional_user
from sp.infrastructure.security.jwt import TokenPayload

from ..application.use_cases import ProxyRequestUseCase
from ..infrastructure.dependencies import enforce_rate_limit, get_proxy_use_case

router = APIRouter(tags=["proxy"])
logger = get_logger("gateway.api")


@router.api_route(
    "/{service}/{path:path}",
    methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    summary="Proxy request to the appropriate upstream service",
    dependencies=[Depends(enforce_rate_limit)],
)
async def proxy(
    service: str,
    path: str,
    request: Request,
    proxy_uc: Annotated[ProxyRequestUseCase, Depends(get_proxy_use_case)],
    user: Annotated[TokenPayload | None, Depends(get_optional_user)],
) -> Response:
    """Route any request to its upstream service.

    - Enforces rate limiting (dependencies=[Depends(enforce_rate_limit)])
    - Optionally authenticates via Bearer token (auth is not required at gateway level)
    - Propagates X-User-ID, X-User-Role, X-User-Email headers to upstream
    - Retries on transient failures, returns 503 if upstream is down
    """
    if user:
        logger.info(
            "Proxy request",
            extra={"service": service, "path": path, "user_id": str(user.user_id)},
        )
    else:
        logger.info("Proxy request (unauthenticated)", extra={"service": service, "path": path})

    return await proxy_uc.execute(service, path, request, user)
