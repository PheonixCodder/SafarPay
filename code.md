# Project Structure

```
├── libs
│   └── platform
│       ├── src
│       │   └── sp
│       │       ├── __pycache__
│       │       ├── core
│       │       │   ├── __pycache__
│       │       │   ├── observability
│       │       │   ├── __init__.py
│       │       │   └── config.py
│       │       ├── infrastructure
│       │       │   ├── __pycache__
│       │       │   ├── cache
│       │       │   ├── db
│       │       │   ├── messaging
│       │       │   ├── security
│       │       │   └── __init__.py
│       │       └── __init__.py
│       └── pyproject.toml
├── migrations
│   ├── versions
│   │   └── __init__.py
│   ├── alembic.ini
│   └── env.py
├── scripts
│   └── init-schemas.sql
├── services
│   ├── auth
│   │   ├── auth
│   │   │   ├── __pycache__
│   │   │   ├── api
│   │   │   │   ├── __pycache__
│   │   │   │   ├── __init__.py
│   │   │   │   └── router.py
│   │   │   ├── application
│   │   │   │   ├── __pycache__
│   │   │   │   ├── __init__.py
│   │   │   │   ├── schemas.py
│   │   │   │   └── use_cases.py
│   │   │   ├── domain
│   │   │   │   ├── __pycache__
│   │   │   │   ├── __init__.py
│   │   │   │   ├── exceptions.py
│   │   │   │   ├── interfaces.py
│   │   │   │   └── models.py
│   │   │   ├── infrastructure
│   │   │   │   ├── __pycache__
│   │   │   │   ├── messaging
│   │   │   │   │   ├── __pycache__
│   │   │   │   │   └── whatsapp.py
│   │   │   │   ├── security
│   │   │   │   │   ├── __pycache__
│   │   │   │   │   ├── google_oauth.py
│   │   │   │   │   └── rate_limit.py
│   │   │   │   ├── __init__.py
│   │   │   │   ├── dependencies.py
│   │   │   │   ├── orm_models.py
│   │   │   │   └── repositories.py
│   │   │   ├── __init__.py
│   │   │   └── main.py
│   │   └── pyproject.toml
│   ├── bidding
│   │   ├── bidding
│   │   │   ├── __pycache__
│   │   │   ├── api
│   │   │   │   ├── __init__.py
│   │   │   │   └── router.py
│   │   │   ├── application
│   │   │   │   ├── __pycache__
│   │   │   │   ├── __init__.py
│   │   │   │   ├── schemas.py
│   │   │   │   └── use_cases.py
│   │   │   ├── domain
│   │   │   │   ├── __pycache__
│   │   │   │   ├── __init__.py
│   │   │   │   ├── exceptions.py
│   │   │   │   ├── interfaces.py
│   │   │   │   └── models.py
│   │   │   ├── infrastructure
│   │   │   │   ├── __init__.py
│   │   │   │   ├── dependencies.py
│   │   │   │   ├── orm_models.py
│   │   │   │   └── repositories.py
│   │   │   ├── __init__.py
│   │   │   └── main.py
│   │   └── pyproject.toml
│   ├── gateway
│   │   ├── gateway
│   │   │   ├── __pycache__
│   │   │   ├── api
│   │   │   │   ├── __init__.py
│   │   │   │   └── router.py
│   │   │   ├── application
│   │   │   │   ├── __init__.py
│   │   │   │   └── use_cases.py
│   │   │   ├── domain
│   │   │   │   ├── __pycache__
│   │   │   │   ├── __init__.py
│   │   │   │   └── models.py
│   │   │   ├── infrastructure
│   │   │   │   ├── __init__.py
│   │   │   │   └── dependencies.py
│   │   │   ├── __init__.py
│   │   │   └── main.py
│   │   └── pyproject.toml
│   ├── geospatial
│   │   ├── geospatial
│   │   │   ├── __pycache__
│   │   │   ├── api
│   │   │   │   ├── __init__.py
│   │   │   │   └── router.py
│   │   │   ├── application
│   │   │   │   ├── __init__.py
│   │   │   │   ├── schemas.py
│   │   │   │   └── use_cases.py
│   │   │   ├── domain
│   │   │   │   ├── __pycache__
│   │   │   │   ├── __init__.py
│   │   │   │   └── models.py
│   │   │   ├── infrastructure
│   │   │   │   ├── __init__.py
│   │   │   │   ├── dependencies.py
│   │   │   │   ├── orm_models.py
│   │   │   │   └── repositories.py
│   │   │   ├── __init__.py
│   │   │   └── main.py
│   │   └── pyproject.toml
│   ├── location
│   │   ├── location
│   │   │   ├── __pycache__
│   │   │   ├── api
│   │   │   │   ├── __init__.py
│   │   │   │   └── router.py
│   │   │   ├── application
│   │   │   │   ├── __init__.py
│   │   │   │   ├── schemas.py
│   │   │   │   └── use_cases.py
│   │   │   ├── domain
│   │   │   │   ├── __pycache__
│   │   │   │   ├── __init__.py
│   │   │   │   └── models.py
│   │   │   ├── infrastructure
│   │   │   │   ├── __init__.py
│   │   │   │   └── dependencies.py
│   │   │   ├── __init__.py
│   │   │   └── main.py
│   │   └── pyproject.toml
│   ├── notification
│   │   ├── notification
│   │   │   ├── __pycache__
│   │   │   ├── api
│   │   │   │   ├── __init__.py
│   │   │   │   └── router.py
│   │   │   ├── application
│   │   │   │   ├── __init__.py
│   │   │   │   ├── schemas.py
│   │   │   │   └── use_cases.py
│   │   │   ├── domain
│   │   │   │   ├── __pycache__
│   │   │   │   ├── __init__.py
│   │   │   │   └── models.py
│   │   │   ├── infrastructure
│   │   │   │   ├── __init__.py
│   │   │   │   └── dependencies.py
│   │   │   ├── __init__.py
│   │   │   └── main.py
│   │   └── pyproject.toml
│   └── verification
│       ├── verification
│       │   ├── __pycache__
│       │   ├── api
│       │   │   ├── __init__.py
│       │   │   └── router.py
│       │   ├── application
│       │   │   ├── __init__.py
│       │   │   ├── schemas.py
│       │   │   └── use_cases.py
│       │   ├── domain
│       │   │   ├── __pycache__
│       │   │   ├── __init__.py
│       │   │   ├── exceptions.py
│       │   │   └── models.py
│       │   ├── infrastructure
│       │   │   ├── __init__.py
│       │   │   ├── dependencies.py
│       │   │   ├── orm_models.py
│       │   │   └── repositories.py
│       │   ├── __init__.py
│       │   └── main.py
│       └── pyproject.toml
├── architecture_audit_report.md
├── code.md
├── docker-compose.yml
├── Dockerfile
├── Dockerfile.migrate
├── main.py
├── pyproject.toml
├── README.md
├── Refactoring SafarPay Microservices Architecture.md
├── Tech Stack.txt
└── uv.lock
```

What is the flow:
Path A (Phone-first): /otp/send → /otp/verify → /register → verified rider
Path B (Google-first): /google/verify-token → /otp/send → /otp/verify → /google/link-phone → verified rider (with automatic account merge if phone conflicts)
WhatsApp: Authentication template with COPY_CODE button
Google: Mobile SDK id_token offline verification (no authlib, uses google-auth)
Rate limiting: 3 OTP sends/phone/15min, 10 verifies/IP/15min via Redis

# File Contents

## libs\platform\src\sp\infrastructure\security\dependencies.py

```python
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

```

## libs\platform\src\sp\infrastructure\security\jwt.py

```python
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

```

## libs\platform\src\sp\infrastructure\security\permissions.py

