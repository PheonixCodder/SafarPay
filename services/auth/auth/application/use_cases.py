"""Auth use cases — all business logic lives here, not in API routes.

Use cases receive dependencies via constructor injection.
They are instantiated by provider functions in infrastructure/dependencies.py.
"""
from __future__ import annotations

import logging

import bcrypt
from sp.core.config import Settings
from sp.infrastructure.messaging.events import UserLoggedInEvent, UserRegisteredEvent
from sp.infrastructure.messaging.publisher import EventPublisher
from sp.infrastructure.security.jwt import create_access_token

from ..domain.exceptions import (
    InactiveUserError,
    InvalidCredentialsError,
    UserAlreadyExistsError,
)
from ..domain.interfaces import UserRepositoryProtocol
from ..domain.models import User, UserRole
from .schemas import LoginRequest, RegisterRequest, TokenResponse, UserResponse

logger = logging.getLogger("auth.use_cases")


class RegisterUserUseCase:
    """Register a new user account."""

    def __init__(
        self,
        repo: UserRepositoryProtocol,
        settings: Settings,
        publisher: EventPublisher | None = None,
    ) -> None:
        self._repo = repo
        self._settings = settings
        self._publisher = publisher

    async def execute(self, req: RegisterRequest) -> UserResponse:
        if await self._repo.exists_by_email(req.email):
            raise UserAlreadyExistsError(f"Email already registered: {req.email}")

        hashed = bcrypt.hashpw(req.password.encode(), bcrypt.gensalt()).decode()
        user = User.create(
            email=req.email,
            phone=req.phone,
            role=UserRole(req.role),
            hashed_password=hashed,
        )
        saved = await self._repo.save(user)

        if self._publisher:
            await self._publisher.publish(
                UserRegisteredEvent(
                    payload={"user_id": str(saved.id), "email": saved.email}
                )
            )

        logger.info("User registered email=%s role=%s", saved.email, saved.role.value)
        return _to_response(saved)


class LoginUseCase:
    """Authenticate a user and issue a JWT access token."""

    def __init__(
        self,
        repo: UserRepositoryProtocol,
        settings: Settings,
        publisher: EventPublisher | None = None,
    ) -> None:
        self._repo = repo
        self._settings = settings
        self._publisher = publisher

    async def execute(self, req: LoginRequest) -> TokenResponse:
        user = await self._repo.find_by_email(req.email)
        if not user:
            raise InvalidCredentialsError("Invalid email or password")
        if not user.is_active:
            raise InactiveUserError("Account is inactive")
        if not bcrypt.checkpw(req.password.encode(), user.hashed_password.encode()):
            raise InvalidCredentialsError("Invalid email or password")

        token = create_access_token(
            user_id=user.id,
            email=user.email,
            role=user.role.value,
            secret=self._settings.JWT_SECRET,
            algorithm=self._settings.JWT_ALGORITHM,
            expiration_hours=self._settings.JWT_EXPIRATION_HOURS,
        )

        if self._publisher:
            await self._publisher.publish(
                UserLoggedInEvent(payload={"user_id": str(user.id)})
            )

        logger.info("User logged in email=%s", user.email)
        return TokenResponse(
            access_token=token,
            expires_in=self._settings.JWT_EXPIRATION_HOURS * 3600,
        )


# ── Helpers ───────────────────────────────────────────────────────────────────

def _to_response(user: User) -> UserResponse:
    return UserResponse(
        id=user.id,
        email=user.email,
        phone=user.phone,
        role=user.role.value,
        is_active=user.is_active,
        is_verified=user.is_verified,
    )
