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

from pydantic import BaseModel, ConfigDict, Field, ValidationError


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


class EventPayload(BaseModel):
    """Base payload contract: known fields are enforced, extra fields are allowed."""

    model_config = ConfigDict(extra="allow")


class UserRegisteredPayload(EventPayload):
    user_id: UUID


class UserLoggedInPayload(EventPayload):
    user_id: UUID


class BidPlacedPayload(EventPayload):
    bid_id: UUID
    session_id: UUID
    driver_id: UUID


class BidAcceptedPayload(EventPayload):
    bid_id: UUID
    session_id: UUID
    ride_id: UUID
    driver_id: UUID


class BidUpdatedPayload(EventPayload):
    bid_id: UUID
    session_id: UUID
    driver_id: UUID


class BidWithdrawnPayload(EventPayload):
    bid_id: UUID
    session_id: UUID
    driver_id: UUID


class BidRejectedPayload(EventPayload):
    bid_id: UUID
    session_id: UUID


class BidAutoAcceptRequestedPayload(EventPayload):
    session_id: UUID
    bid_id: UUID
    passenger_id: UUID


class BidCounterOfferPayload(EventPayload):
    session_id: UUID
    counter_offer_id: UUID


class CommunicationConversationPayload(EventPayload):
    conversation_id: UUID


class CommunicationMessagePayload(EventPayload):
    message_id: UUID


class CommunicationMediaMessagePayload(EventPayload):
    message_id: UUID
    media_id: UUID


class CommunicationCallPayload(EventPayload):
    call_id: UUID


class NotificationRequestedPayload(EventPayload):
    recipient_id: UUID


class DocumentVerifiedPayload(EventPayload):
    document_id: UUID


class VerificationReviewRequestedPayload(EventPayload):
    user_id: UUID
    driver_id: UUID


class ServiceRequestCreatedPayload(EventPayload):
    ride_id: UUID
    passenger_user_id: UUID
    service_type: str
    pricing_mode: str


class ServiceRequestUpdatedPayload(EventPayload):
    ride_id: UUID


class ServiceRequestCancelledPayload(EventPayload):
    ride_id: UUID
    passenger_user_id: UUID


class ServiceRequestAcceptedPayload(EventPayload):
    ride_id: UUID
    passenger_user_id: UUID
    driver_id: UUID


class ServiceRequestStartedPayload(EventPayload):
    ride_id: UUID


class ServiceRequestCompletedPayload(EventPayload):
    ride_id: UUID
    passenger_user_id: UUID


class ServiceStopPayload(EventPayload):
    ride_id: UUID
    stop_id: UUID


class ServiceProofUploadedPayload(EventPayload):
    ride_id: UUID
    proof_id: UUID
    proof_type: str


class ServiceVerificationPayload(EventPayload):
    ride_id: UUID
    code_id: UUID


class DriverMatchingRequestedPayload(EventPayload):
    candidate_count: int


class DriverMatchingCompletedPayload(EventPayload):
    ride_id: UUID
    dispatched_to: int


class DriverAvailabilityUpdatedPayload(EventPayload):
    driver_id: UUID


class DriverLocationUpdatedPayload(EventPayload):
    driver_id: UUID
    lat: float
    lng: float


class PassengerLocationUpdatedPayload(EventPayload):
    user_id: UUID
    lat: float
    lng: float


class DriverStatusChangedPayload(EventPayload):
    driver_id: UUID
    status: str


class GeofenceViolationPayload(EventPayload):
    actor_id: UUID
    actor_role: str
    zone_id: UUID
    zone_type: str
    lat: float
    lng: float


class WebhookFailedPayload(EventPayload):
    original_payload: dict[str, Any]
    error: str
    retry_count: int


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


class BidUpdatedEvent(BaseEvent):
    event_type: Literal["bid.updated"] = "bid.updated"


class BidWithdrawnEvent(BaseEvent):
    event_type: Literal["bid.withdrawn"] = "bid.withdrawn"


class BidRejectedEvent(BaseEvent):
    event_type: Literal["bid.rejected"] = "bid.rejected"


class BidAutoAcceptRequestedEvent(BaseEvent):
    event_type: Literal["bid.auto_accept_requested"] = "bid.auto_accept_requested"


class BidCounterOfferCreatedEvent(BaseEvent):
    event_type: Literal["bid.counter_offer.created"] = "bid.counter_offer.created"


class BidCounterOfferRespondedEvent(BaseEvent):
    event_type: Literal["bid.counter_offer.responded"] = "bid.counter_offer.responded"


# Communication events

class CommunicationConversationOpenedEvent(BaseEvent):
    event_type: Literal["communication.conversation.opened"] = "communication.conversation.opened"


class CommunicationConversationClosedEvent(BaseEvent):
    event_type: Literal["communication.conversation.closed"] = "communication.conversation.closed"


class CommunicationMessageSentEvent(BaseEvent):
    event_type: Literal["communication.message.sent"] = "communication.message.sent"


