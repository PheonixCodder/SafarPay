"""Geospatial service HTTP adapter.

Calls the SafarPay geospatial microservice to find eligible nearby drivers.
Returns a list of DriverCandidate domain objects ranked by proximity.

If GEOSPATIAL_SERVICE_URL is not configured, a NullGeospatialClient is used
which always returns an empty list (safe for local dev / unit tests).
"""
from __future__ import annotations

import logging
from typing import Any
from uuid import UUID

import httpx

from ..domain.interfaces import GeospatialClientProtocol
from ..domain.models import DriverCandidate

logger = logging.getLogger("ride.geospatial")

_DEFAULT_TIMEOUT = 8.0

# TODO implement geospatial client
class GeospatialClient:
    """HTTP adapter to the SafarPay geospatial service."""

    def __init__(self, base_url: str, *, timeout: float = _DEFAULT_TIMEOUT) -> None:
        self._base_url = base_url.rstrip("/")
        self._client: httpx.AsyncClient | None = None

    async def start(self) -> None:
        self._client = httpx.AsyncClient(
            base_url=self._base_url,
            timeout=httpx.Timeout(_DEFAULT_TIMEOUT),
            headers={"Accept": "application/json"},
        )

    async def close(self) -> None:
        if self._client:
            await self._client.aclose()
            self._client = None

    async def find_nearby_drivers(
        self,
        latitude: float,
        longitude: float,
        radius_km: float,
        *,
        category: str | None = None,
        vehicle_type: str | None = None,
        fuel_types: list[str] | None = None,
        limit: int = 20,
    ) -> list[DriverCandidate]:
        if not self._client:
            logger.error("GeospatialClient not started")
            return []

        params: dict[str, Any] = {
            "lat": latitude,
            "lng": longitude,
            "radius_km": radius_km,
            "limit": limit,
        }
        if category:
            params["category"] = category
        if vehicle_type:
            params["vehicle_type"] = vehicle_type
        if fuel_types:
            params["fuel_types"] = ",".join(fuel_types)

        try:
            resp = await self._client.get("/api/v1/drivers/nearby", params=params)
            resp.raise_for_status()
            data: list[dict[str, Any]] = resp.json().get("drivers", [])
            return [self._to_domain(d) for d in data]
        except httpx.HTTPError as exc:
            logger.error("GeospatialClient error: %s", exc)
            return []

    @staticmethod
    def _to_domain(raw: dict[str, Any]) -> DriverCandidate:
        return DriverCandidate(
            driver_id=UUID(raw["driver_id"]),
            distance_km=float(raw.get("distance_km", 0)),
            vehicle_type=raw.get("vehicle_type", "OTHER"),
            rating=raw.get("rating"),
            priority_score=float(raw.get("priority_score", 0)),
            estimated_arrival_minutes=raw.get("estimated_arrival_minutes"),
        )


class NullGeospatialClient:
    """No-op fallback when geospatial service is not configured."""

    async def start(self) -> None:
        pass

    async def close(self) -> None:
        pass

    async def find_nearby_drivers(
        self,
        latitude: float,
        longitude: float,
        radius_km: float,
        *,
        category: str | None = None,
        vehicle_type: str | None = None,
        fuel_types: list[str] | None = None,
        limit: int = 20,
    ) -> list[DriverCandidate]:
        logger.warning("NullGeospatialClient: no geo service configured — returning []")
        return []
