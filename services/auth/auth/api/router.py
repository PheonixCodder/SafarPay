"""Auth API router — thin controllers, domain exceptions mapped to HTTP responses."""
from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sp.core.observability.logging import get_logger
from sp.infrastructure.security.dependencies import CurrentUser

from ..application.schemas import (
    LoginRequest,
    RegisterRequest,
    TokenResponse,
    UserResponse,
)
from ..application.use_cases import LoginUseCase, RegisterUserUseCase
from ..domain.exceptions import (
    InactiveUserError,
    InvalidCredentialsError,
    UserAlreadyExistsError,
)
from ..infrastructure.dependencies import get_login_use_case, get_register_use_case

router = APIRouter(tags=["auth"])
logger = get_logger("auth.api")


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user account",
)
async def register(
    req: RegisterRequest,
    use_case: Annotated[RegisterUserUseCase, Depends(get_register_use_case)],
) -> UserResponse:
    try:
        return await use_case.execute(req)
    except UserAlreadyExistsError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from None


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Authenticate and receive a JWT token",
)
async def login(
    req: LoginRequest,
    use_case: Annotated[LoginUseCase, Depends(get_login_use_case)],
) -> TokenResponse:
    try:
        return await use_case.execute(req)
    except (InvalidCredentialsError, InactiveUserError) as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
            headers={"WWW-Authenticate": "Bearer"},
        ) from None


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get authenticated user profile",
)
async def get_me(current_user: CurrentUser) -> UserResponse:
    """Requires a valid Bearer token — returns the authenticated user's profile."""
    return UserResponse(
        id=current_user.user_id,
        email=current_user.email,
        phone="",
        role=current_user.role,
        is_active=True,
        is_verified=False,
    )
