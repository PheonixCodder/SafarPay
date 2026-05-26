"""External service clients with resilience."""
from __future__ import annotations

import asyncio
import logging
from typing import Any
from uuid import UUID

import httpx

from ..domain.exceptions import BiddingDomainError
from ..domain.interfaces import (
    DriverEligibilityClientProtocol,
    PaymentClientProtocol,
    RideServiceClientProtocol,
)

logger = logging.getLogger("bidding.clients")


# ** TODO Fix all clients
class ResilientHttpClient:
    """Base HTTP client with retries, timeout, and basic circuit breaker."""

    def __init__(self, base_url: str, timeout: float = 0.3, max_retries: int = 2) -> None:
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout
        self._max_retries = max_retries
        self._client: httpx.AsyncClient | None = None
        self._circuit_open = False
        self._failures = 0

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

    async def _get_with_retry(self, path: str) -> dict[str, Any]:
        if self._circuit_open:
            raise BiddingDomainError("Circuit breaker is open. Service unavailable.")

        if not self._client:
            raise BiddingDomainError("Client not started.")

        for attempt in range(1, self._max_retries + 1):
            try:
                resp = await self._client.get(path)
                if resp.status_code >= 500:
                    self._failures += 1
                else:
                    self._failures = 0
                    if resp.status_code == 404:
                        raise BiddingDomainError("Resource not found")
                    if resp.status_code == 403:
                        raise BiddingDomainError("Unauthorized access")
                    resp.raise_for_status()
                    return resp.json()
            except (httpx.TransportError, httpx.TimeoutException) as exc:
                self._failures += 1
                if attempt == self._max_retries:
                    logger.error("HTTP request failed after %d attempts: %s", self._max_retries, exc)
                    raise BiddingDomainError("Service request failed") from exc
                await asyncio.sleep(0.1 * attempt)

        if self._failures >= 5:
            self._circuit_open = True
            logger.critical("Circuit breaker opened for %s", self._base_url)
            # A real implementation would have a background task to half-open the circuit later

        raise BiddingDomainError("Max retries exceeded")

    async def _post(self, path: str, payload: dict[str, Any], *, idempotency_key: str) -> dict[str, Any]:
        if not self._client:
            raise BiddingDomainError("Client not started.")

        last_exc: httpx.TransportError | httpx.TimeoutException | None = None
        for attempt in range(1, self._max_retries + 1):
            try:
                resp = await self._client.post(
                    path,
                    json=payload,
                    headers={"Idempotency-Key": idempotency_key},
                )
                if resp.status_code >= 500 and attempt < self._max_retries:
                    await asyncio.sleep(0.1 * attempt)
                    continue
                if resp.status_code >= 400:
                    raise BiddingDomainError(f"HTTP {resp.status_code}: {resp.text[:200]}")
                self._failures = 0
                return resp.json() if resp.content else {}
            except (httpx.TransportError, httpx.TimeoutException) as exc:
                last_exc = exc
                self._failures += 1
                if attempt == self._max_retries:
                    logger.error(
                        "HTTP POST %s failed after %d attempts: %s",
                        path,
                        self._max_retries,
                        exc,
                    )
                    raise BiddingDomainError("Service request failed") from exc
                await asyncio.sleep(0.1 * attempt)

        raise BiddingDomainError("Service request failed") from last_exc

# ** TODO Fix all clients
class RideServiceClient(ResilientHttpClient, RideServiceClientProtocol):
    def __init__(self, base_url: str) -> None:
        # Use a short timeout of 300ms as requested
        super().__init__(base_url, timeout=0.3, max_retries=2)

    async def validate_ride(self, ride_id: UUID, passenger_id: UUID) -> dict[str, Any]:
        try:
            data = await self._get_with_retry(f"/internal/rides/{ride_id}/validate?passenger_id={passenger_id}")
            return data
        except BiddingDomainError as e:
            logger.error("Ride validation failed for %s: %s", ride_id, e)
            raise

# ** TODO Fix all clients
class DriverEligibilityClient(ResilientHttpClient, DriverEligibilityClientProtocol):
    def __init__(self, base_url: str) -> None:
        super().__init__(base_url, timeout=0.2, max_retries=2)

    async def validate_driver(self, driver_id: UUID, session_id: UUID) -> bool:
        try:
            data = await self._get_with_retry(f"/internal/drivers/{driver_id}/eligibility?session_id={session_id}")
            return data.get("is_eligible", False)
        except BiddingDomainError as e:
            logger.warning("Driver eligibility check failed for %s: %s", driver_id, e)
            return False


class PaymentClient(ResilientHttpClient, PaymentClientProtocol):
    def __init__(self, base_url: str) -> None:
        super().__init__(base_url, timeout=3.0, max_retries=2)

    async def reserve_commission(
        self,
        ride_id: UUID,
        driver_id: UUID,
        passenger_id: UUID | None,
        basis_amount: float,
        *,
        idempotency_key: str,
    ) -> dict[str, Any]:
        return await self._post(
            f"/api/v1/internal/rides/{ride_id}/commission/reserve",
            {
                "driver_id": str(driver_id),
                "passenger_id": str(passenger_id) if passenger_id else None,
                "basis_amount": basis_amount,
                "currency": "PKR",
            },
            idempotency_key=idempotency_key,
        )


class NullPaymentClient(PaymentClientProtocol):
    async def reserve_commission(self, *args, **kwargs) -> dict[str, Any]:
        logger.warning("NullPaymentClient: commission reserve skipped")
        return {}
