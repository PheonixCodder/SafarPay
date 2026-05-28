"""Notification DI providers."""
from __future__ import annotations

from typing import Annotated

from fastapi import Depends, Request
from sp.infrastructure.messaging.publisher import EventPublisher
from sp.infrastructure.db.session import get_async_session
from sqlalchemy.ext.asyncio import AsyncSession

from ..application.use_cases import (
    GetUnreadCountUseCase,
    ListNotificationsUseCase,
    MarkAllNotificationsReadUseCase,
    MarkNotificationReadUseCase,
    RegisterDeviceTokenUseCase,
    SendNotificationUseCase,
    UnregisterDeviceTokenUseCase,
)
from .push_client import PushClient
from .repositories import DeviceTokenRepository, NotificationRepository


def get_publisher(request: Request) -> EventPublisher | None:
    return getattr(request.app.state, "publisher", None)


def get_notification_repo(
    session: Annotated[AsyncSession, Depends(get_async_session)],
) -> NotificationRepository:
    return NotificationRepository(session)


def get_device_token_repo(
    session: Annotated[AsyncSession, Depends(get_async_session)],
) -> DeviceTokenRepository:
    return DeviceTokenRepository(session)


def get_push_client(request: Request) -> PushClient | None:
    return getattr(request.app.state, "push_client", None)


def get_send_notification_uc(
    request: Request,
    repo: Annotated[NotificationRepository, Depends(get_notification_repo)],
    device_tokens: Annotated[DeviceTokenRepository, Depends(get_device_token_repo)],
) -> SendNotificationUseCase:
    return SendNotificationUseCase(
        repo,
        publisher=get_publisher(request),
        device_tokens=device_tokens,
        push_client=get_push_client(request),
    )


def get_list_notifications_uc(
    repo: Annotated[NotificationRepository, Depends(get_notification_repo)],
) -> ListNotificationsUseCase:
    return ListNotificationsUseCase(repo)


def get_unread_count_uc(
    repo: Annotated[NotificationRepository, Depends(get_notification_repo)],
) -> GetUnreadCountUseCase:
    return GetUnreadCountUseCase(repo)


def get_mark_read_uc(
    repo: Annotated[NotificationRepository, Depends(get_notification_repo)],
) -> MarkNotificationReadUseCase:
    return MarkNotificationReadUseCase(repo)


def get_mark_all_read_uc(
    repo: Annotated[NotificationRepository, Depends(get_notification_repo)],
) -> MarkAllNotificationsReadUseCase:
    return MarkAllNotificationsReadUseCase(repo)


def get_register_device_token_uc(
    repo: Annotated[DeviceTokenRepository, Depends(get_device_token_repo)],
) -> RegisterDeviceTokenUseCase:
    return RegisterDeviceTokenUseCase(repo)


def get_unregister_device_token_uc(
    repo: Annotated[DeviceTokenRepository, Depends(get_device_token_repo)],
) -> UnregisterDeviceTokenUseCase:
    return UnregisterDeviceTokenUseCase(repo)