```python
"""Role-based permission system.

Usage:
    @router.get("/admin-only")
    async def admin_route(user = Depends(require_role(Permission.ADMIN))):
        ...
"""
from __future__ import annotations

from enum import Enum
from typing import Annotated

from fastapi import Depends, HTTPException, status

from .dependencies import get_current_user
from .jwt import TokenPayload


class Permission(str, Enum):
    PASSENGER = "passenger"
    DRIVER = "driver"
    ADMIN = "admin"


def require_role(*roles: Permission):
    """Dependency factory that enforces role-based access control.

    Returns the verified TokenPayload so callers can use it directly.
    Raises HTTP 403 if the authenticated user's role is not in the allowed list.
    """
    async def _check(
        user: Annotated[TokenPayload, Depends(get_current_user)]
    ) -> TokenPayload:
        if user.role not in [r.value for r in roles]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required roles: {[r.value for r in roles]}",
            )
        return user

    return _check

```

## libs\platform\src\sp\infrastructure\security\__init__.py

```python
"""Security — JWT, auth dependencies, permissions."""

from .dependencies import CurrentUser, OptionalUser, get_current_user, get_optional_user
from .jwt import (
    TokenPayload,
    create_access_token,
    create_tokens,
    create_verification_token,
    verify_token,
    verify_verification_token,
)
from .permissions import Permission, require_role

__all__ = [
    "TokenPayload",
    "create_access_token",
    "create_tokens",
    "create_verification_token",
    "verify_token",
    "verify_verification_token",
    "get_current_user",
    "get_optional_user",
    "CurrentUser",
    "OptionalUser",
    "Permission",
    "require_role",
]

```

## services\auth\auth\api\router.py

```python
"""Auth API router — thin controllers, domain exceptions mapped to HTTP responses.

Routes:
  POST /otp/send          — Send WhatsApp OTP
  POST /otp/verify        — Verify OTP → verification_token
  POST /register          — Create user from verification_token + profile (Path A)
  POST /google/verify-token — Verify Google id_token → tokens (Path B start)
  POST /google/link-phone — Link verified phone to Google user (Path B complete)
  POST /refresh           — Rotate tokens
  GET  /sessions          — List active sessions
  DELETE /sessions/{id}   — Revoke session
  POST /logout            — Logout
  GET  /me                — Profile
"""
from __future__ import annotations

import hashlib
import json
import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status

from sp.core.observability.logging import get_logger
from sp.infrastructure.security.dependencies import CurrentUser

from ..application.schemas import (
    GoogleTokenRequest,
    LinkPhoneRequest,
    OTPRequest,
    OTPVerifyRequest,
    OTPVerifyResponse,
    RegisterRequest,
    SessionResponse,
    TokenResponse,
    UserResponse,
)
from ..application.use_cases import (
    GoogleVerifyTokenUseCase,
    LinkPhoneUseCase,
    RefreshTokenUseCase,
    RegisterUseCase,
    SendOTPUseCase,
    VerifyOTPUseCase,
)
from ..domain.exceptions import (
    AuthDomainError,
    GoogleTokenError,
    InvalidSessionError,
    InvalidVerificationTokenError,
    OTPExpiredError,
    OTPInvalidError,
    OTPMaxAttemptsError,
    OTPRateLimitError,
    UserAlreadyExistsError,
)
from ..infrastructure.dependencies import (
    get_google_verify_use_case,
    get_link_phone_use_case,
    get_otp_rate_limiter,
    get_refresh_use_case,
    get_register_use_case,
    get_send_otp_use_case,
    get_session_repo,
    get_user_repo,
    get_verify_otp_use_case,
)
from ..infrastructure.repositories import SessionRepository, UserRepository
from ..infrastructure.security.rate_limit import OTPRateLimiter

router = APIRouter(tags=["auth"])
logger = get_logger("auth.api")


# ── Cookie helpers ────────────────────────────────────────────────────────────

_REFRESH_COOKIE_NAME = "refresh_token"
_REFRESH_COOKIE_MAX_AGE = 30 * 24 * 60 * 60  # 30 days


def _set_refresh_cookie(response: Response, refresh_token: str) -> None:
    response.set_cookie(
        key=_REFRESH_COOKIE_NAME,
        value=refresh_token,
        max_age=_REFRESH_COOKIE_MAX_AGE,
        httponly=True,
        secure=True,
        samesite="strict",
    )


def _clear_refresh_cookie(response: Response) -> None:
    response.delete_cookie(
        key=_REFRESH_COOKIE_NAME,
        httponly=True,
        secure=True,
        samesite="strict",
    )


def _get_metadata(request: Request) -> dict:
    return {
        "user_agent": request.headers.get("user-agent"),
        "ip_address": request.client.host if request.client else None,
    }


# ── WhatsApp OTP Flow ─────────────────────────────────────────────────────────


@router.post(
    "/otp/send",
    status_code=status.HTTP_200_OK,
    summary="Send WhatsApp OTP via authentication template",
)
async def send_otp(
    payload: OTPRequest,
    use_case: Annotated[SendOTPUseCase, Depends(get_send_otp_use_case)],
    rate_limiter: Annotated[OTPRateLimiter, Depends(get_otp_rate_limiter)],
):
    try:
        await rate_limiter.check_send_limit(payload.phone)
        await use_case.execute(payload.phone)
        return {"message": "OTP sent successfully"}
    except OTPRateLimitError as e:
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail=str(e))
    except Exception:
        logger.exception("OTP send failed")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send OTP. Please try again.",
        )


@router.post(
    "/otp/verify",
    response_model=OTPVerifyResponse,
    summary="Verify WhatsApp OTP → returns verification_token (proof of phone)",
)
async def verify_otp(
    payload: OTPVerifyRequest,
    request: Request,
    use_case: Annotated[VerifyOTPUseCase, Depends(get_verify_otp_use_case)],
    rate_limiter: Annotated[OTPRateLimiter, Depends(get_otp_rate_limiter)],
):
    try:
        ip = request.client.host if request.client else "unknown"
        await rate_limiter.check_verify_limit(ip)

        verification_token = await use_case.execute(
            phone=payload.phone,
            otp_code=payload.code,
        )

        return OTPVerifyResponse(verification_token=verification_token)

    except OTPRateLimitError as e:
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail=str(e))
    except OTPExpiredError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="OTP expired. Please request a new one.",
        )
    except OTPInvalidError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid OTP code.",
        )
    except OTPMaxAttemptsError:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many failed attempts. Please request a new OTP.",
        )


# ── Registration (Path A completion) ──────────────────────────────────────────


@router.post(
    "/register",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create verified rider from phone verification + profile data",
)
async def register(
    payload: RegisterRequest,
    request: Request,
    response: Response,
    use_case: Annotated[RegisterUseCase, Depends(get_register_use_case)],
):
    try:
        tokens = await use_case.execute(
            verification_token=payload.verification_token,
            full_name=payload.full_name,
            metadata=_get_metadata(request),
        )

        _set_refresh_cookie(response, tokens["refresh_token"])

        return TokenResponse(
            access_token=tokens["access_token"],
            expires_in=tokens["expires_in"],
        )
    except InvalidVerificationTokenError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired verification token. Please verify your phone again.",
        )
    except UserAlreadyExistsError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Phone number already registered. Please login instead.",
        )


# ── Google OAuth Flow (Mobile SDK) ────────────────────────────────────────────


@router.post(
    "/google/verify-token",
    response_model=TokenResponse,
    summary="Verify Google id_token from mobile SDK → create/find user",
)
async def google_verify_token(
    payload: GoogleTokenRequest,
    request: Request,
    response: Response,
    use_case: Annotated[GoogleVerifyTokenUseCase, Depends(get_google_verify_use_case)],
):
    try:
        tokens = await use_case.execute(
            id_token_str=payload.id_token,
            metadata=_get_metadata(request),
        )

        _set_refresh_cookie(response, tokens["refresh_token"])

        return TokenResponse(
            access_token=tokens["access_token"],
            expires_in=tokens["expires_in"],
            phone_required=tokens.get("phone_required", False),
        )
    except GoogleTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        )


@router.post(
    "/google/link-phone",
    response_model=TokenResponse,
    summary="Link verified phone to Google user (with account merge if needed)",
)
async def google_link_phone(
    payload: LinkPhoneRequest,
    request: Request,
    response: Response,
    current_user: CurrentUser,
    use_case: Annotated[LinkPhoneUseCase, Depends(get_link_phone_use_case)],
):
    try:
        tokens = await use_case.execute(
            current_user_id=current_user.user_id,
            verification_token=payload.verification_token,
            metadata=_get_metadata(request),
        )

        _set_refresh_cookie(response, tokens["refresh_token"])

        return TokenResponse(
            access_token=tokens["access_token"],
            expires_in=tokens["expires_in"],
            phone_required=False,
        )
    except InvalidVerificationTokenError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired verification token.",
        )
    except AuthDomainError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


# ── Session & Token Management ────────────────────────────────────────────────


@router.post(
    "/refresh",
    response_model=TokenResponse,
    summary="Rotate refresh token (cookie or body fallback for mobile)",
)
async def refresh_token(
    request: Request,
    response: Response,
    use_case: Annotated[RefreshTokenUseCase, Depends(get_refresh_use_case)],
):
    old_refresh = request.cookies.get(_REFRESH_COOKIE_NAME)

    if not old_refresh:
        try:
            body = await request.body()
            if body:
                data = json.loads(body)
                old_refresh = data.get("refresh_token")
        except Exception:
            pass

    if not old_refresh:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Refresh token required (cookie or body)",
        )

    try:
        tokens = await use_case.execute(old_refresh)
        _set_refresh_cookie(response, tokens["refresh_token"])

        return TokenResponse(
            access_token=tokens["access_token"],
            expires_in=tokens["expires_in"],
        )
    except InvalidSessionError:
        _clear_refresh_cookie(response)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired session",
        )


@router.get(
    "/sessions",
    response_model=list[SessionResponse],
    summary="List active sessions for the authenticated user",
)
async def get_active_sessions(
    current_user: CurrentUser,
    session_repo: Annotated[SessionRepository, Depends(get_session_repo)],
):
    sessions = await session_repo.find_active_by_user(current_user.user_id)

    return [
        SessionResponse(
            id=s.id,
            user_agent=s.user_agent,
            ip_address=s.ip_address,
            last_active_at=s.last_active_at,
            is_current=(s.id == current_user.session_id),
        )
        for s in sessions
    ]


@router.delete(
    "/sessions/{session_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Revoke a specific session (not the current one)",
)
async def revoke_session(
    session_id: uuid.UUID,
    current_user: CurrentUser,
    session_repo: Annotated[SessionRepository, Depends(get_session_repo)],
):
    session = await session_repo.find_by_id(session_id)

    if not session or session.user_id != current_user.user_id:
        raise HTTPException(status_code=404, detail="Session not found")

    if session.id == current_user.session_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot revoke current session. Use /logout instead.",
        )

    session.is_revoked = True
    await session_repo.update(session)


@router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Logout current session",
)
async def logout(
    current_user: CurrentUser,
    request: Request,
    response: Response,
    session_repo: Annotated[SessionRepository, Depends(get_session_repo)],
):
    refresh_token_raw = request.cookies.get(_REFRESH_COOKIE_NAME)

    if refresh_token_raw:
        token_hash = hashlib.sha256(refresh_token_raw.encode()).hexdigest()
        session = await session_repo.find_by_hash(token_hash)
    else:
        session = await session_repo.find_by_id(current_user.session_id)

    if session:
        session.is_revoked = True
        await session_repo.update(session)

    _clear_refresh_cookie(response)


# ── Profile ───────────────────────────────────────────────────────────────────


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current user profile",
)
async def get_me(
    current_user: CurrentUser,
    user_repo: Annotated[UserRepository, Depends(get_user_repo)],
):
    user = await user_repo.find_by_id(current_user.user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return UserResponse(
        id=user.id,
        full_name=user.full_name,
        email=user.email,
        phone=user.phone,
        role=user.role.value,
        is_active=user.is_active,
        is_verified=user.is_verified,
        is_onboarded=bool(user.phone and user.full_name),
    )
```

