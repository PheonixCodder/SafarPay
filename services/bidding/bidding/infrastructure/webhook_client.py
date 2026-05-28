"""Webhook client for dispatching bidding opportunities to drivers."""
from __future__ import annotations

import asyncio
import logging
from typing import Any
from uuid import UUID

import httpx
from sp.infrastructure.messaging.publisher import EventPublisher

from ..application.schemas import BiddingRidePayload
from ..domain.interfaces import WebhookClientProtocol

logger = logging.getLogger("bidding.webhook")


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
        ride_id = ride_payload.get("ride_id") or ride_payload.get("id")
        payload = {
            **ride_payload,
            "ride_id": str(ride_id or ""),
            "session_id": str(session_id),
            "pricing_mode": "hybrid",
            "alert_type": "bidding_opportunity",
        }
        return await self._post(
            f"/api/v1/notification/internal/ride-jobs/{driver_id}",
            payload=payload,
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
            f"/api/v1/notification/internal/ride-jobs/{driver_id}",
            payload=BiddingRidePayload(
                session_id=session_id,
                ride_id=ride_id,
            ).model_dump(mode="json")
            | {
                "alert_type": "bid_accepted",
                "title": "Ride confirmed",
                "message": "The passenger accepted your offer.",
            },
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
            f"/api/v1/notification/internal/ride-jobs/{driver_id}",
            payload=BiddingRidePayload(
                session_id=session_id,
                ride_id=ride_id,
            ).model_dump(mode="json")
            | {
                "alert_type": "session_cancelled",
                "title": "Ride request closed",
                "message": "This bidding request is no longer available.",
            },
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
            dlq_payload = {
                "event_type": "webhook.failed",
                "original_payload": payload,
                "error": last_error,
                "retry_count": max_attempts
            }
            await self._publisher.publish_to_topic(
                "bidding-webhook-dlq.v1",
                BaseEvent(event_type="webhook.failed", payload=dlq_payload)
            )

        return False


class NullWebhookClient(WebhookClientProtocol):
    """No-op fallback for local dev / testing."""

    async def dispatch_bidding_opportunity(self, *args, **kwargs) -> bool:
        return True

    async def notify_bid_accepted(self, *args, **kwargs) -> bool:
        return True

    async def notify_session_cancelled(self, *args, **kwargs) -> bool:
        return True