class CommunicationMediaMessageSentEvent(BaseEvent):
    event_type: Literal["communication.media_message.sent"] = "communication.media_message.sent"


class CommunicationCallStartedEvent(BaseEvent):
    event_type: Literal["communication.call.started"] = "communication.call.started"


class CommunicationCallUpdatedEvent(BaseEvent):
    event_type: Literal["communication.call.updated"] = "communication.call.updated"


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


class GeofenceViolationEvent(BaseEvent):
    """Published by Geospatial Service when a driver/passenger violates a restricted zone."""
    event_type: Literal["geofence.violation"] = "geofence.violation"
    # payload: {actor_id, actor_role, zone_id, zone_type, lat, lng, recorded_at}


class WebhookFailedEvent(BaseEvent):
    event_type: Literal["webhook.failed"] = "webhook.failed"


# ── Registry for deserialisation in subscriber ────────────────────────────────

EVENT_REGISTRY: dict[str, type[BaseEvent]] = {
    "user.registered": UserRegisteredEvent,
    "user.logged_in": UserLoggedInEvent,
    "bid.placed": BidPlacedEvent,
    "bid.accepted": BidAcceptedEvent,
    "bid.updated": BidUpdatedEvent,
    "bid.withdrawn": BidWithdrawnEvent,
    "bid.rejected": BidRejectedEvent,
    "bid.auto_accept_requested": BidAutoAcceptRequestedEvent,
    "bid.counter_offer.created": BidCounterOfferCreatedEvent,
    "bid.counter_offer.responded": BidCounterOfferRespondedEvent,
    "communication.conversation.opened": CommunicationConversationOpenedEvent,
    "communication.conversation.closed": CommunicationConversationClosedEvent,
    "communication.message.sent": CommunicationMessageSentEvent,
    "communication.media_message.sent": CommunicationMediaMessageSentEvent,
    "communication.call.started": CommunicationCallStartedEvent,
    "communication.call.updated": CommunicationCallUpdatedEvent,
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
    "geofence.violation": GeofenceViolationEvent,
    "webhook.failed": WebhookFailedEvent,
}


PAYLOAD_REGISTRY: dict[str, type[EventPayload]] = {
    "user.registered": UserRegisteredPayload,
    "user.logged_in": UserLoggedInPayload,
    "bid.placed": BidPlacedPayload,
    "bid.accepted": BidAcceptedPayload,
    "bid.updated": BidUpdatedPayload,
    "bid.withdrawn": BidWithdrawnPayload,
    "bid.rejected": BidRejectedPayload,
    "bid.auto_accept_requested": BidAutoAcceptRequestedPayload,
    "bid.counter_offer.created": BidCounterOfferPayload,
    "bid.counter_offer.responded": BidCounterOfferPayload,
    "communication.conversation.opened": CommunicationConversationPayload,
    "communication.conversation.closed": CommunicationConversationPayload,
    "communication.message.sent": CommunicationMessagePayload,
    "communication.media_message.sent": CommunicationMediaMessagePayload,
    "communication.call.started": CommunicationCallPayload,
    "communication.call.updated": CommunicationCallPayload,
    "notification.requested": NotificationRequestedPayload,
    "document.verified": DocumentVerifiedPayload,
    "verification.review_requested": VerificationReviewRequestedPayload,
    "service.request.created": ServiceRequestCreatedPayload,
    "service.request.updated": ServiceRequestUpdatedPayload,
    "service.request.cancelled": ServiceRequestCancelledPayload,
    "service.request.accepted": ServiceRequestAcceptedPayload,
    "service.request.started": ServiceRequestStartedPayload,
    "service.request.completed": ServiceRequestCompletedPayload,
    "service.stop.arrived": ServiceStopPayload,
    "service.stop.completed": ServiceStopPayload,
    "service.proof.uploaded": ServiceProofUploadedPayload,
    "service.verification.generated": ServiceVerificationPayload,
    "service.verification.verified": ServiceVerificationPayload,
    "driver.matching.requested": DriverMatchingRequestedPayload,
    "driver.matching.completed": DriverMatchingCompletedPayload,
    "driver.availability.updated": DriverAvailabilityUpdatedPayload,
    "driver.location.updated": DriverLocationUpdatedPayload,
    "passenger.location.updated": PassengerLocationUpdatedPayload,
    "driver.status.changed": DriverStatusChangedPayload,
    "geofence.violation": GeofenceViolationPayload,
    "webhook.failed": WebhookFailedPayload,
}


class EventPayloadValidationError(ValueError):
    """Raised when a known event has an invalid payload contract."""


def validate_event_payload(event: BaseEvent) -> None:
    """Validate the payload for known event types.

    Unknown event types are allowed for forward compatibility, but known events
    must carry the payload fields their consumers rely on.
    """
    payload_model = PAYLOAD_REGISTRY.get(event.event_type)
    if not payload_model:
        return
    try:
        payload_model.model_validate(event.payload)
    except ValidationError as exc:
        raise EventPayloadValidationError(
            f"Invalid payload for event_type={event.event_type}: {exc}"
        ) from exc