## services\auth\auth\api\__init__.py

```python
"""Auth API layer — controllers only, zero business logic."""

```

## services\auth\auth\application\schemas.py

```python
"""Auth API request/response schemas.

Pydantic models for HTTP boundary validation only.
Domain models (User dataclass) are never exposed directly to the API.
"""
from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field


# --- WHATSAPP OTP SCHEMAS ---


class OTPRequest(BaseModel):
    """Initial request to trigger WhatsApp message."""

    phone: str = Field(
        ..., pattern=r"^\+?[1-9]\d{7,14}$", examples=["+923001234567"]
    )


class OTPVerifyRequest(BaseModel):
    """Submission of the 6-digit code."""

    phone: str = Field(..., pattern=r"^\+?[1-9]\d{7,14}$")
    code: str = Field(..., min_length=6, max_length=6, examples=["123456"])


class OTPVerifyResponse(BaseModel):
    """Returned after successful OTP verification — proof of phone ownership."""

    verification_token: str


# --- REGISTRATION SCHEMAS ---


class RegisterRequest(BaseModel):
    """Profile completion for new phone-verified users (Path A)."""

    full_name: str = Field(..., min_length=2, max_length=255)
    verification_token: str


# --- GOOGLE OAUTH SCHEMAS ---


class GoogleTokenRequest(BaseModel):
    """Mobile app sends the id_token from Google Sign-In SDK."""

    id_token: str


class LinkPhoneRequest(BaseModel):
    """Link a verified phone to the authenticated Google user (Path B)."""

    verification_token: str


# --- TOKEN & SESSION SCHEMAS ---


class TokenResponse(BaseModel):
    """Standard JWT response for successful login/refresh."""

    access_token: str
    token_type: str = "bearer"
    expires_in: int
    # True if user still needs to verify phone (Google-first path)
    phone_required: bool = False


class SessionResponse(BaseModel):
    """Metadata for the 'Active Devices' UI."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_agent: Optional[str]
    ip_address: Optional[str]
    last_active_at: datetime
    is_current: bool = False


# --- USER PROFILE SCHEMAS ---


class UserResponse(BaseModel):
    """The public user profile returned by /me."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    full_name: Optional[str]
    email: Optional[str]
    phone: Optional[str]
    role: str
    is_active: bool
    is_verified: bool
    is_onboarded: bool = False

```

## services\auth\auth\application\use_cases.py

