from __future__ import annotations

from typing import Any, cast

import pytest
from location.application.use_cases import GeocodeUseCase, SearchPlacesUseCase
from location.domain.models import Address, Coordinates, Place, PlaceSearchResult
from location.maps.normalization import normalise_search_query, stable_source_key
from location.infrastructure.place_repository import build_place_search_sql


class FakePlaceRepository:
    def __init__(self, results: list[PlaceSearchResult] | None = None) -> None:
        self.results = results or []
        self.searches: list[dict[str, Any]] = []
        self.events: list[dict[str, Any]] = []

    async def search_places(
        self,
        query: str,
        *,
        latitude: float | None = None,
        longitude: float | None = None,
        limit: int = 10,
    ) -> list[PlaceSearchResult]:
        self.searches.append(
            {
                "query": query,
                "latitude": latitude,
                "longitude": longitude,
                "limit": limit,
            }
        )
        return self.results[:limit]

    async def record_search_event(
        self,
        query: str,
        *,
        result_count: int,
        served_from: str,
        latitude: float | None = None,
        longitude: float | None = None,
    ) -> None:
        self.events.append(
            {
                "query": query,
                "result_count": result_count,
                "served_from": served_from,
                "latitude": latitude,
                "longitude": longitude,
            }
        )

    async def save_place(self, place: Place) -> None:
        return None


class FakeMapbox:
    def __init__(self) -> None:
        self.calls: list[str] = []
        self.rich_calls: list[str] = []
        self.reverse_calls: list[tuple[float, float]] = []

    async def geocode(self, address: str) -> list[Coordinates]:
        self.calls.append(address)
        return [Coordinates(latitude=31.52, longitude=74.35)]

    async def search_places_rich(
        self,
        query: str,
        *,
        limit: int = 5,
        country: str = "pk",
        proximity: tuple[float, float] | None = None,
    ) -> list[Address]:
        self.rich_calls.append(query)
        return [
            Address(
                formatted=f"{query}, Lahore, Pakistan",
                coordinates=Coordinates(latitude=31.52, longitude=74.35),
                street=query,
                city="Lahore",
                country="Pakistan",
            )
        ]

    async def reverse_geocode(self, latitude: float, longitude: float) -> Address:
        self.reverse_calls.append((latitude, longitude))
        return Address(
            formatted="Pin Location, Lahore, Pakistan",
            coordinates=Coordinates(latitude=latitude, longitude=longitude),
            street="Pin Location",
            city="Lahore",
            country="Pakistan",
        )


def place_result(name: str = "Askari 10") -> PlaceSearchResult:
    return PlaceSearchResult(
        place=Place(
            name=name,
            formatted=f"{name}, Lahore, Pakistan",
            coordinates=Coordinates(latitude=31.51, longitude=74.39),
            place_type="neighbourhood",
            source="OSM",
            source_key="osm:node:1",
            country_code="PK",
            city="Lahore",
            country="Pakistan",
        ),
        confidence=0.91,
        distance_meters=1200,
    )


def test_place_search_normalisation_and_source_key_are_stable() -> None:
    assert normalise_search_query("  Askari-10, Lahore!!!  ") == "askari 10 lahore"
    assert normalise_search_query("D.H.A Phase 5") == "d h a phase 5"
    assert stable_source_key("OSM", "node", 123) == "osm:node:123"


@pytest.mark.asyncio
async def test_search_places_uses_local_results_without_mapbox_fallback() -> None:
    repo = FakePlaceRepository([place_result()])
    mapbox = FakeMapbox()
    uc = SearchPlacesUseCase(cast(Any, repo), cast(Any, mapbox), fallback_enabled=True)

    response = await uc.execute("Askari 10", latitude=31.5, longitude=74.3)

    assert len(response.results) == 1
    assert response.results[0].source == "OSM"
    assert mapbox.calls == []
    assert repo.searches[0]["query"] == "Askari 10"
    assert repo.events[0]["served_from"] == "LOCAL"


@pytest.mark.asyncio
async def test_search_places_falls_back_to_mapbox_and_logs_miss_without_storing_result() -> None:
    repo = FakePlaceRepository([])
    mapbox = FakeMapbox()
    uc = SearchPlacesUseCase(cast(Any, repo), cast(Any, mapbox), fallback_enabled=True)

    response = await uc.execute("Missing Place", limit=3)

    assert len(response.results) == 1
    assert response.results[0].source == "MAPBOX"
    assert response.results[0].formatted == "Missing Place, Lahore, Pakistan"
    assert mapbox.rich_calls == ["Missing Place"]
    assert mapbox.reverse_calls == []
    assert repo.events[0]["served_from"] == "MAPBOX_FALLBACK"


@pytest.mark.asyncio
async def test_search_places_uses_reverse_for_coordinate_query() -> None:
    repo = FakePlaceRepository([])
    mapbox = FakeMapbox()
    uc = SearchPlacesUseCase(cast(Any, repo), cast(Any, mapbox), fallback_enabled=True)

    response = await uc.execute("31.53723, 74.42631")

    assert len(response.results) == 1
    assert response.results[0].formatted == "Pin Location, Lahore, Pakistan"
    assert mapbox.rich_calls == []
    assert mapbox.reverse_calls == [(31.53723, 74.42631)]
    assert repo.events[0]["served_from"] == "COORDINATE_REVERSE"


@pytest.mark.asyncio
async def test_legacy_geocode_returns_best_local_place_before_mapbox() -> None:
    repo = FakePlaceRepository([place_result("Liberty Market")])
    mapbox = FakeMapbox()
    uc = GeocodeUseCase(cast(Any, mapbox), place_repo=cast(Any, repo), fallback_enabled=True)

    response = await uc.execute("Liberty")

    assert response.formatted == "Liberty Market, Lahore, Pakistan"
    assert response.coordinates.latitude == 31.51
    assert mapbox.calls == []


def test_place_search_sql_prioritises_curated_verified_exact_aliases() -> None:
    sql = build_place_search_sql().text

    assert "source = 'CURATED'" in sql
    assert "is_verified" in sql
    assert "normalised_alias = :query" in sql
    assert "source_priority DESC" in sql
    assert "exact_match DESC" in sql
