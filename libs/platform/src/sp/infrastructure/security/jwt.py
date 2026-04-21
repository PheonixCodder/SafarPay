"""JWT creation and verification with typed TokenPayload.

Uses PyJWT (pyjwt) — actively maintained replacement for python-jose.
Returns a typed TokenPayload instead of Dict[str, Any] to prevent KeyError at runtime.
"""
from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone
from uuid import UUID

import jwt
from pydantic import BaseModel

logger = logging.getLogger("platform.security.jwt")


class TokenPayload(BaseModel):
    """Typed JWT payload — eliminates Dict[str, Any] runtime KeyError risks."""

    user_id: UUID
    email: str
    role: str
    exp: datetime
    iat: datetime


def create_access_token(
    user_id: UUID,
    email: str,
    role: str,
    secret: str,
    algorithm: str = "HS256",
    expiration_hours: int = 24,
) -> str:
    """Create a signed JWT access token."""
    now = datetime.now(timezone.utc)
    payload = {
        "user_id": str(user_id),
        "email": email,
        "role": role,
        "iat": now,
        "exp": now + timedelta(hours=expiration_hours),
    }
    return jwt.encode(payload, secret, algorithm=algorithm)


def verify_token(
    token: str,
    secret: str,
    algorithm: str = "HS256",
) -> TokenPayload | None:
    """Verify JWT signature and expiry. Returns typed payload or None on failure.

    Never raises — callers decide how to handle invalid tokens.
    """
    try:
        raw = jwt.decode(token, secret, algorithms=[algorithm])
        return TokenPayload(
            user_id=UUID(raw["user_id"]),
            email=raw["email"],
            role=raw["role"],
            exp=datetime.fromtimestamp(raw["exp"], tz=timezone.utc),
            iat=datetime.fromtimestamp(raw["iat"], tz=timezone.utc),
        )
    except (jwt.InvalidTokenError, KeyError, ValueError) as exc:
        logger.debug("Token verification failed: %s", exc)
        return None
