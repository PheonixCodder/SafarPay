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

    def __init__(self, access_token: str, *, timeout: float = _DEFAULT_TIMEOUT) -> None:
        self._access_token = access_token
        self._timeout = timeout
        self._client: httpx.AsyncClient | None = None
        # Use OSRM or Mapbox. 
        # By default, use mapbox directions v5 if token is provided.
        self._base_url = "https://api.mapbox.com/directions/v5/mapbox/driving"
        self._matrix_url = "https://api.mapbox.com/directions-matrix/v1/mapbox/driving"

    async def start(self) -> None:
        self._client = httpx.AsyncClient(timeout=httpx.Timeout(self._timeout))

    async def close(self) -> None:
        if self._client:
            await self._client.aclose()
            self._client = None

    async def calculate_route(self, origin: Coordinates, destination: Coordinates) -> Route:
        if not self._client or not self._access_token:
            logger.warning("MapboxClient not started or no token. Using mock route.")
            return self._mock_route(origin, destination)

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
        return Route(
            distance_km=5.0,
            duration_minutes=15.0,
            polyline="mock_polyline",
            steps=[],
        )