```python
"""Auth use cases — all business logic lives here, not in API routes.

Use cases receive dependencies via constructor injection.
They are instantiated by provider functions in infrastructure/dependencies.py.
"""
from __future__ import annotations

import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from uuid import uuid4

from sp.core.config import Settings
from sp.infrastructure.security.jwt import (
    create_tokens,
    create_verification_token,
    verify_verification_token,
)

from ..domain.exceptions import (
    GoogleTokenError,
    InvalidSessionError,
    InvalidVerificationTokenError,
    OTPExpiredError,
    OTPInvalidError,
    OTPMaxAttemptsError,
    UserAlreadyExistsError,
)
from ..domain.interfaces import (
    AccountRepositoryProtocol,
    GoogleTokenVerifierProtocol,
    OTPProviderProtocol,
    SessionRepositoryProtocol,
    UserRepositoryProtocol,
    VerificationRepositoryProtocol,
)
from ..domain.models import Account, Session, User, UserRole, Verification


# ── Helpers ───────────────────────────────────────────────────────────────────


def _build_session_and_tokens(
    user: User,
    session_id,
    settings: Settings,
    metadata: dict,
) -> tuple[Session, dict]:
    """Shared logic for creating a session + token pair."""
    tokens = create_tokens(
        user_id=user.id,
        email=user.email or "",
        role=user.role.value,
        session_id=session_id,
        secret=settings.JWT_SECRET,
        algorithm=settings.JWT_ALGORITHM,
        access_ttl_minutes=settings.JWT_EXPIRATION_MINUTES,
    )
    session = Session(
        id=session_id,
        user_id=user.id,
        refresh_token_hash=hashlib.sha256(
            tokens["refresh_token"].encode()
        ).hexdigest(),
        expires_at=datetime.now(timezone.utc)
        + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
        user_agent=metadata.get("user_agent"),
        ip_address=metadata.get("ip_address"),
    )
    return session, tokens


# ── OTP: Send ─────────────────────────────────────────────────────────────────


class SendOTPUseCase:
    """Generate and send a 6-digit OTP via WhatsApp."""

    def __init__(
        self,
        otp_provider: OTPProviderProtocol,
        verification_repo: VerificationRepositoryProtocol,
    ) -> None:
        self.otp_provider = otp_provider
        self.verification_repo = verification_repo

    async def execute(self, phone: str) -> None:
        code = f"{secrets.randbelow(900000) + 100000}"

        verification = Verification(
            id=uuid4(),
            identifier=phone,
            code_hash=hashlib.sha256(code.encode()).hexdigest(),
            expires_at=datetime.now(timezone.utc) + timedelta(minutes=5),
        )

        await self.verification_repo.create(verification)
        await self.otp_provider.send_otp(phone, code)


# ── OTP: Verify (returns verification_token, does NOT create user) ────────────


class VerifyOTPUseCase:
    """Verify the OTP code → return a short-lived verification_token (proof of phone)."""

    def __init__(
        self,
        verification_repo: VerificationRepositoryProtocol,
        settings: Settings,
    ) -> None:
        self.verification_repo = verification_repo
        self.settings = settings

    async def execute(self, phone: str, otp_code: str) -> str:
        """Returns a verification_token JWT proving phone ownership."""
        verification = await self.verification_repo.find_valid(phone)
        if not verification:
            raise OTPExpiredError("OTP expired or not found")

        if verification.attempt_count >= verification.max_attempts:
            raise OTPMaxAttemptsError("Too many failed attempts. Request a new OTP.")

        incoming_hash = hashlib.sha256(otp_code.encode()).hexdigest()
        if verification.code_hash != incoming_hash:
            await self.verification_repo.increment_attempts(verification.id)
            raise OTPInvalidError("Invalid OTP code")

        await self.verification_repo.mark_verified(verification.id)

        return create_verification_token(
            phone=phone,
            secret=self.settings.JWT_SECRET,
            algorithm=self.settings.JWT_ALGORITHM,
        )


# ── Register (Phone-first Path A completion) ─────────────────────────────────


class RegisterUseCase:
    """Create a verified rider from a verification_token + profile data."""

    def __init__(
        self,
        user_repo: UserRepositoryProtocol,
        session_repo: SessionRepositoryProtocol,
        settings: Settings,
    ) -> None:
        self.user_repo = user_repo
        self.session_repo = session_repo
        self.settings = settings

    async def execute(
        self, verification_token: str, full_name: str, metadata: dict
    ) -> dict:
        # 1. Decode verification_token → extract phone
        phone = verify_verification_token(
            verification_token,
            self.settings.JWT_SECRET,
            self.settings.JWT_ALGORITHM,
        )
        if not phone:
            raise InvalidVerificationTokenError(
                "Invalid or expired verification token"
            )

        # 2. Check phone isn't already registered
        existing = await self.user_repo.find_by_phone(phone)
        if existing:
            raise UserAlreadyExistsError("Phone number already registered")

        # 3. Create verified user
        user = await self.user_repo.save(
            User.create(
                role=UserRole.PASSENGER,
                full_name=full_name,
                phone=phone,
                is_verified=True,
            )
        )

        # 4. Create session + tokens
        session_id = uuid4()
        session, tokens = _build_session_and_tokens(
            user, session_id, self.settings, metadata
        )
        await self.session_repo.save(session)

        return tokens


# ── Google: Verify ID Token (Path B start) ────────────────────────────────────


class GoogleVerifyTokenUseCase:
    """Verify Google id_token → create unverified user + account → issue tokens."""

    def __init__(
        self,
        google_verifier: GoogleTokenVerifierProtocol,
        user_repo: UserRepositoryProtocol,
        account_repo: AccountRepositoryProtocol,
        session_repo: SessionRepositoryProtocol,
        settings: Settings,
    ) -> None:
        self.google_verifier = google_verifier
        self.user_repo = user_repo
        self.account_repo = account_repo
        self.session_repo = session_repo
        self.settings = settings

    async def execute(self, id_token_str: str, metadata: dict) -> dict:
        # 1. Verify the Google id_token
        try:
            claims = await self.google_verifier.verify(id_token_str)
        except Exception as e:
            raise GoogleTokenError(f"Google token verification failed: {e}")

        google_sub = claims["sub"]
        email = claims.get("email", "")
        name = claims.get("name", "")

        # 2. Check if this Google account already exists
        existing_account = await self.account_repo.find_by_provider(
            "google", google_sub
        )

        if existing_account:
            # Returning user — find their User and issue tokens
            user = await self.user_repo.find_by_id(existing_account.user_id)
            if not user:
                raise GoogleTokenError("Linked user not found")
        else:
            # New user — create User (unverified) + Account
            user = await self.user_repo.save(
                User.create(
                    role=UserRole.PASSENGER,
                    full_name=name,
                    email=email,
                    is_verified=False,  # not verified until phone is linked
                )
            )
            await self.account_repo.save(
                Account(
                    id=uuid4(),
                    user_id=user.id,
                    provider="google",
                    provider_account_id=google_sub,
                )
            )

        # 3. Create session + tokens
        session_id = uuid4()
        session, tokens = _build_session_and_tokens(
            user, session_id, self.settings, metadata
        )
        await self.session_repo.save(session)

        # 4. Signal to frontend whether phone verification is needed
        tokens["phone_required"] = not user.is_verified

        return tokens


# ── Google: Link Phone (Path B completion, with account merge) ────────────────


class LinkPhoneUseCase:
    """Link a verified phone to the authenticated Google user.

    Handles account merge: if the phone belongs to an existing phone-only user,
    migrates the Google Account to that user and deletes the temporary one.
    """

    def __init__(
        self,
        user_repo: UserRepositoryProtocol,
        account_repo: AccountRepositoryProtocol,
        session_repo: SessionRepositoryProtocol,
        settings: Settings,
    ) -> None:
        self.user_repo = user_repo
        self.account_repo = account_repo
        self.session_repo = session_repo
        self.settings = settings

    async def execute(
        self,
        current_user_id,
        verification_token: str,
        metadata: dict,
    ) -> dict:
        # 1. Decode verification_token → extract phone
        phone = verify_verification_token(
            verification_token,
            self.settings.JWT_SECRET,
            self.settings.JWT_ALGORITHM,
        )
        if not phone:
            raise InvalidVerificationTokenError(
                "Invalid or expired verification token"
            )

        # 2. Load the current (Google-created) user
        current_user = await self.user_repo.find_by_id(current_user_id)
        if not current_user:
            raise InvalidSessionError("Current user not found")

        # 3. Check if this phone belongs to an existing user
        phone_owner = await self.user_repo.find_by_phone(phone)

        if phone_owner and phone_owner.id != current_user.id:
            # ── ACCOUNT MERGE ─────────────────────────────────────────
            # The phone belongs to an existing phone-only user.
            # Migrate Google account(s) from current_user → phone_owner.
            google_accounts = await self.account_repo.find_by_user_id(
                current_user.id
            )
            for account in google_accounts:
                await self.account_repo.transfer_to_user(
                    account.id, phone_owner.id
                )

            # Copy Google info to phone_owner if missing
            if not phone_owner.full_name and current_user.full_name:
                phone_owner.full_name = current_user.full_name
            if not phone_owner.email and current_user.email:
                phone_owner.email = current_user.email
            await self.user_repo.update(phone_owner)

            # Revoke all sessions for the temporary Google user
            await self.session_repo.revoke_all_for_user(current_user.id)

            # Delete the temporary Google user (cascade deletes sessions)
            await self.user_repo.delete(current_user.id)

            # The merged user is the phone_owner
            merged_user = phone_owner
        else:
            # ── SIMPLE LINK (no conflict) ─────────────────────────────
            current_user.phone = phone
            current_user.is_verified = True
            await self.user_repo.update(current_user)
            merged_user = current_user

        # 4. Create new session + tokens for the final user
        session_id = uuid4()
        session, tokens = _build_session_and_tokens(
            merged_user, session_id, self.settings, metadata
        )
        await self.session_repo.save(session)
        tokens["phone_required"] = False

        return tokens


# ── Token Refresh ─────────────────────────────────────────────────────────────


class RefreshTokenUseCase:
    """Rotate the refresh token and issue a new access token."""

    def __init__(
        self,
        session_repo: SessionRepositoryProtocol,
        user_repo: UserRepositoryProtocol,
        settings: Settings,
    ) -> None:
        self.session_repo = session_repo
        self.user_repo = user_repo
        self.settings = settings

    async def execute(self, old_refresh_token: str) -> dict:
        token_hash = hashlib.sha256(old_refresh_token.encode()).hexdigest()
        session = await self.session_repo.find_by_hash(token_hash)

        if not session or session.is_revoked:
            raise InvalidSessionError("Session not found or revoked")

        if session.expires_at < datetime.now(timezone.utc):
            raise InvalidSessionError("Session expired")

        user = await self.user_repo.find_by_id(session.user_id)
        if not user:
            raise InvalidSessionError("User not found")

        new_tokens = create_tokens(
            user_id=user.id,
            email=user.email or "",
            role=user.role.value,
            session_id=session.id,
            secret=self.settings.JWT_SECRET,
            algorithm=self.settings.JWT_ALGORITHM,
            access_ttl_minutes=self.settings.JWT_EXPIRATION_MINUTES,
        )

        session.refresh_token_hash = hashlib.sha256(
            new_tokens["refresh_token"].encode()
        ).hexdigest()
        session.last_active_at = datetime.now(timezone.utc)
        await self.session_repo.update(session)

        return new_tokens
```

