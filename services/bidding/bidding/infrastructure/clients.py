"""External service clients with resilience."""
from __future__ import annotations

import asyncio
import logging
from typing import Any
from uuid import UUID

import httpx

from ..domain.exceptions import BiddingDomainError
from ..domain.interfaces import DriverEligibilityClientProtocol, RideServiceClientProtocol

logger = logging.getLogger("bidding.clients")


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
