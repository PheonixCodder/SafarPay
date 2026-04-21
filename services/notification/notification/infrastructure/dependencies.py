"""Notification DI providers."""
from __future__ import annotations

from fastapi import Request
from sp.infrastructure.messaging.publisher import EventPublisher

from ..application.use_cases import SendNotificationUseCase


def get_publisher(request: Request) -> EventPublisher | None:
    return getattr(request.app.state, "publisher", None)


def get_send_notification_uc(request: Request) -> SendNotificationUseCase:
    return SendNotificationUseCase(publisher=get_publisher(request))
