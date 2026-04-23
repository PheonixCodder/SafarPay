"""JWT creation and verification with typed TokenPayload.

Uses PyJWT (pyjwt) — actively maintained replacement for python-jose.
Returns a typed TokenPayload instead of Dict[str, Any] to prevent KeyError at runtime.
"""
from __future__ import annotations

import logging
import secrets
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
    session_id: UUID  # links token to a Session row for revocation checks
    exp: datetime
    iat: datetime


def create_access_token(
    user_id: UUID,
    email: str,
    role: str,
    session_id: UUID,
    secret: str,
    algorithm: str = "HS256",
    expiration_minutes: int = 15,
) -> str:
    """Create a signed JWT access token (short-lived)."""
    now = datetime.now(timezone.utc)
    payload = {
        "user_id": str(user_id),
        "email": email,
        "role": role,
        "session_id": str(session_id),
        "iat": now,
        "exp": now + timedelta(minutes=expiration_minutes),
    }
    return jwt.encode(payload, secret, algorithm=algorithm)


def create_tokens(
    user_id: UUID,
    email: str,
    role: str,
    session_id: UUID,
    secret: str,
    algorithm: str = "HS256",
    access_ttl_minutes: int = 15,
) -> dict:
    """Create an access + refresh token pair.

    Returns:
        dict with access_token, refresh_token, and expires_in (seconds).
    """
    access_token = create_access_token(
        user_id=user_id,
        email=email or "",
        role=role,
        session_id=session_id,
        secret=secret,
        algorithm=algorithm,
        expiration_minutes=access_ttl_minutes,
    )
    # 48 bytes → 64-char URL-safe string, 384-bit entropy
    refresh_token = secrets.token_urlsafe(48)
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "expires_in": access_ttl_minutes * 60,
    }


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
            session_id=UUID(raw["session_id"]),
            exp=datetime.fromtimestamp(raw["exp"], tz=timezone.utc),
            iat=datetime.fromtimestamp(raw["iat"], tz=timezone.utc),
        )
    except (jwt.InvalidTokenError, KeyError, ValueError) as exc:
        logger.debug("Token verification failed: %s", exc)
        return None


# ── Verification tokens (proof-of-phone, short-lived) ────────────────────────


def create_verification_token(
    phone: str,
    secret: str,
    algorithm: str = "HS256",
    expiration_minutes: int = 10,
) -> str:
    """Create a short-lived JWT proving phone ownership.

    Used between /otp/verify → /register or /google/link-phone.
    Contains only the phone claim — no user identity.
    """
    now = datetime.now(timezone.utc)
    payload = {
        "phone": phone,
        "purpose": "phone_verification",
        "iat": now,
        "exp": now + timedelta(minutes=expiration_minutes),
    }
    return jwt.encode(payload, secret, algorithm=algorithm)


def verify_verification_token(
    token: str,
    secret: str,
    algorithm: str = "HS256",
) -> str | None:
    """Decode a verification token. Returns the phone number or None."""
    try:
        raw = jwt.decode(token, secret, algorithms=[algorithm])
        if raw.get("purpose") != "phone_verification":
            return None
        return raw["phone"]
    except (jwt.InvalidTokenError, KeyError, ValueError) as exc:
        logger.debug("Verification token failed: %s", exc)
        return None
