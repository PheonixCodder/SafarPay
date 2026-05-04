"""FastAPI dependency providers for authentication.

IMPORTANT: Tokens are ALWAYS extracted from the Authorization: Bearer <token> header.
           Never from query parameters — bearer tokens in URLs leak to logs and proxies.
"""
from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException, status, WebSocket
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from sp.core.config import Settings, get_settings
from sp.infrastructure.db.session import get_async_session
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from .jwt import TokenPayload, verify_token

# auto_error=False so we can return None for optional auth instead of raising
_security = HTTPBearer(auto_error=False)

async def get_current_user_ws(
    websocket: WebSocket,
    settings: Annotated[Settings, Depends(get_settings)],
) -> TokenPayload:

    token = websocket.query_params.get("token")

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="WebSocket token required"
        )

    payload = verify_token(
        token,
        settings.JWT_SECRET,
        settings.JWT_ALGORITHM,
    )

    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )

    return payload

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


# ---------------------------------------------------------------------------
# Driver identity helper
# ---------------------------------------------------------------------------

async def get_current_driver(
    current_user: Annotated[TokenPayload, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_async_session)],
) -> UUID:
    """Resolve the authenticated user's driver_id from verification.drivers.

    Chains off get_current_user so the JWT is always verified first.
    Raises HTTP 403 when the user has no driver profile, ensuring driver-scoped
    routes cannot be called by plain passengers or unregistered users.
    """
    result = await session.execute(
        text("SELECT id FROM verification.drivers WHERE user_id = :uid LIMIT 1"),
        {"uid": current_user.user_id},
    )
    row = result.fetchone()
    if row is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Caller has no driver profile — driver account required.",
        )
    return row[0]  # type: ignore[return-value]
    

async def get_current_driver_ws(
    current_user: Annotated[
        TokenPayload,
        Depends(get_current_user_ws)
    ],
    session: Annotated[
        AsyncSession,
        Depends(get_async_session)
    ],
) -> UUID:

    result = await session.execute(
        text("""
            SELECT id
            FROM verification.drivers
            WHERE user_id = :uid
            LIMIT 1
        """),
        {"uid": current_user.user_id},
    )

    row = result.fetchone()

    if row is None:
        raise HTTPException(
            status_code=403,
            detail="Driver account required"
        )

    return row[0]


# Convenience alias — mirrors the CurrentUser pattern from sp.infrastructure.security
CurrentDriver = Annotated[UUID, Depends(get_current_driver)]


async def get_optional_driver_id(
    current_user: Annotated[TokenPayload, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_async_session)],
) -> UUID | None:
    """Return the driver_id for the authenticated user, or None if they have no driver profile.

    Used by proof endpoints that can be called by either a passenger or the assigned
    driver: the caller's driver_id (not their auth user_id) must be compared against
    ride.assigned_driver_id / proof.uploaded_by_driver_id which stores the driver UUID
    from verification.drivers.id.  When the caller is a passenger this returns None and
    the passenger-path check uses current_user.user_id instead.
    """
    result = await session.execute(
        text("SELECT id FROM verification.drivers WHERE user_id = :uid LIMIT 1"),
        {"uid": current_user.user_id},
    )
    row = result.fetchone()
    return row[0] if row else None  # type: ignore[return-value]


# Annotated alias for optional-driver injection
OptionalDriverId = Annotated[UUID | None, Depends(get_optional_driver_id)]