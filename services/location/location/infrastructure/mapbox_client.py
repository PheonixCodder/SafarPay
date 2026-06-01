"""Mapbox Geocoding API client.

Wraps the Mapbox Geocoding REST API v5 with:
  - Cache-first reads (24-hour TTL via platform CacheManager)
  - httpx.AsyncClient with connection pooling and 5s timeout
  - Graceful error handling — never raises to callers, returns empty result on failure

Mapbox API reference:
  https://docs.mapbox.com/api/search/geocoding/

Endpoints used:
  GET /geocoding/v5/mapbox.places/{query}.json?access_token=...
  GET /geocoding/v5/mapbox.places/{lng},{lat}.json?access_token=...
"""
from __future__ import annotations

import hashlib
import logging
from typing import Any
from urllib.parse import quote

import httpx
from sp.infrastructure.cache.manager import CacheManager

from ..domain.models import Address, Coordinates

logger = logging.getLogger("location.mapbox_client")

_GEOCODE_CACHE_TTL = 86_400   # 24 hours — geocoded addresses change rarely
_BASE_URL = "https://api.mapbox.com/geocoding/v5/mapbox.places"
_TIMEOUT = 5.0


class MapboxClient:
    """Async Mapbox Geocoding client with cache-first reads."""

    def __init__(self, access_token: str, cache: CacheManager) -> None:
        self._token = access_token
        self._cache = cache
        self._http = httpx.AsyncClient(
            timeout=_TIMEOUT,
            limits=httpx.Limits(max_connections=20, max_keepalive_connections=10),
        )

    async def close(self) -> None:
        await self._http.aclose()

    # ------------------------------------------------------------------
    # Geocode: address text → coordinates list
    # ------------------------------------------------------------------

    async def geocode(self, address: str) -> list[Coordinates]:
        """Convert a free-text address to a list of coordinate candidates.

        Returns an empty list on API error — callers should handle gracefully.
        """
        cache_key = hashlib.sha256(address.lower().strip().encode()).hexdigest()
        cached = await self._cache.get("mapbox_geocode", cache_key)
        if cached:
            return [Coordinates(**c) for c in cached]

        try:
            resp = await self._http.get(
                f"{_BASE_URL}/{quote(address.strip(), safe='')}.json",
                params={
                    "access_token": self._token,
                    "limit": 5,
                    "types": "address,place",
                },
            )
            resp.raise_for_status()
            features: list[dict] = resp.json().get("features", [])
            results = [
                Coordinates(
                    latitude=f["center"][1],
                    longitude=f["center"][0],
                )
                for f in features
            ]
            await self._cache.set(
                "mapbox_geocode",
                cache_key,
                [{"latitude": c.latitude, "longitude": c.longitude} for c in results],
                ttl=_GEOCODE_CACHE_TTL,
            )
            return results
        except Exception as exc:  # noqa: BLE001
            addr_token = hashlib.sha256(address.encode()).hexdigest()[:12]
            logger.exception("Mapbox geocode failed addr_token=%s: %s", addr_token, exc)
            return []

    # ------------------------------------------------------------------
    # Search places rich: address text → full Address list (with names)
    # ------------------------------------------------------------------

    async def search_places_rich(
        self,
        query: str,
        *,
        limit: int = 5,
        country: str = "pk",
        proximity: tuple[float, float] | None = None,
    ) -> list[Address]:
        """Forward geocode returning full Address objects with place names.

        Unlike ``geocode()`` which returns bare Coordinates, this method
        extracts place_name, street, city, and country from the Mapbox
        response so results can be displayed and saved to the local DB.
        """
        proximity_key = ""
        if proximity is not None:
            proximity_key = f":{proximity[0]:.5f},{proximity[1]:.5f}"
        cache_key = (
            f"rich:{hashlib.sha256((query.lower().strip() + proximity_key).encode()).hexdigest()}"
        )
        cached = await self._cache.get("mapbox_geocode_rich", cache_key)
        if cached:
            return [_dict_to_address(c) for c in cached]

        params: dict[str, Any] = {
            "access_token": self._token,
            "limit": limit,
            "types": "address,place,poi,locality,neighborhood",
            "country": country,
        }
        if proximity is not None:
            params["proximity"] = f"{proximity[0]},{proximity[1]}"

        try:
            resp = await self._http.get(
                f"{_BASE_URL}/{quote(query.strip(), safe='')}.json",
                params=params,
            )
            resp.raise_for_status()
            features: list[dict] = resp.json().get("features", [])
            results: list[Address] = []
            for feat in features:
                context: list[dict] = feat.get("context", [])

                def _ctx(id_prefix: str) -> str | None:
                    return next(
                        (c["text"] for c in context if c.get("id", "").startswith(id_prefix)),
                        None,
                    )

                results.append(Address(
                    formatted=feat.get("place_name", query),
                    coordinates=Coordinates(
                        latitude=feat["center"][1],
                        longitude=feat["center"][0],
                    ),
                    street=feat.get("text"),
                    city=_ctx("place"),
                    country=_ctx("country"),
                    postal_code=_ctx("postcode"),
                ))
            await self._cache.set(
                "mapbox_geocode_rich",
                cache_key,
                [_address_to_dict(a) for a in results],
                ttl=_GEOCODE_CACHE_TTL,
            )
            return results
        except httpx.HTTPStatusError as exc:
            addr_token = hashlib.sha256(query.encode()).hexdigest()[:12]
            body = exc.response.text[:500] if exc.response is not None else ""
            logger.warning(
                "Mapbox search_places_rich HTTP %s addr_token=%s body=%s",
                exc.response.status_code if exc.response is not None else "?",
                addr_token,
                body,
            )
            return []
        except Exception as exc:  # noqa: BLE001
            addr_token = hashlib.sha256(query.encode()).hexdigest()[:12]
            logger.exception("Mapbox search_places_rich failed addr_token=%s: %s", addr_token, exc)
            return []


    # ------------------------------------------------------------------
    # Reverse geocode: coordinates → Address
    # ------------------------------------------------------------------

    async def reverse_geocode(self, latitude: float, longitude: float) -> Address:
        """Convert coordinates to the nearest human-readable address.

        Returns a fallback Address with the raw coordinates on API error.
        """
        cache_key = f"{latitude:.6f}:{longitude:.6f}"
        cached = await self._cache.get("mapbox_reverse", cache_key)
        if cached:
            return _dict_to_address(cached)

        fallback = Address(
            formatted=f"{latitude:.5f}, {longitude:.5f}",
            coordinates=Coordinates(latitude=latitude, longitude=longitude),
        )

        try:
            resp = await self._http.get(
                f"{_BASE_URL}/{longitude},{latitude}.json",
                params={
                    "access_token": self._token,
                    "limit": 1,
                    "types": "address,place,poi,locality,neighborhood",
                },
            )
            resp.raise_for_status()
            features = resp.json().get("features", [])
            if not features:
                return fallback

            feat = features[0]
            context: list[dict] = feat.get("context", [])

            def _ctx(id_prefix: str) -> str | None:
                return next(
                    (c["text"] for c in context if c.get("id", "").startswith(id_prefix)),
                    None,
                )

            addr = Address(
                formatted=feat.get("place_name", fallback.formatted),
                coordinates=Coordinates(latitude=latitude, longitude=longitude),
                street=feat.get("text"),
                city=_ctx("place"),
                country=_ctx("country"),
                postal_code=_ctx("postcode"),
            )
            await self._cache.set(
                "mapbox_reverse",
                cache_key,
                _address_to_dict(addr),
                ttl=_GEOCODE_CACHE_TTL,
            )
            return addr
        except Exception as exc:  # noqa: BLE001
            logger.exception("Mapbox reverse geocode failed (%s,%s): %s", latitude, longitude, exc)
            return fallback


# ---------------------------------------------------------------------------
# Serialisation helpers
# ---------------------------------------------------------------------------


def _address_to_dict(addr: Address) -> dict:
    return {
        "formatted": addr.formatted,
        "latitude": addr.coordinates.latitude,
        "longitude": addr.coordinates.longitude,
        "street": addr.street,
        "city": addr.city,
        "country": addr.country,
        "postal_code": addr.postal_code,
    }


def _dict_to_address(data: dict) -> Address:
    return Address(
        formatted=data["formatted"],
        coordinates=Coordinates(
            latitude=data["latitude"],
            longitude=data["longitude"],
        ),
        street=data.get("street"),
        city=data.get("city"),
        country=data.get("country"),
        postal_code=data.get("postal_code"),
    )
