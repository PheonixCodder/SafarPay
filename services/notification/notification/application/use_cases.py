"""Notification use case — publishes typed event to Kafka."""
from __future__ import annotations

import logging

from sp.infrastructure.messaging.events import NotificationRequestedEvent
from sp.infrastructure.messaging.publisher import EventPublisher

from ..domain.models import Notification, NotificationChannel
from .schemas import NotificationResponse, SendNotificationRequest

logger = logging.getLogger("notification.use_cases")


class SendNotificationUseCase:
    """Queues a notification by publishing a typed event.

    The actual delivery (email/SMS/push) is handled by
    a consumer subscribing to 'notification-events'.
    """

    def __init__(self, publisher: EventPublisher | None = None) -> None:
        self._publisher = publisher

    async def execute(self, req: SendNotificationRequest) -> NotificationResponse:
        notification = Notification.create(
            user_id=req.user_id,
            message=req.message,
            channel=NotificationChannel(req.channel),
        )

        if self._publisher:
            await self._publisher.publish(
                NotificationRequestedEvent(
                    payload={
                        "notification_id": str(notification.id),
                        "user_id": str(notification.user_id),
                        "message": notification.message,
                        "channel": notification.channel.value,
                    }
                )
            )
            logger.info(
                "Notification queued id=%s channel=%s",
                notification.id,
                notification.channel.value,
            )
        else:
            logger.warning(
                "No publisher configured. Notification not queued: %s", notification.id
            )

        return NotificationResponse(
            id=notification.id,
            user_id=notification.user_id,
            message=notification.message,
            channel=notification.channel.value,
            status=notification.status.value,
        )
