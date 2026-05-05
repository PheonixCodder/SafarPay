"""Auth ORM models — SQLAlchemy only, no business logic.

All auth tables live in the 'auth' PostgreSQL schema.
The single Base from platform ensures Alembic discovers these models.
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sp.infrastructure.db.base import Base, TimestampMixin
from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PgUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship


class UserORM(Base, TimestampMixin):
    """The central profile connecting identities."""

    __tablename__ = "users"
    __table_args__ = {"schema": "auth"}

    id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    full_name: Mapped[str | None] = mapped_column(String(255))
    email: Mapped[str | None] = mapped_column(String(255), unique=True, index=True)
    phone: Mapped[str | None] = mapped_column(String(20), unique=True, index=True)
    profile_img: Mapped[str | None] = mapped_column(String(500))
    role: Mapped[str] = mapped_column(String(20), default="passenger")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)

    # Relationships
    accounts: Mapped[list[AccountORM]] = relationship(back_populates="user", cascade="all, delete-orphan")
    sessions: Mapped[list[SessionORM]] = relationship(back_populates="user", cascade="all, delete-orphan")


class AccountORM(Base, TimestampMixin):
    """The OAuth bridge (e.g., Google login)."""

    __tablename__ = "accounts"
    __table_args__ = (
        UniqueConstraint("provider", "provider_account_id", name="uq_provider_account"),
        {"schema": "auth"}
    )

    id: Mapped[uuid.UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("auth.users.id", ondelete="CASCADE"))

    provider: Mapped[str] = mapped_column(String(50))  # e.g., "google"
    provider_account_id: Mapped[str] = mapped_column(String(255))  # Google's sub ID

    user: Mapped[UserORM] = relationship(back_populates="accounts")


class SessionORM(Base, TimestampMixin):
    """The active device tracker with Refresh Token Rotation."""

    __tablename__ = "sessions"
    __table_args__ = {"schema": "auth"}

    id: Mapped[uuid.UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("auth.users.id", ondelete="CASCADE"))

    refresh_token_hash: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    is_revoked: Mapped[bool] = mapped_column(Boolean, default=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    # Metadata for Device Management UI
    user_agent: Mapped[str | None] = mapped_column(Text)
    ip_address: Mapped[str | None] = mapped_column(String(45))
    last_active_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )

    user: Mapped[UserORM] = relationship(back_populates="sessions")


class VerificationORM(Base, TimestampMixin):
    """Temporary storage for WhatsApp OTPs."""

    __tablename__ = "verifications"
    __table_args__ = {"schema": "auth"}

    id: Mapped[uuid.UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    identifier: Mapped[str] = mapped_column(String(255), index=True)  # phone number or email
    code_hash: Mapped[str] = mapped_column(String(255))
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    attempt_count: Mapped[int] = mapped_column(Integer, default=0)


class AuthOutboxEventORM(Base, TimestampMixin):
    __tablename__ = "outbox_events"
    __table_args__ = (
        Index(
            "ix_auth_outbox_pending",
            "processed_at",
            "created_at",
            postgresql_where=text("processed_at IS NULL AND error_count < 5"),
        ),
        {"schema": "auth"},
    )

    id: Mapped[uuid.UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    event_type: Mapped[str] = mapped_column(String(160), nullable=False, index=True)
    aggregate_id: Mapped[str | None] = mapped_column(String(120), index=True)
    aggregate_type: Mapped[str | None] = mapped_column(String(80))
    topic: Mapped[str] = mapped_column(String(160), nullable=False, default="auth-events")
    payload: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    correlation_id: Mapped[str | None] = mapped_column(String(120))
    idempotency_key: Mapped[str | None] = mapped_column(String(180), unique=True)
    processed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    error_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    last_error: Mapped[str | None] = mapped_column(Text)