## services\auth\auth\application\__init__.py

```python
"""Auth application layer — use cases and request/response schemas."""

```

## services\auth\auth\domain\exceptions.py

```python
"""Auth domain exceptions — typed errors that map to HTTP responses in api/router.py."""


class AuthDomainError(Exception):
    """Base for all auth domain exceptions."""


class InvalidCredentialsError(AuthDomainError):
    """Raised when login credentials are wrong."""


class UserNotFoundError(AuthDomainError):
    """Raised when a user cannot be located by id or email."""


class UserAlreadyExistsError(AuthDomainError):
    """Raised when attempting to register a duplicate email or phone."""


class InactiveUserError(AuthDomainError):
    """Raised when a deactivated account attempts to authenticate."""


class TokenExpiredError(AuthDomainError):
    """Raised when a JWT token has passed its expiry."""


class InvalidSessionError(AuthDomainError):
    """Raised when a refresh token maps to no active session."""


class OTPExpiredError(AuthDomainError):
    """Raised when the OTP has expired or was already used."""


class OTPInvalidError(AuthDomainError):
    """Raised when the OTP code does not match."""


class OTPMaxAttemptsError(AuthDomainError):
    """Raised when too many OTP verification attempts have been made."""


class OTPRateLimitError(AuthDomainError):
    """Raised when OTP send/verify rate limit is exceeded."""


class GoogleTokenError(AuthDomainError):
    """Raised when Google id_token verification fails."""


class InvalidVerificationTokenError(AuthDomainError):
    """Raised when the phone verification_token is invalid or expired."""


class PhoneAlreadyLinkedError(AuthDomainError):
    """Raised when trying to link a phone that belongs to another account (pre-merge info)."""

```

## services\auth\auth\domain\interfaces.py

```python
"""Repository protocols — contracts without implementations.

The infrastructure layer provides concrete implementations.
The application layer depends only on these protocols (Dependency Inversion).
"""
from typing import Protocol, runtime_checkable
from uuid import UUID

from .models import User, Session, Account, Verification


@runtime_checkable
class UserRepositoryProtocol(Protocol):
    async def find_by_id(self, user_id: UUID) -> User | None: ...
    async def find_by_phone(self, phone: str) -> User | None: ...
    async def find_by_email(self, email: str) -> User | None: ...
    async def save(self, user: User) -> User: ...
    async def update(self, user: User) -> User: ...
    async def delete(self, user_id: UUID) -> bool: ...


@runtime_checkable
class SessionRepositoryProtocol(Protocol):
    async def find_by_id(self, session_id: UUID) -> Session | None: ...
    async def find_by_hash(self, token_hash: str) -> Session | None: ...
    async def find_active_by_user(self, user_id: UUID) -> list[Session]: ...
    async def save(self, session: Session) -> Session: ...
    async def update(self, session: Session) -> Session: ...
    async def revoke_all_for_user(self, user_id: UUID) -> None: ...


@runtime_checkable
class AccountRepositoryProtocol(Protocol):
    async def find_by_provider(
        self, provider: str, provider_account_id: str
    ) -> Account | None: ...
    async def find_by_user_id(self, user_id: UUID) -> list[Account]: ...
    async def save(self, account: Account) -> Account: ...
    async def transfer_to_user(
        self, account_id: UUID, new_user_id: UUID
    ) -> None: ...


@runtime_checkable
class VerificationRepositoryProtocol(Protocol):
    async def create(self, verification: Verification) -> Verification: ...
    async def find_valid(self, identifier: str) -> Verification | None: ...
    async def mark_verified(self, verification_id: UUID) -> None: ...
    async def increment_attempts(self, verification_id: UUID) -> int: ...


@runtime_checkable
class OTPProviderProtocol(Protocol):
    async def send_otp(self, phone: str, code: str) -> None: ...


@runtime_checkable
class GoogleTokenVerifierProtocol(Protocol):
    async def verify(self, id_token: str) -> dict: ...
```

## services\auth\auth\domain\models.py

```python
"""Auth domain models — pure Python dataclasses, no ORM, no Pydantic, no libs."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from uuid import UUID, uuid4


class UserRole(str, Enum):
    PASSENGER = "passenger"
    DRIVER = "driver"
    ADMIN = "admin"


@dataclass
class User:
    id: UUID
    role: UserRole
    full_name: str | None = None
    email: str | None = None
    phone: str | None = None
    is_active: bool = True
    is_verified: bool = False  # True once phone is verified via OTP
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @classmethod
    def create(
        cls,
        role: UserRole,
        full_name: str | None = None,
        email: str | None = None,
        phone: str | None = None,
        is_verified: bool = False,
    ) -> User:
        return cls(
            id=uuid4(),
            role=role,
            full_name=full_name,
            email=email,
            phone=phone,
            is_verified=is_verified,
        )


@dataclass
class Session:
    id: UUID
    user_id: UUID
    refresh_token_hash: str
    expires_at: datetime
    is_revoked: bool = False
    user_agent: str | None = None
    ip_address: str | None = None
    last_active_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class Account:
    id: UUID
    user_id: UUID
    provider: str  # e.g., "google"
    provider_account_id: str


@dataclass
class Verification:
    id: UUID
    identifier: str  # phone number
    code_hash: str
    expires_at: datetime
    verified_at: datetime | None = None
    attempt_count: int = 0
    max_attempts: int = 5

```

## services\auth\auth\domain\__init__.py

```python
"""Auth service domain layer — pure Python, zero external dependencies."""

```

## services\auth\auth\infrastructure\dependencies.py

