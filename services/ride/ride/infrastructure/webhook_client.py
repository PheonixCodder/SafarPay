"""Webhook client for dispatching ride jobs to downstream services.

Design
------
- Uses httpx.AsyncClient for non-blocking HTTP calls.
- Sends an `Idempotency-Key` header so downstream services can safely
  deduplicate retries.
- Exponential back-off with jitter on transient failures (5xx / network).
- A single shared client is reused across requests (configured at lifespan).
- Each dispatch is fire-and-forget from the caller's perspective but logs
  all failures for observability.
"""
from __future__ import annotations

import asyncio
import logging
import random
from typing import Any
from uuid import UUID

import httpx
from pydantic import BaseModel, ConfigDict

logger = logging.getLogger("ride.webhook")

_RETRY_STATUSES = {429, 500, 502, 503, 504}
_ALLOWED_MIME = {"image/jpeg", "image/png", "image/webp"}


class WebhookPayload(BaseModel):
    model_config = ConfigDict(extra="allow")


class RideJobPayload(WebhookPayload):
    driver_id: UUID
    ride_id: UUID


class RideCancellationPayload(WebhookPayload):
    driver_id: UUID
    ride_id: UUID
    reason: str | None = None


# TODO implement Webhook client
class WebhookClient:
    """httpx-based async webhook dispatcher with retry + idempotency."""

    def __init__(
        self,
        base_url: str,
        *,
        timeout: float = 10.0,
        max_retries: int = 3,
        backoff_base: float = 1.0,
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._timeout = httpx.Timeout(timeout)
        self._max_retries = max_retries
        self._backoff_base = backoff_base
        self._client: httpx.AsyncClient | None = None

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    async def start(self) -> None:
        """Create the shared async HTTP client. Call at lifespan startup."""
        self._client = httpx.AsyncClient(
            base_url=self._base_url,
            timeout=self._timeout,
            headers={"Content-Type": "application/json", "Accept": "application/json"},
        )
        logger.info("WebhookClient started base_url=%s", self._base_url)

    async def close(self) -> None:
        """Cleanly shut down the HTTP client. Call at lifespan shutdown."""
        if self._client:
            await self._client.aclose()
            self._client = None

    # ------------------------------------------------------------------
    # Internal retry helper
    # ------------------------------------------------------------------

    async def _post_with_retry(
        self,
        path: str,
        payload: dict[str, Any],
        idempotency_key: str,
    ) -> bool:
        if not self._client:
            logger.error("WebhookClient not started — call start() at lifespan.")
            return False

        headers = {"Idempotency-Key": idempotency_key}
        last_exc: Exception | None = None

        for attempt in range(1, self._max_retries + 1):
            try:
                resp = await self._client.post(path, json=payload, headers=headers)
                if resp.status_code < 300:
                    logger.info(
                        "Webhook OK path=%s idempotency_key=%s attempt=%d status=%d",
                        path, idempotency_key, attempt, resp.status_code,
                    )
                    return True
                if resp.status_code not in _RETRY_STATUSES:
                    logger.warning(
                        "Webhook non-retryable path=%s status=%d body=%s",
                        path, resp.status_code, resp.text[:200],
                    )
                    return False
                logger.warning(
                    "Webhook transient error path=%s status=%d attempt=%d/%d",
                    path, resp.status_code, attempt, self._max_retries,
                )
            except (httpx.TransportError, httpx.TimeoutException) as exc:
                last_exc = exc
                logger.warning(
                    "Webhook network error path=%s attempt=%d/%d exc=%s",
                    path, attempt, self._max_retries, exc,
                )

            if attempt < self._max_retries:
                delay = self._backoff_base * (2 ** (attempt - 1)) + random.uniform(0, 0.5)
                await asyncio.sleep(delay)

        logger.error(
            "Webhook exhausted retries path=%s idempotency_key=%s last_exc=%s",
            path, idempotency_key, last_exc,
        )
        return False

    # ------------------------------------------------------------------
    # Public API  (implements WebhookClientProtocol)
    # ------------------------------------------------------------------

    async def dispatch_ride_job(
        self,
        driver_id: UUID,
        ride_id: UUID,
        payload: dict[str, Any],
        *,
        idempotency_key: str,
    ) -> bool:
        """POST ride job to the notification/dispatch service endpoint."""
        body = {
            "driver_id": str(driver_id),
            "ride_id": str(ride_id),
            **payload,
        }
        body = RideJobPayload.model_validate(body).model_dump(mode="json")
        return await self._post_with_retry(
            f"/internal/ride-jobs/{driver_id}",
            body,
            idempotency_key,
        )

    async def dispatch_cancellation(
        self,
        driver_id: UUID,
        ride_id: UUID,
        reason: str | None,
        *,
        idempotency_key: str,
    ) -> bool:
        """Notify driver/dispatch service that a ride was cancelled."""
        body = {
            "driver_id": str(driver_id),
            "ride_id": str(ride_id),
            "reason": reason,
        }
        body = RideCancellationPayload.model_validate(body).model_dump(mode="json")
        return await self._post_with_retry(
            f"/internal/ride-cancellations/{driver_id}",
            body,
            idempotency_key,
        )


# ---------------------------------------------------------------------------
# Null implementation for environments without a webhook target
# ---------------------------------------------------------------------------

class NullWebhookClient:
    """No-op webhook client used when NOTIFICATION_SERVICE_URL is not configured."""

    async def dispatch_ride_job(
        self,
        driver_id: UUID,
        ride_id: UUID,
        payload: dict[str, Any],
        *,
        idempotency_key: str,
    ) -> bool:
        logger.warning(
            "NullWebhookClient: ride job not dispatched ride_id=%s driver_id=%s",
            ride_id, driver_id,
        )
        return False

    async def dispatch_cancellation(
        self,
        driver_id: UUID,
        ride_id: UUID,
        reason: str | None,
        *,
        idempotency_key: str,
    ) -> bool:
        return False

    async def start(self) -> None:
        pass

    async def close(self) -> None:
        pass
