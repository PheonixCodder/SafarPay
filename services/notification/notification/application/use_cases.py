"""Notification use case — publishes typed event to Kafka."""
from __future__ import annotations

import logging
from typing import Any
from uuid import UUID

from sp.infrastructure.messaging.events import BaseEvent, NotificationRequestedEvent
from sp.infrastructure.messaging.publisher import EventPublisher

from ..domain.models import (
    DevicePlatform,
    DeviceToken,
    Notification,
    NotificationChannel,
    NotificationStatus,
    NotificationType,
)
from .schemas import (
    DeviceTokenResponse,
    NotificationListResponse,
    NotificationResponse,
    NotificationUnreadCountResponse,
    RegisterDeviceTokenRequest,
    SendNotificationRequest,
    UnregisterDeviceTokenRequest,
)

logger = logging.getLogger("notification.use_cases")


def _to_response(notification: Notification) -> NotificationResponse:
    return NotificationResponse(
        id=notification.id,
        user_id=notification.user_id,
        type=notification.type.value,
        title=notification.title,
        message=notification.message,
        channel=notification.channel.value,
        status=notification.status.value,
        metadata=notification.metadata,
        source_service=notification.source_service,
        source_event_type=notification.source_event_type,
        source_event_id=notification.source_event_id,
        deeplink=notification.deeplink,
        read_at=notification.read_at,
        created_at=notification.created_at,
        is_unread=notification.is_unread,
    )


def _device_to_response(token: DeviceToken) -> DeviceTokenResponse:
    return DeviceTokenResponse(
        id=token.id,
        user_id=token.user_id,
        token=token.token,
        platform=token.platform.value,
        driver_id=token.driver_id,
        device_id=token.device_id,
        app_version=token.app_version,
        is_active=token.is_active,
        created_at=token.created_at,
        last_seen_at=token.last_seen_at,
    )


