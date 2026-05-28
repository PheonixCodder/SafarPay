"""Notification domain models."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from uuid import UUID, uuid4
from typing import Any


class NotificationChannel(str, Enum):
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"


class NotificationStatus(str, Enum):
    QUEUED = "queued"
    SENT = "sent"
    FAILED = "failed"


class NotificationType(str, Enum):
    TRIP = "trip"
    PAYMENT = "payment"
    OFFER = "offer"
    SAFETY = "safety"
    SYSTEM = "system"


class DevicePlatform(str, Enum):
    ANDROID = "android"
    IOS = "ios"
    WEB = "web"
    UNKNOWN = "unknown"


@dataclass
class Notification:
    id: UUID
    user_id: UUID
    type: NotificationType
    title: str
    message: str
    channel: NotificationChannel
    status: NotificationStatus
    metadata: dict[str, Any] = field(default_factory=dict)
    source_service: str | None = None
    source_event_type: str | None = None
    source_event_id: str | None = None
    idempotency_key: str | None = None
    deeplink: str | None = None
    read_at: datetime | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @property
    def is_unread(self) -> bool:
        return self.read_at is None

    @classmethod
    def create(
        cls,
        user_id: UUID,
        message: str,
        channel: NotificationChannel,
        title: str = "SafarPay update",
        type: NotificationType = NotificationType.SYSTEM,
        metadata: dict[str, Any] | None = None,
        source_service: str | None = None,
        source_event_type: str | None = None,
        source_event_id: str | None = None,
        idempotency_key: str | None = None,
        deeplink: str | None = None,
    ) -> Notification:
        return cls(
            id=uuid4(),
            user_id=user_id,
            type=type,
            title=title,
            message=message,
            channel=channel,
            status=NotificationStatus.QUEUED,
            metadata=metadata or {},
            source_service=source_service,
            source_event_type=source_event_type,
            source_event_id=source_event_id,
            idempotency_key=idempotency_key,
            deeplink=deeplink,
        )


@dataclass
class DeviceToken:
    id: UUID
    user_id: UUID
    token: str
    platform: DevicePlatform
    driver_id: UUID | None = None
    device_id: str | None = None
    app_version: str | None = None
    is_active: bool = True
    last_seen_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @classmethod
    def register(
        cls,
        *,
        user_id: UUID,
        token: str,
        platform: DevicePlatform,
        driver_id: UUID | None = None,
        device_id: str | None = None,
        app_version: str | None = None,
    ) -> DeviceToken:
        return cls(
            id=uuid4(),
            user_id=user_id,
            token=token,
            platform=platform,
            driver_id=driver_id,
            device_id=device_id,
            app_version=app_version,
        )