```python
"""Auth DI provider functions — bridge FastAPI Depends with constructor-injected use cases.

Rule: FastAPI Depends() is used here and in api/.
      Constructor injection is used inside use_cases.py.
"""
from __future__ import annotations

from typing import Annotated

from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from sp.core.config import Settings, get_settings
from sp.infrastructure.cache.manager import CacheManager
from sp.infrastructure.db.session import get_async_session

from ..application.use_cases import (
    GoogleVerifyTokenUseCase,
    LinkPhoneUseCase,
    RefreshTokenUseCase,
    RegisterUseCase,
    SendOTPUseCase,
    VerifyOTPUseCase,
)
from ..infrastructure.messaging.whatsapp import PywaOTPProvider
from ..infrastructure.repositories import (
    AccountRepository,
    SessionRepository,
    UserRepository,
    VerificationRepository,
)
from ..infrastructure.security.google_oauth import GoogleTokenVerifier
from ..infrastructure.security.rate_limit import OTPRateLimiter


# ── Repository providers ─────────────────────────────────────────────────────


def get_user_repo(
    session: Annotated[AsyncSession, Depends(get_async_session)],
) -> UserRepository:
    return UserRepository(session)


def get_session_repo(
    session: Annotated[AsyncSession, Depends(get_async_session)],
) -> SessionRepository:
    return SessionRepository(session)


def get_account_repo(
    session: Annotated[AsyncSession, Depends(get_async_session)],
) -> AccountRepository:
    return AccountRepository(session)


def get_verification_repo(
    session: Annotated[AsyncSession, Depends(get_async_session)],
) -> VerificationRepository:
    return VerificationRepository(session)


# ── External service providers ────────────────────────────────────────────────


def get_otp_provider(
    settings: Annotated[Settings, Depends(get_settings)],
) -> PywaOTPProvider:
    return PywaOTPProvider(
        token=settings.WHATSAPP_TOKEN,
        phone_id=settings.WHATSAPP_PHONE_ID,
        template_name=settings.WHATSAPP_AUTH_TEMPLATE_NAME,
    )


def get_google_verifier(
    settings: Annotated[Settings, Depends(get_settings)],
) -> GoogleTokenVerifier:
    return GoogleTokenVerifier(client_id=settings.GOOGLE_CLIENT_ID)


def get_cache_manager(request: Request) -> CacheManager:
    """Retrieve CacheManager from app.state (initialized at lifespan startup)."""
    return request.app.state.cache


def get_otp_rate_limiter(
    cache: Annotated[CacheManager, Depends(get_cache_manager)],
) -> OTPRateLimiter:
    return OTPRateLimiter(cache=cache)


# ── Use-case providers ────────────────────────────────────────────────────────


def get_send_otp_use_case(
    otp_provider: Annotated[PywaOTPProvider, Depends(get_otp_provider)],
    verification_repo: Annotated[VerificationRepository, Depends(get_verification_repo)],
) -> SendOTPUseCase:
    return SendOTPUseCase(otp_provider, verification_repo)


def get_verify_otp_use_case(
    verification_repo: Annotated[VerificationRepository, Depends(get_verification_repo)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> VerifyOTPUseCase:
    return VerifyOTPUseCase(verification_repo, settings)


def get_register_use_case(
    user_repo: Annotated[UserRepository, Depends(get_user_repo)],
    session_repo: Annotated[SessionRepository, Depends(get_session_repo)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> RegisterUseCase:
    return RegisterUseCase(user_repo, session_repo, settings)


def get_google_verify_use_case(
    google_verifier: Annotated[GoogleTokenVerifier, Depends(get_google_verifier)],
    user_repo: Annotated[UserRepository, Depends(get_user_repo)],
    account_repo: Annotated[AccountRepository, Depends(get_account_repo)],
    session_repo: Annotated[SessionRepository, Depends(get_session_repo)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> GoogleVerifyTokenUseCase:
    return GoogleVerifyTokenUseCase(
        google_verifier, user_repo, account_repo, session_repo, settings
    )


def get_link_phone_use_case(
    user_repo: Annotated[UserRepository, Depends(get_user_repo)],
    account_repo: Annotated[AccountRepository, Depends(get_account_repo)],
    session_repo: Annotated[SessionRepository, Depends(get_session_repo)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> LinkPhoneUseCase:
    return LinkPhoneUseCase(user_repo, account_repo, session_repo, settings)


def get_refresh_use_case(
    session_repo: Annotated[SessionRepository, Depends(get_session_repo)],
    user_repo: Annotated[UserRepository, Depends(get_user_repo)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> RefreshTokenUseCase:
    return RefreshTokenUseCase(session_repo, user_repo, settings)

```

## services\auth\auth\infrastructure\messaging\whatsapp.py

```python
"""WhatsApp OTP provider via pywa authentication template.

Uses pywa's send_template() with an AUTHENTICATION category template
and COPY_CODE OTP button, as required by Meta's Business API policy.
"""
from __future__ import annotations

import asyncio
import inspect
import logging

from pywa import WhatsApp
from pywa.types import Template as WaTemplate

from auth.domain.interfaces import OTPProviderProtocol

logger = logging.getLogger("auth.messaging.whatsapp")


class PywaOTPProvider(OTPProviderProtocol):
    def __init__(self, token: str, phone_id: str, template_name: str) -> None:
        self.client = WhatsApp(token=token, phone_id=phone_id)
        self.template_name = template_name

    async def send_otp(self, phone: str, code: str) -> None:
        """Send OTP via WhatsApp authentication template with COPY_CODE button."""
        template = WaTemplate(
            name=self.template_name,
            language=WaTemplate.Language.ENGLISH_US,
            body=WaTemplate.Body(code=code),
            buttons=WaTemplate.OTPButton(
                otp_type=WaTemplate.OTPButton.OtpType.COPY_CODE,
            ),
        )

        send_fn = self.client.send_template

        if inspect.iscoroutinefunction(send_fn):
            await send_fn(to=phone, template=template)
        else:
            await asyncio.to_thread(send_fn, to=phone, template=template)

        logger.info("OTP template sent", extra={"phone": phone[-4:]})
```

## services\auth\auth\infrastructure\orm_models.py

```python
"""Auth ORM models — SQLAlchemy only, no business logic.

All auth tables live in the 'auth' PostgreSQL schema.
The single Base from platform ensures Alembic discovers these models.
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sp.infrastructure.db.base import Base, TimestampMixin
from sqlalchemy import Boolean, String, ForeignKey, DateTime, Text, Integer, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PgUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship


class UserORM(Base, TimestampMixin):
    """The central profile connecting identities."""

    __tablename__ = "users"
    __table_args__ = {"schema": "auth"}

    id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    full_name: Mapped[str | None] = mapped_column(String(255))
    email: Mapped[str | None] = mapped_column(String(255), unique=True, index=True)
    phone: Mapped[str | None] = mapped_column(String(20), unique=True, index=True)
    role: Mapped[str] = mapped_column(String(20), default="passenger")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)

    # Relationships
    accounts: Mapped[list[AccountORM]] = relationship(back_populates="user", cascade="all, delete-orphan")
    sessions: Mapped[list[SessionORM]] = relationship(back_populates="user", cascade="all, delete-orphan")


class AccountORM(Base, TimestampMixin):
    """The OAuth bridge (e.g., Google login)."""

    __tablename__ = "accounts"
    __table_args__ = (
        UniqueConstraint("provider", "provider_account_id", name="uq_provider_account"),
        {"schema": "auth"}
    )

    id: Mapped[uuid.UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("auth.users.id", ondelete="CASCADE"))

    provider: Mapped[str] = mapped_column(String(50))  # e.g., "google"
    provider_account_id: Mapped[str] = mapped_column(String(255))  # Google's sub ID

    user: Mapped[UserORM] = relationship(back_populates="accounts")


class SessionORM(Base, TimestampMixin):
    """The active device tracker with Refresh Token Rotation."""

    __tablename__ = "sessions"
    __table_args__ = {"schema": "auth"}

    id: Mapped[uuid.UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("auth.users.id", ondelete="CASCADE"))

    refresh_token_hash: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    is_revoked: Mapped[bool] = mapped_column(Boolean, default=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    # Metadata for Device Management UI
    user_agent: Mapped[str | None] = mapped_column(Text)
    ip_address: Mapped[str | None] = mapped_column(String(45))
    last_active_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )

    user: Mapped[UserORM] = relationship(back_populates="sessions")


class VerificationORM(Base, TimestampMixin):
    """Temporary storage for WhatsApp OTPs."""

    __tablename__ = "verifications"
    __table_args__ = {"schema": "auth"}

    id: Mapped[uuid.UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    identifier: Mapped[str] = mapped_column(String(255), index=True)  # phone number or email
    code_hash: Mapped[str] = mapped_column(String(255))
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    attempt_count: Mapped[int] = mapped_column(Integer, default=0)

```

