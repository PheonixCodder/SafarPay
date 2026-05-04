"""Location service HTTP adapter.

Calls the Location Service's internal ``/api/v1/location/drivers/nearby``
endpoint.  The endpoint uses query params ``lat``, ``lng``, ``radius_km``,
``max_results`` and returns ``NearbyDriversResponse`` with a ``drivers`` list
of ``DriverLocationResponse`` objects.

This adapter maps the Location Service's response shape into the geospatial
domain's ``DriverCandidate`` model.

Authentication
--------------
The Location Service requires a Bearer JWT on all endpoints (``CurrentUser``
dependency).  We mint a **service-to-service token** at startup using the
platform's ``create_service_token()`` helper, signed with the shared
``JWT_SECRET``.  The role is ``"service"`` — the Location Service's ``CurrentUser``
only validates signature + expiry and accepts any role.
"""
from __future__ import annotations

import logging
from uuid import UUID

import httpx
from sp.infrastructure.security.jwt import create_service_token

from ..domain.interfaces import LocationProviderProtocol
from ..domain.models import DriverCandidate

logger = logging.getLogger("geospatial.location_client")

_DEFAULT_TIMEOUT = 8.0
_MAX_RETRIES = 2


class LocationClient(LocationProviderProtocol):
    """HTTP adapter to the SafarPay location service."""

    def __init__(
        self,
        base_url: str,
        jwt_secret: str,
        jwt_algorithm: str = "HS256",
        *,
        timeout: float = _DEFAULT_TIMEOUT,
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout
        self._jwt_secret = jwt_secret
        self._jwt_algorithm = jwt_algorithm
        self._client: httpx.AsyncClient | None = None

    async def start(self) -> None:
        # Mint a long-lived service-to-service JWT (renewed on every restart)
        service_token = create_service_token(
            service_name="geospatial",
            secret=self._jwt_secret,
            algorithm=self._jwt_algorithm,
        )
        self._client = httpx.AsyncClient(
            base_url=self._base_url,
            timeout=httpx.Timeout(self._timeout),
            headers={
                "Accept": "application/json",
                "Authorization": f"Bearer {service_token}",
            },
        )

    async def close(self) -> None:
        if self._client:
            await self._client.aclose()
            self._client = None

    async def get_nearby_drivers(
        self,
        latitude: float,
        longitude: float,
        radius_km: float,
        limit: int,
    ) -> list[DriverCandidate]:
        """Query Location Service for nearby ONLINE drivers.

        The Location Service endpoint signature (from its router):
            GET /api/v1/location/drivers/nearby
            Query params: lat, lng, radius_km, max_results
            Response: NearbyDriversResponse { drivers: [DriverLocationResponse], ... }

        DriverLocationResponse fields:
            driver_id, status, lat, lng, heading, speed, accuracy, updated_at, ride_id
        """
        if not self._client:
            logger.error("LocationClient not started — returning empty list")
            return []

        # Match the Location Service's actual query parameter names
        params = {
            "lat": latitude,
            "lng": longitude,
            "radius_km": radius_km,
            "max_results": limit,
        }

        for attempt in range(_MAX_RETRIES + 1):
            try:
                resp = await self._client.get(
                    "/api/v1/location/drivers/nearby", params=params,
                )
                resp.raise_for_status()

                data = resp.json()
                raw_drivers = data.get("drivers", [])

                candidates: list[DriverCandidate] = []
                for d in raw_drivers:
                    try:
                        candidates.append(
                            DriverCandidate(
                                driver_id=UUID(str(d["driver_id"])),
                                # Location service returns lat/lng, not latitude/longitude
                                latitude=float(d["lat"]),
                                longitude=float(d["lng"]),
                                distance_km=float(d.get("distance_km", 0.0)),
                                vehicle_type=d.get("vehicle_type", "OTHER"),
                                rating=d.get("rating"),
                            )
                        )
                    except (KeyError, ValueError, TypeError) as parse_err:
                        logger.warning(
                            "Skipped malformed driver row: %s — %s", d, parse_err,
                        )
                return candidates

            except httpx.TimeoutException:
                logger.warning(
                    "LocationClient timeout (attempt %d/%d)",
                    attempt + 1, _MAX_RETRIES + 1,
                )
            except httpx.HTTPStatusError as exc:
                logger.error(
                    "LocationClient HTTP %d: %s", exc.response.status_code, exc,
                )
                return []  # non-retryable
            except httpx.HTTPError as exc:
                logger.error("LocationClient network error: %s", exc)

        logger.error("LocationClient exhausted retries — returning empty list")
        return []
