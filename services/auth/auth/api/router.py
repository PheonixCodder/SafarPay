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
        profile_img=user.profile_img,
        is_active=user.is_active,
        is_verified=user.is_verified,
        is_onboarded=bool(user.phone and user.full_name),
    )