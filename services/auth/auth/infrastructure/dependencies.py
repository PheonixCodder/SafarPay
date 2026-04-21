"""Auth DI provider functions — bridge FastAPI Depends with constructor-injected use cases.

Rule: FastAPI Depends() is used here and in api/.
      Constructor injection is used inside use_cases.py.
"""
from __future__ import annotations

from typing import Annotated

from fastapi import Depends, Request
from sp.core.config import Settings, get_settings
from sp.infrastructure.cache.manager import CacheManager
from sp.infrastructure.db.session import get_async_session
from sp.infrastructure.messaging.publisher import EventPublisher
from sqlalchemy.ext.asyncio import AsyncSession

from ..application.use_cases import LoginUseCase, RegisterUserUseCase
from ..domain.interfaces import UserRepositoryProtocol
from .repositories import UserRepository

# ── Infrastructure providers ──────────────────────────────────────────────────

def get_user_repo(
    session: Annotated[AsyncSession, Depends(get_async_session)],
) -> UserRepositoryProtocol:
    return UserRepository(session)


def get_cache(request: Request) -> CacheManager:
    return request.app.state.cache


def get_publisher(request: Request) -> EventPublisher | None:
    return getattr(request.app.state, "publisher", None)


# ── Use case providers ────────────────────────────────────────────────────────

def get_register_use_case(
    repo: Annotated[UserRepositoryProtocol, Depends(get_user_repo)],
    settings: Annotated[Settings, Depends(get_settings)],
    request: Request,
) -> RegisterUserUseCase:
    return RegisterUserUseCase(repo=repo, settings=settings, publisher=get_publisher(request))


def get_login_use_case(
    repo: Annotated[UserRepositoryProtocol, Depends(get_user_repo)],
    settings: Annotated[Settings, Depends(get_settings)],
    request: Request,
) -> LoginUseCase:
    return LoginUseCase(repo=repo, settings=settings, publisher=get_publisher(request))
