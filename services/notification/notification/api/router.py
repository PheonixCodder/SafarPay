"""Notification API router."""
from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sp.infrastructure.security.dependencies import CurrentUser
from sp.infrastructure.security.permissions import Permission, require_role

from ..application.schemas import (
    DeviceTokenResponse,
    NotificationListResponse,
    NotificationResponse,
    NotificationUnreadCountResponse,
    RegisterDeviceTokenRequest,
    SendNotificationRequest,
    UnregisterDeviceTokenRequest,
)
from ..application.use_cases import (
    GetUnreadCountUseCase,
    ListNotificationsUseCase,
    MarkAllNotificationsReadUseCase,
    MarkNotificationReadUseCase,
    RegisterDeviceTokenUseCase,
    SendNotificationUseCase,
    UnregisterDeviceTokenUseCase,
)
from ..domain.models import Notification, NotificationChannel, NotificationStatus, NotificationType
from ..infrastructure.dependencies import (
    get_device_token_repo,
    get_list_notifications_uc,
    get_mark_all_read_uc,
    get_mark_read_uc,
    get_notification_repo,
    get_push_client,
    get_register_device_token_uc,
    get_send_notification_uc,
    get_unread_count_uc,
    get_unregister_device_token_uc,
)
from ..infrastructure.push_client import PushClient
from ..infrastructure.repositories import (
    DeviceTokenRepository,
    NotificationNotFoundError,
    NotificationRepository,
)

router = APIRouter(tags=["notification"])


@router.post(
    "/notifications",
    response_model=NotificationResponse,
    summary="Queue a notification for delivery",
    dependencies=[Depends(require_role(Permission.ADMIN, Permission.DRIVER))],
)
async def send_notification(
    req: SendNotificationRequest,
    use_case: Annotated[SendNotificationUseCase, Depends(get_send_notification_uc)],
) -> NotificationResponse:
    """Publish a notification event. Actual delivery is handled by consumers."""
    return await use_case.execute(req)


@router.post(
    "/device-tokens",
    response_model=DeviceTokenResponse,
    summary="Register this device for push notifications",
)
async def register_device_token(
    req: RegisterDeviceTokenRequest,
    current_user: CurrentUser,
    use_case: Annotated[RegisterDeviceTokenUseCase, Depends(get_register_device_token_uc)],
) -> DeviceTokenResponse:
    return await use_case.execute(current_user.user_id, req)


@router.post(
    "/device-tokens/unregister",
    response_model=dict,
    summary="Deactivate this device push token",
)
async def unregister_device_token(
    req: UnregisterDeviceTokenRequest,
    current_user: CurrentUser,
    use_case: Annotated[UnregisterDeviceTokenUseCase, Depends(get_unregister_device_token_uc)],
) -> dict[str, bool]:
    return await use_case.execute(current_user.user_id, req)


@router.post(
    "/internal/ride-jobs/{driver_id}",
    response_model=dict,
    summary="Internal ride job push dispatch endpoint",
)
async def dispatch_ride_job(
    driver_id: UUID,
    payload: dict,
    notifications: Annotated[NotificationRepository, Depends(get_notification_repo)],
    device_tokens: Annotated[DeviceTokenRepository, Depends(get_device_token_repo)],
    push_client: Annotated[PushClient | None, Depends(get_push_client)],
) -> dict[str, bool]:
    tokens = await device_tokens.active_tokens_for_driver(driver_id)
    title = str(payload.get("title") or "New ride request")
    message = str(payload.get("message") or "A passenger request is available near you.")
    ride_id = payload.get("ride_id") or payload.get("id") or payload.get("service_request_id")
    source_event = str(payload.get("alert_type") or "service.request.driver_job")
    metadata = {
        **payload,
        "notification_kind": payload.get("notification_kind") or "driver_ride_request",
        "present_as_driver_alert": True,
        "driver_id": str(driver_id),
        "ride_id": str(ride_id or ""),
    }
    recipients = {token.user_id: token for token in tokens}
    if not recipients and payload.get("driver_user_id"):
        recipients[UUID(str(payload["driver_user_id"]))] = None  # type: ignore[assignment]
    for user_id, token in recipients.items():
        notification = await notifications.create(Notification.create(
            user_id=user_id,
            title=title,
            message=message,
            channel=NotificationChannel.PUSH,
            type=NotificationType.TRIP,
            metadata=metadata,
            source_service="ride",
            source_event_type=source_event,
            source_event_id=str(ride_id or ""),
            idempotency_key=f"driver_job:{ride_id}:{driver_id}:{user_id}:{source_event}",
            deeplink=f"safarpay://driver/requests/{ride_id}",
        ))
        if push_client is not None and token is not None:
            delivered = await push_client.send_to_token(token.token, notification)
            if not delivered and getattr(push_client, "last_error_code", "") == "UNREGISTERED":
                await device_tokens.deactivate(token.user_id, token.token)
            if hasattr(notifications, "update_status"):
                await notifications.update_status(
                    notification.id,
                    NotificationStatus.SENT if delivered else NotificationStatus.FAILED,
                )
        elif hasattr(notifications, "update_status"):
            await notifications.update_status(notification.id, NotificationStatus.FAILED)
    return {"ok": True}


@router.get(
    "/notifications",
    response_model=NotificationListResponse,
    summary="List the authenticated user's notification inbox",
)
async def list_notifications(
    current_user: CurrentUser,
    use_case: Annotated[ListNotificationsUseCase, Depends(get_list_notifications_uc)],
    limit: int = Query(30, ge=1, le=100),
    offset: int = Query(0, ge=0),
    unread_only: bool = Query(False),
) -> NotificationListResponse:
    return await use_case.execute(
        current_user.user_id,
        limit=limit,
        offset=offset,
        unread_only=unread_only,
    )


@router.get(
    "/notifications/unread-count",
    response_model=NotificationUnreadCountResponse,
    summary="Get unread notification count",
)
async def unread_count(
    current_user: CurrentUser,
    use_case: Annotated[GetUnreadCountUseCase, Depends(get_unread_count_uc)],
) -> NotificationUnreadCountResponse:
    return await use_case.execute(current_user.user_id)


@router.post(
    "/notifications/read-all",
    response_model=NotificationUnreadCountResponse,
    summary="Mark all notifications as read",
)
async def mark_all_read(
    current_user: CurrentUser,
    use_case: Annotated[MarkAllNotificationsReadUseCase, Depends(get_mark_all_read_uc)],
) -> NotificationUnreadCountResponse:
    return await use_case.execute(current_user.user_id)


@router.post(
    "/notifications/{notification_id}/read",
    response_model=NotificationResponse,
    summary="Mark a notification as read",
)
async def mark_read(
    notification_id: UUID,
    current_user: CurrentUser,
    use_case: Annotated[MarkNotificationReadUseCase, Depends(get_mark_read_uc)],
) -> NotificationResponse:
    try:
        return await use_case.execute(current_user.user_id, notification_id)
    except NotificationNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found",
        ) from exc
