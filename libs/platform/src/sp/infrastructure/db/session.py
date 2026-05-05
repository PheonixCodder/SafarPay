"""FastAPI-compatible async session dependency provider.

Sessions are never committed inside this provider — business logic
in use cases owns transaction boundaries via explicit session.commit().
The provider only rolls back on exception and always closes the session.
"""
from __future__ import annotations

import logging
from collections.abc import AsyncGenerator, Awaitable, Callable
from functools import lru_cache
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from sp.core.config import Settings, get_settings

from .engine import get_db_engine

logger = logging.getLogger("platform.db.session")
PostCommitHook = Callable[[], Awaitable[None]]
_POST_COMMIT_HOOKS_KEY = "post_commit_hooks"


def register_post_commit_hook(
    session: AsyncSession,
    hook: PostCommitHook,
) -> None:
    """Register an async side effect to run only after this session commits."""
    hooks = session.info.setdefault(_POST_COMMIT_HOOKS_KEY, [])
    hooks.append(hook)


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
            hooks = list(session.info.pop(_POST_COMMIT_HOOKS_KEY, []))
            for hook in hooks:
                try:
                    await hook()
                except Exception:
                    logger.exception("Post-commit hook failed")
        except Exception:
            session.info.pop(_POST_COMMIT_HOOKS_KEY, None)
            await session.rollback()
            raise
