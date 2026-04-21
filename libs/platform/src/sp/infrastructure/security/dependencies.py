"""FastAPI dependency providers for authentication.

IMPORTANT: Tokens are ALWAYS extracted from the Authorization: Bearer <token> header.
           Never from query parameters — bearer tokens in URLs leak to logs and proxies.
"""
from __future__ import annotations

from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from sp.core.config import Settings, get_settings

from .jwt import TokenPayload, verify_token

# auto_error=False so we can return None for optional auth instead of raising
_security = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: Annotated[
        HTTPAuthorizationCredentials | None, Depends(_security)
    ],
    settings: Annotated[Settings, Depends(get_settings)],
) -> TokenPayload:
    """Extract and verify the Bearer token from the Authorization header.

    Raises HTTP 401 if:
    - No Authorization header present
    - Token is invalid, expired, or malformed
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    payload = verify_token(
        credentials.credentials,
        settings.JWT_SECRET,
        settings.JWT_ALGORITHM,
    )
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return payload


async def get_optional_user(
    credentials: Annotated[
        HTTPAuthorizationCredentials | None, Depends(_security)
    ],
    settings: Annotated[Settings, Depends(get_settings)],
) -> TokenPayload | None:
    """Like get_current_user but returns None if no auth provided."""
    if not credentials:
        return None
    return verify_token(
        credentials.credentials,
        settings.JWT_SECRET,
        settings.JWT_ALGORITHM,
    )


# Convenience type aliases for route signatures
CurrentUser = Annotated[TokenPayload, Depends(get_current_user)]
OptionalUser = Annotated[TokenPayload | None, Depends(get_optional_user)]
