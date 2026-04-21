"""Typed domain event schemas for the SafarPay event bus.

All events extend BaseEvent which enforces:
- Unique event_id (UUID4) for deduplication
- event_type for routing to correct handler
- version for schema evolution
- idempotency_key to prevent duplicate processing
- correlation_id for distributed tracing
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Literal
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class BaseEvent(BaseModel):
    """Base for all SafarPay domain events."""

    event_id: UUID = Field(default_factory=uuid4)
    event_type: str
    version: int = 1
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    idempotency_key: str = Field(default_factory=lambda: str(uuid4()))
    correlation_id: str | None = None
    payload: dict[str, Any] = Field(default_factory=dict)


# ── Auth events ───────────────────────────────────────────────────────────────

class UserRegisteredEvent(BaseEvent):
    event_type: Literal["user.registered"] = "user.registered"


class UserLoggedInEvent(BaseEvent):
    event_type: Literal["user.logged_in"] = "user.logged_in"


# ── Bidding events ────────────────────────────────────────────────────────────

class BidPlacedEvent(BaseEvent):
    event_type: Literal["bid.placed"] = "bid.placed"


class BidAcceptedEvent(BaseEvent):
    event_type: Literal["bid.accepted"] = "bid.accepted"


# ── Notification events ───────────────────────────────────────────────────────

class NotificationRequestedEvent(BaseEvent):
    event_type: Literal["notification.requested"] = "notification.requested"


# ── Verification events ───────────────────────────────────────────────────────

class DocumentVerifiedEvent(BaseEvent):
    event_type: Literal["document.verified"] = "document.verified"


# ── Registry for deserialisation in subscriber ────────────────────────────────

EVENT_REGISTRY: dict[str, type[BaseEvent]] = {
    "user.registered": UserRegisteredEvent,
    "user.logged_in": UserLoggedInEvent,
    "bid.placed": BidPlacedEvent,
    "bid.accepted": BidAcceptedEvent,
    "notification.requested": NotificationRequestedEvent,
    "document.verified": DocumentVerifiedEvent,
}