## services\auth\auth\infrastructure\repositories.py

```python
"""Auth concrete repositories — implement domain protocols via SQLAlchemy."""
from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from ..domain.models import User, UserRole, Session, Account, Verification
from ..domain.interfaces import (
    UserRepositoryProtocol,
    SessionRepositoryProtocol,
    AccountRepositoryProtocol,
    VerificationRepositoryProtocol,
)
from .orm_models import UserORM, SessionORM, AccountORM, VerificationORM


# ── User Repository ──────────────────────────────────────────────────────────


class UserRepository(UserRepositoryProtocol):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    def _to_domain(self, orm: UserORM) -> User:
        return User(
            id=orm.id,
            role=UserRole(orm.role),
            full_name=orm.full_name,
            email=orm.email,
            phone=orm.phone,
            is_active=orm.is_active,
            is_verified=orm.is_verified,
            created_at=orm.created_at,
        )

    async def find_by_id(self, user_id: UUID) -> User | None:
        result = await self._session.execute(
            select(UserORM).where(UserORM.id == user_id)
        )
        orm = result.scalar_one_or_none()
        return self._to_domain(orm) if orm else None

    async def find_by_phone(self, phone: str) -> User | None:
        result = await self._session.execute(
            select(UserORM).where(UserORM.phone == phone)
        )
        orm = result.scalar_one_or_none()
        return self._to_domain(orm) if orm else None

    async def find_by_email(self, email: str) -> User | None:
        result = await self._session.execute(
            select(UserORM).where(UserORM.email == email)
        )
        orm = result.scalar_one_or_none()
        return self._to_domain(orm) if orm else None

    async def save(self, user: User) -> User:
        orm = UserORM(
            id=user.id,
            role=user.role.value,
            full_name=user.full_name,
            email=user.email,
            phone=user.phone,
            is_active=user.is_active,
            is_verified=user.is_verified,
        )
        merged = await self._session.merge(orm)
        await self._session.flush()
        return self._to_domain(merged)

    async def update(self, user: User) -> User:
        await self._session.execute(
            update(UserORM)
            .where(UserORM.id == user.id)
            .values(
                full_name=user.full_name,
                email=user.email,
                phone=user.phone,
                role=user.role.value,
                is_active=user.is_active,
                is_verified=user.is_verified,
            )
        )
        await self._session.flush()
        return user

    async def delete(self, user_id: UUID) -> bool:
        result = await self._session.execute(
            delete(UserORM).where(UserORM.id == user_id)
        )
        await self._session.flush()
        return result.rowcount > 0


# ── Session Repository ────────────────────────────────────────────────────────


class SessionRepository(SessionRepositoryProtocol):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    def _to_domain(self, orm: SessionORM) -> Session:
        return Session(
            id=orm.id,
            user_id=orm.user_id,
            refresh_token_hash=orm.refresh_token_hash,
            expires_at=orm.expires_at,
            is_revoked=orm.is_revoked,
            user_agent=orm.user_agent,
            ip_address=orm.ip_address,
            last_active_at=orm.last_active_at,
        )

    async def find_by_id(self, session_id: UUID) -> Session | None:
        result = await self._session.execute(
            select(SessionORM).where(SessionORM.id == session_id)
        )
        orm = result.scalar_one_or_none()
        return self._to_domain(orm) if orm else None

    async def find_by_hash(self, token_hash: str) -> Session | None:
        result = await self._session.execute(
            select(SessionORM).where(
                SessionORM.refresh_token_hash == token_hash,
                SessionORM.is_revoked.is_(False),
            )
        )
        orm = result.scalar_one_or_none()
        return self._to_domain(orm) if orm else None

    async def find_active_by_user(self, user_id: UUID) -> list[Session]:
        result = await self._session.execute(
            select(SessionORM).where(
                SessionORM.user_id == user_id,
                SessionORM.is_revoked.is_(False),
                SessionORM.expires_at > datetime.now(timezone.utc),
            )
        )
        return [self._to_domain(orm) for orm in result.scalars().all()]

    async def save(self, session: Session) -> Session:
        orm = SessionORM(
            id=session.id,
            user_id=session.user_id,
            refresh_token_hash=session.refresh_token_hash,
            expires_at=session.expires_at,
            is_revoked=session.is_revoked,
            user_agent=session.user_agent,
            ip_address=session.ip_address,
            last_active_at=session.last_active_at,
        )
        self._session.add(orm)
        await self._session.flush()
        return self._to_domain(orm)

    async def update(self, session: Session) -> Session:
        await self._session.execute(
            update(SessionORM)
            .where(SessionORM.id == session.id)
            .values(
                refresh_token_hash=session.refresh_token_hash,
                is_revoked=session.is_revoked,
                last_active_at=session.last_active_at,
            )
        )
        await self._session.flush()
        return session

    async def revoke_all_for_user(self, user_id: UUID) -> None:
        """Revoke all sessions for a user (used during account merge)."""
        await self._session.execute(
            update(SessionORM)
            .where(SessionORM.user_id == user_id, SessionORM.is_revoked.is_(False))
            .values(is_revoked=True)
        )
        await self._session.flush()


# ── Account Repository ────────────────────────────────────────────────────────


class AccountRepository(AccountRepositoryProtocol):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    def _to_domain(self, orm: AccountORM) -> Account:
        return Account(
            id=orm.id,
            user_id=orm.user_id,
            provider=orm.provider,
            provider_account_id=orm.provider_account_id,
        )

    async def find_by_provider(
        self, provider: str, provider_account_id: str
    ) -> Account | None:
        result = await self._session.execute(
            select(AccountORM).where(
                AccountORM.provider == provider,
                AccountORM.provider_account_id == provider_account_id,
            )
        )
        orm = result.scalar_one_or_none()
        return self._to_domain(orm) if orm else None

    async def find_by_user_id(self, user_id: UUID) -> list[Account]:
        result = await self._session.execute(
            select(AccountORM).where(AccountORM.user_id == user_id)
        )
        return [self._to_domain(orm) for orm in result.scalars().all()]

    async def save(self, account: Account) -> Account:
        orm = AccountORM(
            id=account.id,
            user_id=account.user_id,
            provider=account.provider,
            provider_account_id=account.provider_account_id,
        )
        self._session.add(orm)
        await self._session.flush()
        return self._to_domain(orm)

    async def transfer_to_user(self, account_id: UUID, new_user_id: UUID) -> None:
        """Move an account record to a different user (for account merges)."""
        await self._session.execute(
            update(AccountORM)
            .where(AccountORM.id == account_id)
            .values(user_id=new_user_id)
        )
        await self._session.flush()


# ── Verification Repository ──────────────────────────────────────────────────


class VerificationRepository(VerificationRepositoryProtocol):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    def _to_domain(self, orm: VerificationORM) -> Verification:
        return Verification(
            id=orm.id,
            identifier=orm.identifier,
            code_hash=orm.code_hash,
            expires_at=orm.expires_at,
            verified_at=orm.verified_at,
            attempt_count=orm.attempt_count,
        )

    async def create(self, verification: Verification) -> Verification:
        orm = VerificationORM(
            id=verification.id,
            identifier=verification.identifier,
            code_hash=verification.code_hash,
            expires_at=verification.expires_at,
        )
        self._session.add(orm)
        await self._session.flush()
        return self._to_domain(orm)

    async def find_valid(self, identifier: str) -> Verification | None:
        result = await self._session.execute(
            select(VerificationORM)
            .where(
                VerificationORM.identifier == identifier,
                VerificationORM.expires_at > datetime.now(timezone.utc),
                VerificationORM.verified_at.is_(None),
            )
            .order_by(VerificationORM.created_at.desc())
            .limit(1)
        )
        orm = result.scalar_one_or_none()
        return self._to_domain(orm) if orm else None

    async def mark_verified(self, verification_id: UUID) -> None:
        await self._session.execute(
            update(VerificationORM)
            .where(VerificationORM.id == verification_id)
            .values(verified_at=datetime.now(timezone.utc))
        )
        await self._session.flush()

    async def increment_attempts(self, verification_id: UUID) -> int:
        result = await self._session.execute(
            select(VerificationORM).where(VerificationORM.id == verification_id)
        )
        orm = result.scalar_one()
        orm.attempt_count += 1
        await self._session.flush()
        return orm.attempt_count
```

