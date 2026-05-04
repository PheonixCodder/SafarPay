"""H3 indexing infrastructure.

Supports both H3 v3 (geo_to_h3 / k_ring) and H3 v4+ (latlng_to_cell / grid_disk).
"""
from __future__ import annotations

import math

import h3

from ..domain.interfaces import H3IndexProtocol

# H3 v4 renamed the core functions. Detect which API is available.
_HAS_V4 = hasattr(h3, "latlng_to_cell")

# Average edge length in km per resolution (approximate)
_H3_EDGE_LENGTH_KM: dict[int, float] = {
    0: 1107.71, 1: 418.68, 2: 158.24, 3: 59.81,
    4: 22.61, 5: 8.54, 6: 3.23, 7: 1.22,
    8: 0.461, 9: 0.174, 10: 0.066, 11: 0.025,
    12: 0.009, 13: 0.003, 14: 0.001, 15: 0.001,
}


class H3IndexAdapter(H3IndexProtocol):
    """Adapter for Uber's H3 library."""

    def geo_to_h3(self, latitude: float, longitude: float, resolution: int) -> str:
        """Convert coordinates to an H3 index.

        Args:
            latitude: Latitude in degrees.
            longitude: Longitude in degrees.
            resolution: H3 resolution (0-15).

        Returns:
            H3 index string.
        """
        if _HAS_V4:
            return h3.latlng_to_cell(latitude, longitude, resolution)
        return h3.geo_to_h3(latitude, longitude, resolution)  # type: ignore[attr-defined]

    def get_k_ring(self, h3_index: str, k: int) -> list[str]:
        """Get all H3 indices within k rings of the origin index.

        Args:
            h3_index: Origin H3 index string.
            k: Number of rings (radius).

        Returns:
            List of H3 index strings.
        """
        if _HAS_V4:
            return list(h3.grid_disk(h3_index, k))
        return list(h3.k_ring(h3_index, k))  # type: ignore[attr-defined]

    def estimate_k_from_radius(self, radius_km: float, resolution: int) -> int:
        """Estimate the k-ring radius needed to cover a given radius in km.

        Uses the average edge length for the resolution to compute how many
        concentric rings are needed.

        Args:
            radius_km: Desired search radius in kilometres.
            resolution: H3 resolution level (0-15).

        Returns:
            Minimum k value to cover the radius.
        """
        edge_km = _H3_EDGE_LENGTH_KM.get(resolution, 0.174)
        if edge_km <= 0:
            return 1
        # Each ring adds ~2 * edge_length to the coverage diameter
        return max(1, math.ceil(radius_km / (2 * edge_km)))

    def get_search_cells(
        self, latitude: float, longitude: float, radius_km: float, resolution: int,
    ) -> list[str]:
        """Convenience: get all H3 cells covering a circular search area.

        Args:
            latitude: Centre latitude.
            longitude: Centre longitude.
            radius_km: Search radius in km.
            resolution: H3 resolution.

        Returns:
            List of H3 cell strings covering the area.
        """
        center = self.geo_to_h3(latitude, longitude, resolution)
        k = self.estimate_k_from_radius(radius_km, resolution)
        return self.get_k_ring(center, k)
