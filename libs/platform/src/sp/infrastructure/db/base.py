"""SQLAlchemy declarative base and common column mixins.

The single Base instance is imported by ALL service ORM models.
This ensures Alembic can discover every model through Base.metadata.
"""
from __future__ import annotations

from datetime import datetime

from sqlalchemy import func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Canonical SQLAlchemy declarative base.

    Every service ORM model must extend this — never create a second Base.
    All models are registered in Base.metadata and discovered by Alembic.
    """


class TimestampMixin:
    """Adds server-managed created_at and updated_at to any model."""

    created_at: Mapped[datetime] = mapped_column(
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
