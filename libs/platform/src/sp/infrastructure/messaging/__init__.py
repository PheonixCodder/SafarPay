"""Messaging — typed events, Kafka wrappers, publisher, subscriber."""

from .events import (
    BaseEvent,
    BidAcceptedEvent,
    BidPlacedEvent,
    DocumentVerifiedEvent,
    NotificationRequestedEvent,
    UserLoggedInEvent,
    UserRegisteredEvent,
)
from .inbox import message_event_id, process_inbox_message
from .outbox import GenericOutboxWorker
from .publisher import EventPublisher
from .subscriber import EventSubscriber

__all__ = [
    "BaseEvent",
    "UserRegisteredEvent",
    "UserLoggedInEvent",
    "BidPlacedEvent",
    "BidAcceptedEvent",
    "NotificationRequestedEvent",
    "DocumentVerifiedEvent",
    "EventPublisher",
    "EventSubscriber",
    "GenericOutboxWorker",
    "message_event_id",
    "process_inbox_message",
]
