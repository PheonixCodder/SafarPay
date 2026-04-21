"""Notification application schemas."""
from __future__ import annotations

from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field


class SendNotificationRequest(BaseModel):
    user_id: UUID
    message: str = Field(..., min_length=1, max_length=1000)
    channel: Literal["email", "sms", "push"] = "push"


class NotificationResponse(BaseModel):
    id: UUID
    user_id: UUID
    message: str
    channel: str
    status: str
