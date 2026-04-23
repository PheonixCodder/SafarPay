"""FastAPI-compatible async session dependency provider.

Sessions are never committed inside this provider — business logic
in use cases owns transaction boundaries via explicit session.commit().
The provider only rolls back on exception and always closes the session.
"""
from __future__ import annotations

from collections.abc import AsyncGenerator
from functools import lru_cache
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from sp.core.config import Settings, get_settings

from .engine import get_db_engine


@lru_cache
def get_session_factory(settings: Settings) -> async_sessionmaker[AsyncSession]:
    """Create a session factory bound to the cached engine."""
    engine = get_db_engine(settings.POSTGRES_DB_URI, settings.POSTGRES_POOL_SIZE)
    return async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )


async def get_async_session(
    settings: Annotated[Settings, Depends(get_settings)],
) -> AsyncGenerator[AsyncSession, None]:
    """FastAPI Depends provider that yields a managed AsyncSession.

    - Auto-commits on successful request completion
    - Auto-rollback on any exception
    - Session is always closed in finally
    """
    factory = get_session_factory(settings)
    async with factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
