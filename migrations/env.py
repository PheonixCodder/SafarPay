"""Alembic env.py — shared async migrations for all SafarPay services.

This file imports ALL ORM models (which register themselves in Base.metadata
by virtue of being imported), then runs async Alembic against a single engine.

Schema isolation is achieved via PostgreSQL schemas:
  auth.users, bidding.bids, verification.documents, geospatial.places
"""
from __future__ import annotations

import asyncio
import sys
from logging.config import fileConfig

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from alembic import context

# ── Import ALL ORM models to register them in Base.metadata ───────────────
# Each import has a side effect: it registers the ORM class with Base.metadata.
# Alembic discovers them through Base.metadata.sorted_tables.
from auth.infrastructure.orm_models import UserORM  # noqa: F401
from bidding.infrastructure.orm_models import BidORM  # noqa: F401
from geospatial.infrastructure.orm_models import PlaceORM  # noqa: F401

# ── Settings ───────────────────────────────────────────────────────────────
from sp.core.config import get_settings

# ── Load platform base (must be imported first) ────────────────────────────
from sp.infrastructure.db.base import Base  # noqa: F401
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import create_async_engine
from verification.infrastructure.orm_models import DocumentORM  # noqa: F401

settings = get_settings()

# Alembic Config object
config = context.config

# Interpret the config file for Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def get_url() -> str:
    """Prefer POSTGRES_DB_URI from settings over alembic.ini fallback."""
    return settings.POSTGRES_DB_URI


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode (SQL script generation)."""
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        include_schemas=True,
        version_table_schema="public",
    )
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection) -> None:
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        include_schemas=True,
        version_table_schema="public",
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """Run migrations in 'online' mode using async engine."""
    connectable = create_async_engine(
        get_url(),
        poolclass=pool.NullPool,  # NullPool: don't maintain connections during migration
    )
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()


def run_migrations_online() -> None:
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
