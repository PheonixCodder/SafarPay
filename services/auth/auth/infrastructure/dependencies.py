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
