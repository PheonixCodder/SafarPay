"""Location use cases — cache-first address lookup."""
from __future__ import annotations

import hashlib
import logging

from sp.infrastructure.cache.manager import CacheManager

from ..domain.models import Address, Coordinates
from .schemas import AddressResponse, CoordinatesResponse

logger = logging.getLogger("location.use_cases")
CACHE_TTL = 86400  # 24 hours — geocoded addresses don't change often


class GeocodeUseCase:
    """Convert a text address into coordinates (cache-first)."""

    def __init__(self, cache: CacheManager) -> None:
        self._cache = cache

    async def execute(self, address_text: str) -> AddressResponse:
        cache_key = hashlib.md5(address_text.lower().strip().encode()).hexdigest()
        cached = await self._cache.get("geocode", cache_key)
        if cached:
            logger.debug("Cache hit for geocode: %s", address_text)
            return AddressResponse(**cached)

        # Placeholder: in production call Google Maps / HERE / Nominatim
        # Returns a stub so the service is importable and testable
        result = Address(
            formatted=address_text,
            coordinates=Coordinates(latitude=0.0, longitude=0.0),
        )
        response = _to_response(result)
        await self._cache.set("geocode", cache_key, response.model_dump(), ttl=CACHE_TTL)
        return response


class ReverseGeocodeUseCase:
    """Convert lat/lon into a formatted address (cache-first)."""

    def __init__(self, cache: CacheManager) -> None:
        self._cache = cache

    async def execute(self, lat: float, lon: float) -> AddressResponse:
        cache_key = f"{lat:.6f}:{lon:.6f}"
        cached = await self._cache.get("reverse_geocode", cache_key)
        if cached:
            return AddressResponse(**cached)

        result = Address(
            formatted=f"{lat:.4f}, {lon:.4f}",
            coordinates=Coordinates(latitude=lat, longitude=lon),
        )
        response = _to_response(result)
        await self._cache.set("reverse_geocode", cache_key, response.model_dump(), ttl=CACHE_TTL)
        return response


def _to_response(addr: Address) -> AddressResponse:
    return AddressResponse(
        formatted=addr.formatted,
        coordinates=CoordinatesResponse(
            latitude=addr.coordinates.latitude,
            longitude=addr.coordinates.longitude,
        ),
        street=addr.street,
        city=addr.city,
        country=addr.country,
        postal_code=addr.postal_code,
    )
