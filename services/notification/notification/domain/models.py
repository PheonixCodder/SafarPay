"""Notification domain models."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from uuid import UUID, uuid4


class NotificationChannel(str, Enum):
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"


class NotificationStatus(str, Enum):
    QUEUED = "queued"
    SENT = "sent"
    FAILED = "failed"


@dataclass
class Notification:
    id: UUID
    user_id: UUID
    message: str
    channel: NotificationChannel
    status: NotificationStatus
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @classmethod
    def create(
        cls,
        user_id: UUID,
        message: str,
        channel: NotificationChannel,
    ) -> Notification:
        return cls(
            id=uuid4(),
            user_id=user_id,
            message=message,
            channel=channel,
            status=NotificationStatus.QUEUED,
        )
