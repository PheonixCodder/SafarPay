"""Notification application schemas."""
from __future__ import annotations

from datetime import datetime
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, Field, model_validator


class SendNotificationRequest(BaseModel):
    user_id: UUID | None = None
    recipient_id: UUID | None = None
    title: str = Field("SafarPay update", min_length=1, max_length=160)
    message: str | None = Field(None, min_length=1, max_length=1000)
    template: str | None = None
    context: dict[str, Any] = Field(default_factory=dict)
    type: Literal["trip", "payment", "offer", "safety", "system"] = "system"
    channel: Literal["email", "sms", "push"] = "push"
    metadata: dict[str, Any] = Field(default_factory=dict)
    source_service: str | None = None
    source_event_type: str | None = None
    source_event_id: str | None = None
    idempotency_key: str | None = None
    deeplink: str | None = None

    @model_validator(mode="after")
    def _recipient_required(self) -> SendNotificationRequest:
        if self.user_id is None and self.recipient_id is None:
            raise ValueError("user_id or recipient_id is required")
        if not self.message:
            self.message = _message_from_template(self.template, self.context)
        return self

    @property
    def resolved_user_id(self) -> UUID:
        return self.user_id or self.recipient_id  # type: ignore[return-value]


class RegisterDeviceTokenRequest(BaseModel):
    token: str = Field(..., min_length=10, max_length=512)
    platform: Literal["android", "ios", "web", "unknown"] = "unknown"
    driver_id: UUID | None = None
    device_id: str | None = Field(None, max_length=160)
    app_version: str | None = Field(None, max_length=80)


class UnregisterDeviceTokenRequest(BaseModel):
    token: str = Field(..., min_length=10, max_length=512)


class DeviceTokenResponse(BaseModel):
    id: UUID
    user_id: UUID
    token: str
    platform: str
    driver_id: UUID | None
    device_id: str | None
    app_version: str | None
    is_active: bool
    created_at: datetime
    last_seen_at: datetime


def _message_from_template(template: str | None, context: dict[str, Any]) -> str:
    if template == "ride_accepted":
        return "Your driver has accepted the ride."
    if template == "ride_started":
        return "Your ride is now in progress."
    if template == "ride_completed":
        return "Your ride has been completed."
    if template == "ride_cancelled":
        return "This ride was cancelled."
    ride_id = context.get("ride_id")
    if ride_id:
        return f"Ride update for {ride_id}."
    return "You have a new SafarPay update."


class NotificationResponse(BaseModel):
    id: UUID
    user_id: UUID
    type: str
    title: str
    message: str
    channel: str
    status: str
    metadata: dict[str, Any] = Field(default_factory=dict)
    source_service: str | None = None
    source_event_type: str | None = None
    source_event_id: str | None = None
    deeplink: str | None = None
    read_at: datetime | None = None
    created_at: datetime
    is_unread: bool


class NotificationListResponse(BaseModel):
    data: list[NotificationResponse]
    total: int
    unread_count: int


class NotificationUnreadCountResponse(BaseModel):
    unread_count: int
