"""Async SQLAlchemy engine factory.

@lru_cache guarantees a single engine (and therefore a single connection pool)
per (db_url, pool_size) combination per process.
Creating a new engine on every request would exhaust Postgres connections immediately.
"""
from __future__ import annotations

from functools import lru_cache

from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine


@lru_cache(maxsize=4)
def get_db_engine(db_url: str, pool_size: int = 10) -> AsyncEngine:
    """Return a cached async engine for the given database URL.

    Args:
        db_url:    SQLAlchemy async connection string
                   (e.g. postgresql+psycopg://user:pass@host/db)
        pool_size: Base connection pool size (max_overflow is fixed at 20)
    """
    return create_async_engine(
        db_url,
        echo=False,
        pool_size=pool_size,
        max_overflow=20,
        pool_pre_ping=True,       # validates connections before use
        pool_recycle=3600,        # recycles connections every hour
    )
