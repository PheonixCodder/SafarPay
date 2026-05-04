"""Geospatial domain interfaces."""
from __future__ import annotations

from typing import Protocol
from uuid import UUID

from .models import Coordinates, DriverCandidate, MatchResult, Route, ServiceZone, SurgeResult


class LocationProviderProtocol(Protocol):
    """Interface for fetching live driver locations."""

    async def get_nearby_drivers(
        self,
        latitude: float,
        longitude: float,
        radius_km: float,
        limit: int,
    ) -> list[DriverCandidate]:
        """Fetch nearby active drivers from the location service."""
        ...


class RoutingClientProtocol(Protocol):
    """Interface for routing and ETA calculations."""

    async def calculate_route(
        self,
        origin: Coordinates,
        destination: Coordinates,
    ) -> Route:
        """Calculate route polyline, distance, and ETA."""
        ...

    async def calculate_eta_matrix(
        self,
        origins: list[Coordinates],
        destinations: list[Coordinates],
    ) -> list[list[float | None]]:
        """Calculate ETA matrix (origins to destinations) in seconds."""
        ...


class SpatialRepositoryProtocol(Protocol):
    """Interface for persistent spatial data (zones)."""

    async def save_zone(self, zone: ServiceZone) -> None:
        """Save a new or updated service zone."""
        ...

    async def get_zone(self, zone_id: UUID) -> ServiceZone | None:
        """Retrieve a service zone by ID."""
        ...

    async def get_active_zones_for_point(self, latitude: float, longitude: float) -> list[ServiceZone]:
        """Find all active zones that contain the given point."""
        ...

    async def list_active_zones(self) -> list[ServiceZone]:
        """List all currently active service zones."""
        ...

    async def deactivate_zone(self, zone_id: UUID) -> bool:
        """Soft-delete a zone by marking it inactive. Returns True if found."""
        ...

    async def get_surge_for_point(self, latitude: float, longitude: float) -> SurgeResult:
        """Return the highest applicable surge multiplier for zones containing the point."""
        ...


class H3IndexProtocol(Protocol):
    """Interface for H3 spatial operations."""

    def geo_to_h3(self, latitude: float, longitude: float, resolution: int) -> str:
        """Convert coordinates to an H3 index."""
        ...

    def get_k_ring(self, h3_index: str, k: int) -> list[str]:
        """Get all H3 indices within k rings of the origin index."""
        ...

    def estimate_k_from_radius(self, radius_km: float, resolution: int) -> int:
        """Estimate the k-ring radius needed to cover a given radius in km."""
        ...


class GeospatialCacheProtocol(Protocol):
    """Interface for short-term caching of matching states."""

    async def set_driver_shortlist(self, ride_id: UUID, candidates: list[DriverCandidate], ttl: int) -> None:
        """Cache a shortlist of matched drivers for a ride."""
        ...

    async def get_driver_shortlist(self, ride_id: UUID) -> list[DriverCandidate] | None:
        """Retrieve a cached driver shortlist."""
        ...

    async def set_match_result(self, ride_id: UUID, result: MatchResult, ttl: int) -> None:
        """Cache the final match result."""
        ...