## services\auth\auth\infrastructure\security\google_oauth.py

```python
"""Google id_token verifier for mobile SDK flow.

The mobile app uses Google Sign-In SDK to get an id_token,
then sends it to the backend for offline verification.
No server-side redirect or code exchange needed.
"""
from __future__ import annotations

import asyncio
import logging

from google.auth.transport import requests as google_requests
from google.oauth2 import id_token

from auth.domain.interfaces import GoogleTokenVerifierProtocol

logger = logging.getLogger("auth.security.google")


class GoogleTokenVerifier(GoogleTokenVerifierProtocol):
    """Verify Google id_tokens offline using google-auth library."""

    def __init__(self, client_id: str) -> None:
        self.client_id = client_id

    async def verify(self, token: str) -> dict:
        """Verify a Google id_token and return user claims.

        Returns dict with keys: sub, email, name, picture, email_verified.
        Raises ValueError if token is invalid or email not verified.
        """
        # google-auth is synchronous — wrap to avoid blocking event loop
        claims = await asyncio.to_thread(
            id_token.verify_oauth2_token,
            token,
            google_requests.Request(),
            self.client_id,
        )

        if not claims.get("email_verified", False):
            raise ValueError("Google email is not verified")

        logger.info(
            "Google token verified",
            extra={"sub": claims.get("sub"), "email": claims.get("email")},
        )

        return claims
```

## services\auth\auth\infrastructure\security\rate_limit.py

```python
"""OTP rate limiting via Redis.

Uses CacheManager.increment() (atomic Redis INCR) for distributed,
race-condition-free rate limiting.
"""
from __future__ import annotations

from sp.infrastructure.cache.manager import CacheManager

from auth.domain.exceptions import OTPRateLimitError


class OTPRateLimiter:
    """Per-phone send limiting and per-IP verify limiting."""

    SEND_NAMESPACE = "otp_send_limit"
    VERIFY_NAMESPACE = "otp_verify_limit"

    SEND_MAX_PER_PHONE = 3       # max 3 OTPs per phone per window
    SEND_WINDOW_SECONDS = 900    # 15-minute window
    VERIFY_MAX_PER_IP = 10       # max 10 verify attempts per IP per window
    VERIFY_WINDOW_SECONDS = 900  # 15-minute window

    def __init__(self, cache: CacheManager) -> None:
        self.cache = cache

    async def check_send_limit(self, phone: str) -> None:
        """Raise OTPRateLimitError if phone has exceeded send limit."""
        count = await self.cache.increment(
            self.SEND_NAMESPACE, phone, ttl=self.SEND_WINDOW_SECONDS
        )
        if count > self.SEND_MAX_PER_PHONE:
            raise OTPRateLimitError(
                f"Too many OTP requests. Try again in {self.SEND_WINDOW_SECONDS // 60} minutes."
            )

    async def check_verify_limit(self, ip_address: str) -> None:
        """Raise OTPRateLimitError if IP has exceeded verify limit."""
        count = await self.cache.increment(
            self.VERIFY_NAMESPACE, ip_address, ttl=self.VERIFY_WINDOW_SECONDS
        )
        if count > self.VERIFY_MAX_PER_IP:
            raise OTPRateLimitError(
                "Too many verification attempts. Try again later."
            )

```

## services\auth\auth\infrastructure\__init__.py

```python
"""Auth infrastructure layer — ORM models, repositories, DI providers."""

```

## services\auth\auth\main.py

```python
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

```

## services\auth\auth\__init__.py

```python
"""Auth service package."""

```

## services\auth\pyproject.toml

```toml
[project]
name = "auth"
version = "0.1.0"
description = "SafarPay Auth Service — authentication and user management"
requires-python = ">=3.10"
dependencies = [
    "sp",
    "fastapi>=0.111.0",
    "uvicorn[standard]>=0.30.0",
    "pydantic[email]>=2.7.0",
    "pywa",
    "google-auth>=2.29.0",
]

[tool.uv.sources]
sp = { workspace = true }

[tool.uv.build-backend]
module-root = "."

[build-system]
requires = ["uv_build>=0.11.7,<0.12.0"]
build-backend = "uv_build"
```

## libs\platform\src\sp\infrastructure\cache\manager.py

```python
"""Redis cache abstraction.

CacheManager is created once at service lifespan startup and stored on app.state.cache.
Done this way to prevent global singletons being initialised at import time.

Usage in routes:
    def get_cache(request: Request) -> CacheManager:
        return request.app.state.cache
"""
from __future__ import annotations

import json
import logging
from typing import Any

import redis.asyncio as aioredis

logger = logging.getLogger("platform.cache")


class CacheManager:
    """Namespace-prefixed Redis cache. Connects lazily via connect()."""

    def __init__(
        self,
        redis_url: str,
        app_name: str,
        pool_size: int = 10,
        default_ttl: int = 3600,
    ) -> None:
        self._redis_url = redis_url
        self._app_name = app_name
        self._pool_size = pool_size
        self._default_ttl = default_ttl
        self._redis: aioredis.Redis | None = None

    async def connect(self) -> None:
        """Open Redis connection pool. Call at lifespan startup."""
        self._redis = aioredis.from_url(
            self._redis_url,
            encoding="utf-8",
            decode_responses=True,
            max_connections=self._pool_size,
        )
        logger.info("Cache connected", extra={"url": self._redis_url})

    async def close(self) -> None:
        """Close Redis connection pool. Call at lifespan shutdown."""
        if self._redis:
            await self._redis.aclose()
            self._redis = None

    # ── Key helpers ───────────────────────────────────────────────────────────

    def _key(self, namespace: str, key: str) -> str:
        return f"{self._app_name}:{namespace}:{key}"

    def _assert_connected(self) -> aioredis.Redis:
        if self._redis is None:
            raise RuntimeError(
                "CacheManager is not connected. "
                "Ensure connect() is called at lifespan startup."
            )
        return self._redis

    # ── Public API ────────────────────────────────────────────────────────────

    async def get(self, namespace: str, key: str) -> Any | None:
        redis = self._assert_connected()
        raw = await redis.get(self._key(namespace, key))
        if raw is None:
            return None
        try:
            return json.loads(raw)
        except (json.JSONDecodeError, TypeError):
            return raw

    async def set(
        self,
        namespace: str,
        key: str,
        value: Any,
        ttl: int | None = None,
    ) -> bool:
        redis = self._assert_connected()
        try:
            serialized = json.dumps(value, default=str)
        except (TypeError, ValueError):
            serialized = str(value)
        return await redis.setex(
            self._key(namespace, key),
            ttl or self._default_ttl,
            serialized,
        )

    async def delete(self, namespace: str, key: str) -> bool:
        redis = self._assert_connected()
        return await redis.delete(self._key(namespace, key)) > 0

    async def increment(
        self,
        namespace: str,
        key: str,
        ttl: int | None = None,
    ) -> int:
        """Atomic Redis INCR. Safe for distributed rate limiting."""
        redis = self._assert_connected()
        full_key = self._key(namespace, key)
        value = await redis.incr(full_key)
        if value == 1 and ttl:
            await redis.expire(full_key, ttl)
        return value

    async def clear_namespace(self, namespace: str) -> int:
        redis = self._assert_connected()
        keys = await redis.keys(f"{self._app_name}:{namespace}:*")
        if keys:
            return await redis.delete(*keys)
        return 0


def get_cache_manager_factory(settings: Any) -> CacheManager:
    """Factory — create a CacheManager from settings. Call once at lifespan startup."""
    return CacheManager(
        redis_url=settings.REDIS_URL,
        app_name=settings.APP_NAME,
        pool_size=settings.REDIS_POOL_SIZE,
        default_ttl=settings.REDIS_DEFAULT_TTL,
    )

```

