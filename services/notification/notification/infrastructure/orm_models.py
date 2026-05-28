from __future__ import annotations

import enum
import uuid
from datetime import datetime

from sp.infrastructure.db.base import Base, TimestampMixin
from sqlalchemy import Boolean, DateTime, Index, String, Text, UniqueConstraint
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PgUUID
from sqlalchemy.orm import Mapped, mapped_column


class NotificationChannelORM(enum.Enum):
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"


class NotificationStatusORM(enum.Enum):
    QUEUED = "queued"
    SENT = "sent"
    FAILED = "failed"


class NotificationTypeORM(enum.Enum):
    TRIP = "trip"
    PAYMENT = "payment"
    OFFER = "offer"
    SAFETY = "safety"
    SYSTEM = "system"


class DevicePlatformORM(enum.Enum):
    ANDROID = "android"
    IOS = "ios"
    WEB = "web"
    UNKNOWN = "unknown"


class NotificationORM(Base, TimestampMixin):
    __tablename__ = "notifications"
    __table_args__ = (
        UniqueConstraint("idempotency_key", name="uq_notifications_idempotency_key"),
        Index("ix_notifications_user_created", "user_id", "created_at"),
        Index("ix_notifications_user_read", "user_id", "read_at"),
        {"schema": "notification"},
    )

    id: Mapped[uuid.UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(PgUUID(as_uuid=True), nullable=False, index=True)
    type: Mapped[NotificationTypeORM] = mapped_column(SQLEnum(NotificationTypeORM, name="notification_type_enum", schema="notification"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(160), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    channel: Mapped[NotificationChannelORM] = mapped_column(SQLEnum(NotificationChannelORM, name="notification_channel_enum", schema="notification"), nullable=False, index=True)
    status: Mapped[NotificationStatusORM] = mapped_column(SQLEnum(NotificationStatusORM, name="notification_status_enum", schema="notification"), nullable=False, index=True)
    metadata_json: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    source_service: Mapped[str | None] = mapped_column(String(80), index=True)
    source_event_type: Mapped[str | None] = mapped_column(String(160), index=True)
    source_event_id: Mapped[str | None] = mapped_column(String(120), index=True)
    idempotency_key: Mapped[str | None] = mapped_column(String(220))
    deeplink: Mapped[str | None] = mapped_column(String(300))
    read_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), index=True)


class DeviceTokenORM(Base, TimestampMixin):
    __tablename__ = "device_tokens"
    __table_args__ = (
        UniqueConstraint("token", name="uq_device_tokens_token"),
        Index("ix_device_tokens_user_active", "user_id", "is_active"),
        {"schema": "notification"},
    )

    id: Mapped[uuid.UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(PgUUID(as_uuid=True), nullable=False, index=True)
    driver_id: Mapped[uuid.UUID | None] = mapped_column(PgUUID(as_uuid=True), index=True)
    token: Mapped[str] = mapped_column(String(512), nullable=False)
    platform: Mapped[DevicePlatformORM] = mapped_column(SQLEnum(DevicePlatformORM, name="device_platform_enum", schema="notification"), nullable=False)
    device_id: Mapped[str | None] = mapped_column(String(160), index=True)
    app_version: Mapped[str | None] = mapped_column(String(80))
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, index=True)
    last_seen_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), index=True)
