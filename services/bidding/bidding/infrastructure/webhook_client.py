"""Webhook client for dispatching bidding opportunities to drivers."""
from __future__ import annotations
import asyncio
import json
import logging
from typing import Any
from uuid import UUID
from sp.infrastructure.messaging.publisher import EventPublisher
import httpx

from ..domain.interfaces import WebhookClientProtocol

logger = logging.getLogger("bidding.webhook")


# ** TODO ** // Fix the internal routes **
class WebhookClient(WebhookClientProtocol):
    """HTTP adapter for notifying driver apps of new bids and session updates."""

    def __init__(self, base_url: str, publisher: EventPublisher | None = None) -> None:
        self._base_url = base_url.rstrip("/")
        self._timeout = 5.0
        self._client: httpx.AsyncClient | None = None
        self._publisher = publisher

    async def start(self) -> None:
        self._client = httpx.AsyncClient(
            base_url=self._base_url,
            timeout=httpx.Timeout(self._timeout),
            headers={"Content-Type": "application/json", "Accept": "application/json"},
        )

    async def close(self) -> None:
        if self._client:
            await self._client.aclose()
            self._client = None

    async def dispatch_bidding_opportunity(
        self,
        driver_id: UUID,
        session_id: UUID,
        ride_payload: dict[str, Any],
        *,
        idempotency_key: str,
    ) -> bool:
        return await self._post(
            f"/internal/drivers/{driver_id}/bidding/opportunities",
            payload={"session_id": str(session_id), "ride": ride_payload},
            idempotency_key=idempotency_key,
        )

    async def notify_bid_accepted(
        self,
        driver_id: UUID,
        session_id: UUID,
        ride_id: UUID,
        *,
        idempotency_key: str,
    ) -> bool:
        return await self._post(
            f"/internal/drivers/{driver_id}/bidding/accepted",
            payload={"session_id": str(session_id), "ride_id": str(ride_id)},
            idempotency_key=idempotency_key,
        )

    async def notify_session_cancelled(
        self,
        driver_id: UUID,
        session_id: UUID,
        ride_id: UUID,
        *,
        idempotency_key: str,
    ) -> bool:
        return await self._post(
            f"/internal/drivers/{driver_id}/bidding/cancelled",
            payload={"session_id": str(session_id), "ride_id": str(ride_id)},
            idempotency_key=idempotency_key,
        )

    async def _post(self, path: str, payload: dict[str, Any], idempotency_key: str) -> bool:
        if not self._client:
            logger.error("WebhookClient not started")
            return False

        headers = {"Idempotency-Key": idempotency_key}
        backoffs = [1.0, 2.0, 5.0, 10.0]
        max_attempts = 5
        last_error = ""

        for attempt in range(1, max_attempts + 1):
            try:
                resp = await self._client.post(path, json=payload, headers=headers)
                if resp.status_code < 300:
                    return True
                last_error = f"HTTP {resp.status_code}: {resp.text}"
            except httpx.HTTPError as exc:
                last_error = str(exc)

            if attempt < max_attempts:
                await asyncio.sleep(backoffs[attempt - 1])

        logger.error("WebhookClient completely failed after 5 attempts path=%s err=%s", path, last_error)

        if self._publisher:
            from sp.infrastructure.messaging.events import BaseEvent
            class WebhookFailedEvent(BaseEvent):
                event_type = "webhook.failed"
            dlq_payload = {
                "event_type": "webhook.failed",
                "original_payload": payload,
                "error": last_error,
                "retry_count": max_attempts
            }
            # Manually publish to DLQ topic
            await self._publisher._producer.send_and_wait("bidding-webhook-dlq.v1", json.dumps(dlq_payload).encode())

        return False


class NullWebhookClient(WebhookClientProtocol):
    """No-op fallback for local dev / testing."""

    async def dispatch_bidding_opportunity(self, *args, **kwargs) -> bool:
        return True

    async def notify_bid_accepted(self, *args, **kwargs) -> bool:
        return True

    async def notify_session_cancelled(self, *args, **kwargs) -> bool:
        return True
