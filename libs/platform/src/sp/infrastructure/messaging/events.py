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


class VerificationReviewRequestedEvent(BaseEvent):
    event_type: Literal["verification.review_requested"] = "verification.review_requested"


# ── Ride / Service-Request events ─────────────────────────────────────────────

class ServiceRequestCreatedEvent(BaseEvent):
    event_type: Literal["service.request.created"] = "service.request.created"


class ServiceRequestUpdatedEvent(BaseEvent):
    event_type: Literal["service.request.updated"] = "service.request.updated"


class ServiceRequestCancelledEvent(BaseEvent):
    event_type: Literal["service.request.cancelled"] = "service.request.cancelled"


class ServiceRequestAcceptedEvent(BaseEvent):
    event_type: Literal["service.request.accepted"] = "service.request.accepted"


class ServiceRequestStartedEvent(BaseEvent):
    event_type: Literal["service.request.started"] = "service.request.started"


class ServiceRequestCompletedEvent(BaseEvent):
    event_type: Literal["service.request.completed"] = "service.request.completed"


class ServiceStopArrivedEvent(BaseEvent):
    event_type: Literal["service.stop.arrived"] = "service.stop.arrived"


class ServiceStopCompletedEvent(BaseEvent):
    event_type: Literal["service.stop.completed"] = "service.stop.completed"


class ServiceProofUploadedEvent(BaseEvent):
    event_type: Literal["service.proof.uploaded"] = "service.proof.uploaded"


class ServiceVerificationGeneratedEvent(BaseEvent):
    event_type: Literal["service.verification.generated"] = "service.verification.generated"


class ServiceVerificationVerifiedEvent(BaseEvent):
    event_type: Literal["service.verification.verified"] = "service.verification.verified"


class DriverMatchingRequestedEvent(BaseEvent):
    event_type: Literal["driver.matching.requested"] = "driver.matching.requested"


class DriverMatchingCompletedEvent(BaseEvent):
    event_type: Literal["driver.matching.completed"] = "driver.matching.completed"


class DriverAvailabilityUpdatedEvent(BaseEvent):
    event_type: Literal["driver.availability.updated"] = "driver.availability.updated"


class DriverLocationUpdatedEvent(BaseEvent):
    event_type: Literal["driver.location.updated"] = "driver.location.updated"
    # payload: {driver_id, lat, lng, speed_kmh, heading_degrees, accuracy_meters, ride_id, recorded_at}


class PassengerLocationUpdatedEvent(BaseEvent):
    """Published by Location Service when a passenger sends a GPS ping."""
    event_type: Literal["passenger.location.updated"] = "passenger.location.updated"
    # payload: {user_id, lat, lng, ride_id, recorded_at}


class DriverStatusChangedEvent(BaseEvent):
    """Published by Location Service when a driver goes ONLINE, OFFLINE, or ON_RIDE."""
    event_type: Literal["driver.status.changed"] = "driver.status.changed"
    # payload: {driver_id, status: ONLINE|OFFLINE|ON_RIDE, ride_id}


# ── Registry for deserialisation in subscriber ────────────────────────────────

EVENT_REGISTRY: dict[str, type[BaseEvent]] = {
    "user.registered": UserRegisteredEvent,
    "user.logged_in": UserLoggedInEvent,
    "bid.placed": BidPlacedEvent,
    "bid.accepted": BidAcceptedEvent,
    "notification.requested": NotificationRequestedEvent,
    "document.verified": DocumentVerifiedEvent,
    "verification.review_requested": VerificationReviewRequestedEvent,
    # Ride events
    "service.request.created": ServiceRequestCreatedEvent,
    "service.request.updated": ServiceRequestUpdatedEvent,
    "service.request.cancelled": ServiceRequestCancelledEvent,
    "service.request.accepted": ServiceRequestAcceptedEvent,
    "service.request.started": ServiceRequestStartedEvent,
    "service.request.completed": ServiceRequestCompletedEvent,
    "service.stop.arrived": ServiceStopArrivedEvent,
    "service.stop.completed": ServiceStopCompletedEvent,
    "service.proof.uploaded": ServiceProofUploadedEvent,
    "service.verification.generated": ServiceVerificationGeneratedEvent,
    "service.verification.verified": ServiceVerificationVerifiedEvent,
    "driver.matching.requested": DriverMatchingRequestedEvent,
    "driver.matching.completed": DriverMatchingCompletedEvent,
    "driver.availability.updated": DriverAvailabilityUpdatedEvent,
    "driver.location.updated": DriverLocationUpdatedEvent,
    "passenger.location.updated": PassengerLocationUpdatedEvent,
    "driver.status.changed": DriverStatusChangedEvent,
}