class SendNotificationUseCase:
    """Queues a notification by publishing a typed event.

    The actual delivery (email/SMS/push) is handled by
    a consumer subscribing to 'notification-events'.
    """

    def __init__(
        self,
        repo: Any,
        publisher: EventPublisher | None = None,
        device_tokens: Any | None = None,
        push_client: Any | None = None,
    ) -> None:
        self._repo = repo
        self._publisher = publisher
        self._device_tokens = device_tokens
        self._push_client = push_client

    async def execute(self, req: SendNotificationRequest) -> NotificationResponse:
        notification = Notification.create(
            user_id=req.resolved_user_id,
            title=req.title,
            message=req.message or "You have a new SafarPay update.",
            channel=NotificationChannel(req.channel),
            type=NotificationType(req.type),
            metadata=req.metadata or req.context,
            source_service=req.source_service,
            source_event_type=req.source_event_type,
            source_event_id=req.source_event_id,
            idempotency_key=req.idempotency_key,
            deeplink=req.deeplink,
        )
        persisted = await self._repo.create(notification)

        if self._publisher:
            await self._publisher.publish(
                NotificationRequestedEvent(
                    payload={
                        "notification_id": str(persisted.id),
                        "recipient_id": str(persisted.user_id),
                        "user_id": str(persisted.user_id),
                        "title": persisted.title,
                        "message": notification.message,
                        "channel": notification.channel.value,
                        "type": notification.type.value,
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

        await _deliver_push_if_possible(
            persisted,
            self._device_tokens,
            self._push_client,
            self._repo,
        )
        return _to_response(persisted)


class ListNotificationsUseCase:
    def __init__(self, repo: Any) -> None:
        self._repo = repo

    async def execute(
        self,
        user_id: UUID,
        *,
        limit: int = 30,
        offset: int = 0,
        unread_only: bool = False,
    ) -> NotificationListResponse:
        items = await self._repo.list_for_user(
            user_id,
            limit=limit,
            offset=offset,
            unread_only=unread_only,
        )
        total = await self._repo.count_for_user(user_id, unread_only=unread_only)
        unread_count = await self._repo.unread_count(user_id)
        return NotificationListResponse(
            data=[_to_response(item) for item in items],
            total=total,
            unread_count=unread_count,
        )


class GetUnreadCountUseCase:
    def __init__(self, repo: Any) -> None:
        self._repo = repo

    async def execute(self, user_id: UUID) -> NotificationUnreadCountResponse:
        return NotificationUnreadCountResponse(
            unread_count=await self._repo.unread_count(user_id)
        )


class MarkNotificationReadUseCase:
    def __init__(self, repo: Any) -> None:
        self._repo = repo

    async def execute(self, user_id: UUID, notification_id: UUID) -> NotificationResponse:
        notification = await self._repo.mark_read(user_id, notification_id)
        return _to_response(notification)


class MarkAllNotificationsReadUseCase:
    def __init__(self, repo: Any) -> None:
        self._repo = repo

    async def execute(self, user_id: UUID) -> NotificationUnreadCountResponse:
        await self._repo.mark_all_read(user_id)
        return NotificationUnreadCountResponse(
            unread_count=await self._repo.unread_count(user_id)
        )


class RegisterDeviceTokenUseCase:
    def __init__(self, repo: Any) -> None:
        self._repo = repo

    async def execute(self, user_id: UUID, req: RegisterDeviceTokenRequest) -> DeviceTokenResponse:
        token = DeviceToken.register(
            user_id=user_id,
            token=req.token,
            platform=DevicePlatform(req.platform),
            driver_id=req.driver_id,
            device_id=req.device_id,
            app_version=req.app_version,
        )
        return _device_to_response(await self._repo.upsert(token))


class UnregisterDeviceTokenUseCase:
    def __init__(self, repo: Any) -> None:
        self._repo = repo

    async def execute(self, user_id: UUID, req: UnregisterDeviceTokenRequest) -> dict[str, bool]:
        await self._repo.deactivate(user_id, req.token)
        return {"ok": True}


class CreateNotificationFromEventUseCase:
    def __init__(self, repo: Any, device_tokens: Any | None = None, push_client: Any | None = None) -> None:
        self._repo = repo
        self._device_tokens = device_tokens
        self._push_client = push_client

    async def execute(self, event: BaseEvent) -> Notification | None:
        for request in _requests_from_event(event):
            notification = await self._repo.create(Notification.create(**request))
            await _deliver_push_if_possible(
                notification,
                self._device_tokens,
                self._push_client,
                self._repo,
            )
        return None


async def _deliver_push_if_possible(
    notification: Notification,
    device_tokens: Any | None,
    push_client: Any | None,
    notification_repo: Any | None = None,
) -> None:
    if device_tokens is None or push_client is None or notification.channel != NotificationChannel.PUSH:
        return
    tokens = await device_tokens.active_tokens_for_user(notification.user_id)
    if not tokens and notification.metadata.get("driver_id"):
        tokens = await device_tokens.active_tokens_for_driver(UUID(str(notification.metadata["driver_id"])))
    if not tokens:
        logger.warning(
            "No active device tokens for notification id=%s user_id=%s metadata=%s",
            notification.id,
            notification.user_id,
            notification.metadata,
        )
        await _mark_notification_status(notification, notification_repo, NotificationStatus.FAILED)
        return
    delivered = False
    for token in tokens:
        sent = await push_client.send_to_token(token.token, notification)
        if not sent and getattr(push_client, "last_error_code", "") == "UNREGISTERED":
            await device_tokens.deactivate(token.user_id, token.token)
        delivered = sent or delivered
    await _mark_notification_status(
        notification,
        notification_repo,
        NotificationStatus.SENT if delivered else NotificationStatus.FAILED,
    )


async def _mark_notification_status(
    notification: Notification,
    notification_repo: Any | None,
    status: NotificationStatus,
) -> None:
    if notification_repo is None or not hasattr(notification_repo, "update_status"):
        return
    await notification_repo.update_status(notification.id, status)


def _requests_from_event(event: BaseEvent) -> list[dict[str, Any]]:
    payload = event.payload or {}
    source = event.event_type
    event_id = str(event.event_id)
    base = {
        "channel": NotificationChannel.PUSH,
        "source_service": _source_service(source),
        "source_event_type": source,
        "source_event_id": event_id,
        "metadata": payload,
        "deeplink": _deeplink(payload, source),
    }

    def make(user_id: Any, title: str, message: str, type_: NotificationType) -> dict[str, Any] | None:
        if not user_id:
            return None
        return {
            **base,
            "user_id": UUID(str(user_id)),
            "title": title,
            "message": message,
            "type": type_,
            "idempotency_key": f"{source}:{event_id}:{user_id}",
        }

    if source == "bid.placed":
        item = make(
            payload.get("passenger_user_id") or payload.get("passenger_id") or payload.get("user_id"),
            "New driver offer",
            "A driver has sent an offer for your ride.",
            NotificationType.OFFER,
        )
        return [item] if item else []
    if source == "bid.accepted":
        items = [
            make(
                payload.get("passenger_user_id") or payload.get("passenger_id") or payload.get("user_id"),
                "Offer accepted",
                "Your selected driver has been assigned.",
                NotificationType.TRIP,
            ),
            make(
                payload.get("driver_user_id") or payload.get("driver_id"),
                "Ride confirmed",
                "The passenger accepted your offer.",
                NotificationType.OFFER,
            ),
        ]
        return [item for item in items if item]
    if source == "service.request.accepted":
        return [
            item
            for item in [
                make(
                    payload.get("passenger_user_id"),
                    "Driver assigned",
                    "Your driver is heading to pickup.",
                    NotificationType.TRIP,
                ),
                make(
                    payload.get("driver_user_id") or payload.get("driver_id"),
                    "Pickup assigned",
                    "You have a confirmed pickup.",
                    NotificationType.TRIP,
                ),
            ]
            if item
        ]
    if source == "service.request.started":
        item = make(
            payload.get("passenger_user_id") or payload.get("user_id"),
            "Trip started",
            "Your ride is now in progress.",
            NotificationType.TRIP,
        )
        return [item] if item else []
    if source == "service.request.completed":
        item = make(
            payload.get("passenger_user_id"),
            "Trip completed",
            "Your ride has been completed. Thanks for riding with SafarPay.",
            NotificationType.TRIP,
        )
        return [item] if item else []
    if source == "service.request.cancelled":
        item = make(
            payload.get("passenger_user_id"),
            "Ride cancelled",
            "This ride was cancelled.",
            NotificationType.TRIP,
        )
        return [item] if item else []
    if source in {
        "communication.message.sent",
        "communication.media_message.sent",
        "communication.message_sent",
        "communication.media_message_sent",
    }:
        item = make(
            payload.get("recipient_id"),
            "New ride message",
            "You received a new message for your ride.",
            NotificationType.SYSTEM,
        )
        return [item] if item else []
    if source in {"communication.call.started", "communication.call_started"}:
        item = make(
            payload.get("recipient_id"),
            "Incoming ride call",
            "Your ride contact is calling.",
            NotificationType.SYSTEM,
        )
        return [item] if item else []
    if source == "geofence.violation":
        item = make(
            payload.get("actor_user_id") or payload.get("actor_id"),
            "Safety alert",
            "A route safety boundary needs attention.",
            NotificationType.SAFETY,
        )
        return [item] if item else []
    return []


def _source_service(event_type: str) -> str:
    return event_type.split(".", 1)[0]


def _deeplink(payload: dict[str, Any], event_type: str = "") -> str | None:
    ride_id = payload.get("ride_id") or payload.get("service_request_id")
    if ride_id:
        if event_type.startswith("communication."):
            return f"safarpay://communication/rides/{ride_id}"
        return f"safarpay://rides/{ride_id}"
    return None
