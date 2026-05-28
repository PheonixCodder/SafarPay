"""Mapbox API client."""
from __future__ import annotations

import logging

import httpx

from ..domain.exceptions import RoutingError
from ..domain.interfaces import RoutingClientProtocol
from ..domain.models import Coordinates, Route, RouteStep

logger = logging.getLogger("geospatial.mapbox")

_DEFAULT_TIMEOUT = 10.0


class MapboxClient(RoutingClientProtocol):
    """Adapter for Mapbox Directions and Matrix APIs."""

    def __init__(
        self,
        access_token: str,
        *,
        timeout: float = _DEFAULT_TIMEOUT,
        allow_mock_route: bool = False,
    ) -> None:
        self._access_token = access_token
        self._timeout = timeout
        self._allow_mock_route = allow_mock_route
        self._client: httpx.AsyncClient | None = None
        # Use OSRM or Mapbox. 
        # By default, use mapbox directions v5 if token is provided.
        self._base_url = "https://api.mapbox.com/directions/v5/mapbox/driving"
        self._matrix_url = "https://api.mapbox.com/directions-matrix/v1/mapbox/driving"

    async def start(self) -> None:
        self._client = httpx.AsyncClient(timeout=httpx.Timeout(self._timeout))
        if self._access_token:
            logger.info("Mapbox routing enabled.")
        elif self._allow_mock_route:
            logger.warning("Mapbox token missing. Explicit mock routing enabled.")
        else:
            logger.warning("Mapbox token missing. Route calculation will fail fast.")

    async def close(self) -> None:
        if self._client:
            await self._client.aclose()
            self._client = None

    async def calculate_route(self, origin: Coordinates, destination: Coordinates) -> Route:
        if not self._client or not self._access_token:
            if self._allow_mock_route:
                logger.warning("MapboxClient not started or no token. Using dynamic mock route.")
                return self._mock_route(origin, destination)
            raise RoutingError("Mapbox routing is not configured")

        url = f"{self._base_url}/{origin.longitude},{origin.latitude};{destination.longitude},{destination.latitude}"
        params = {
            "access_token": self._access_token,
            "geometries": "polyline",
            "steps": "true",
            "overview": "full",
        }

        try:
            resp = await self._client.get(url, params=params)
            resp.raise_for_status()
            data = resp.json()
            
            if data["code"] != "Ok" or not data.get("routes"):
                raise RoutingError(f"Mapbox returned code: {data.get('code')}")
                
            r = data["routes"][0]
            steps = []
            for leg in r.get("legs", []):
                for step in leg.get("steps", []):
                    steps.append(
                        RouteStep(
                            instruction=step.get("maneuver", {}).get("instruction", ""),
                            distance_meters=float(step.get("distance", 0)),
                            duration_seconds=float(step.get("duration", 0)),
                            polyline=step.get("geometry", ""),
                        )
                    )

            return Route(
                distance_km=float(r["distance"]) / 1000.0,
                duration_minutes=float(r["duration"]) / 60.0,
                polyline=r["geometry"],
                steps=steps,
            )
        except httpx.HTTPError as exc:
            logger.error("Mapbox routing network failed: %s", exc)
            raise RoutingError("Failed to communicate with Mapbox API") from exc

    async def calculate_eta_matrix(
        self,
        origins: list[Coordinates],
        destinations: list[Coordinates],
    ) -> list[list[float | None]]:
        if not self._client or not self._access_token:
            # Mock matrix
            return [[120.0 for _ in destinations] for _ in origins]

        # Mapbox matrix takes a list of coordinates
        coords = [f"{o.longitude},{o.latitude}" for o in origins] + [f"{d.longitude},{d.latitude}" for d in destinations]
        coords_str = ";".join(coords)
        
        # Sources are the first N indices
        sources = ";".join(str(i) for i in range(len(origins)))
        # Destinations are the remaining indices
        dests = ";".join(str(i) for i in range(len(origins), len(origins) + len(destinations)))

        url = f"{self._matrix_url}/{coords_str}"
        params = {
            "access_token": self._access_token,
            "sources": sources,
            "destinations": dests,
        }

        try:
            resp = await self._client.get(url, params=params)
            resp.raise_for_status()
            data = resp.json()
            
            if data["code"] != "Ok":
                raise RoutingError(f"Mapbox matrix returned code: {data.get('code')}")
                
            return data["durations"]
        except httpx.HTTPError as exc:
            logger.error("Mapbox matrix network failed: %s", exc)
            raise RoutingError("Failed to communicate with Mapbox matrix API") from exc

    def _mock_route(self, origin: Coordinates, destination: Coordinates) -> Route:
        midpoint = Coordinates(
            latitude=(origin.latitude + destination.latitude) / 2,
            longitude=(origin.longitude + destination.longitude) / 2,
        )
        return Route(
            distance_km=_haversine_km(origin, destination),
            duration_minutes=max(1.0, (_haversine_km(origin, destination) / 30.0) * 60.0),
            polyline=_encode_polyline([origin, midpoint, destination]),
            steps=[],
        )


def _haversine_km(origin: Coordinates, destination: Coordinates) -> float:
    from math import atan2, cos, radians, sin, sqrt

    radius_km = 6371.0
    lat1 = radians(origin.latitude)
    lat2 = radians(destination.latitude)
    delta_lat = radians(destination.latitude - origin.latitude)
    delta_lng = radians(destination.longitude - origin.longitude)
    value = (
        sin(delta_lat / 2) * sin(delta_lat / 2)
        + cos(lat1) * cos(lat2) * sin(delta_lng / 2) * sin(delta_lng / 2)
    )
    return radius_km * 2 * atan2(sqrt(value), sqrt(1 - value))


def _encode_polyline(points: list[Coordinates]) -> str:
    result: list[str] = []
    previous_lat = 0
    previous_lng = 0

    for point in points:
        lat = round(point.latitude * 1e5)
        lng = round(point.longitude * 1e5)
        result.append(_encode_value(lat - previous_lat))
        result.append(_encode_value(lng - previous_lng))
        previous_lat = lat
        previous_lng = lng

    return "".join(result)


def _encode_value(value: int) -> str:
    value = ~(value << 1) if value < 0 else value << 1
    encoded = []
    while value >= 0x20:
        encoded.append(chr((0x20 | (value & 0x1F)) + 63))
        value >>= 5
    encoded.append(chr(value + 63))
    return "".join(encoded)
