"""Notification service HTTP adapter.

Sends push/SMS notifications via the SafarPay notification microservice.
Failure is logged but never raises — notification delivery is best-effort.
"""
from __future__ import annotations

import logging
from typing import Any
from uuid import UUID

import httpx

logger = logging.getLogger("ride.notification")

# TODO implement notification client
class NotificationClient:
    """HTTP adapter to the SafarPay notification service."""

    def __init__(self, base_url: str, *, timeout: float = 6.0) -> None:
        self._base_url = base_url.rstrip("/")
        self._client: httpx.AsyncClient | None = None

    async def start(self) -> None:
        self._client = httpx.AsyncClient(
            base_url=self._base_url,
            timeout=httpx.Timeout(6.0),
            headers={"Content-Type": "application/json", "Accept": "application/json"},
        )

    async def close(self) -> None:
        if self._client:
            await self._client.aclose()
            self._client = None


    async def send_ride_notification(
        self,
        recipient_id: UUID,
        template: str,
        context: dict[str, Any],
    ) -> bool:
        if not self._client:
            logger.error("NotificationClient not started")
            return False
        try:
            resp = await self._client.post(
                "/api/v1/notifications",
                json={
                    "recipient_id": str(recipient_id),
                    "template": template,
                    "context": context,
                },
            )
            if resp.status_code >= 300:
                logger.warning(
                    "Notification failed recipient=%s template=%s status=%d",
                    recipient_id, template, resp.status_code,
                )
                return False
            return True
        except httpx.HTTPError as exc:
            logger.error("NotificationClient error: %s", exc)
            return False


class NullNotificationClient:
    """No-op fallback when notification service is not configured."""

    async def start(self) -> None:
        pass

    async def close(self) -> None:
        pass

    async def send_ride_notification(
        self,
        recipient_id: UUID,
        template: str,
        context: dict[str, Any],
    ) -> bool:
        logger.warning("NullNotificationClient: notification not sent template=%s", template)
        return False
