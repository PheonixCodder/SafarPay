"""Notification API router."""
from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends
from sp.infrastructure.security.permissions import Permission, require_role

from ..application.schemas import NotificationResponse, SendNotificationRequest
from ..application.use_cases import SendNotificationUseCase
from ..infrastructure.dependencies import get_send_notification_uc

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
