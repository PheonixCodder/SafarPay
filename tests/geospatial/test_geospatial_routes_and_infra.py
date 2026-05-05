from __future__ import annotations

from typing import Any, cast
from uuid import uuid4

import httpx
import pytest
from fastapi import FastAPI
from geospatial.application.use_cases import FindNearbyDriversUseCase
from geospatial.domain.exceptions import RoutingError
from geospatial.domain.models import Coordinates, DriverCandidate, MatchingCriteria, SurgeResult
from geospatial.infrastructure.dependencies import (
    get_calculate_eta_uc,
    get_find_nearby_drivers_uc,
    get_manage_zones_uc,
    get_surge_uc,
    get_validate_pickup_uc,
)
from geospatial.infrastructure.location_client import LocationClient
from geospatial.infrastructure.mapbox_client import MapboxClient
from sp.infrastructure.security.dependencies import get_current_user

from tests.geospatial.conftest import (
    DRIVER_ID,
    USER_ID,
    FakeH3,
    FakeLocationProvider,
    FakeRouting,
    make_candidate,
    make_route,
    make_zone,
    token,
)


class StubUseCase:
    def __init__(self, response: Any = None, exc: Exception | None = None) -> None:
        self.response = response
        self.exc = exc
        self.calls: list[tuple[Any, ...]] = []

    async def execute(self, *args: Any, **kwargs: Any) -> Any:
        self.calls.append((*args, kwargs))
        if self.exc:
            raise self.exc
        return self.response


def override(app: FastAPI, dep: Any, value: Any) -> Any:
    app.dependency_overrides[dep] = lambda: value
    return value


def test_all_geospatial_routes_success_and_admin_zone_management(geospatial_app: FastAPI, geospatial_client: Any) -> None:
    candidate = make_candidate()
    route = make_route()
    zone = make_zone()
    nearby = override(geospatial_app, get_find_nearby_drivers_uc, StubUseCase([candidate]))
    eta = override(geospatial_app, get_calculate_eta_uc, StubUseCase(route))
    validate = override(geospatial_app, get_validate_pickup_uc, StubUseCase((True, [zone], 1.5)))
    surge = override(
        geospatial_app,
        get_surge_uc,
        StubUseCase(SurgeResult(31.52, 74.35, 1.5, zone.id, zone.name, zone.zone_type)),
    )

    class ZoneManager:
        async def create_zone(self, created_zone: Any) -> Any:
            self.created = created_zone
            return created_zone

        async def list_zones(self) -> list[Any]:
            return [zone]

        async def deactivate_zone(self, zone_id: Any) -> bool:
            self.deactivated = zone_id
            return True

    manager = ZoneManager()
    override(geospatial_app, get_manage_zones_uc, manager)

    assert geospatial_client.get("/api/v1/drivers/nearby?lat=31.52&lng=74.35&vehicle_type=SEDAN").status_code == 200
    assert geospatial_client.post(
        "/api/v1/routes",
        json={"origin": {"latitude": 31.52, "longitude": 74.35}, "destination": {"latitude": 31.6, "longitude": 74.4}},
    ).status_code == 200
    assert geospatial_client.post("/api/v1/validate-pickup", json={"latitude": 31.52, "longitude": 74.35}).status_code == 200
    assert geospatial_client.post("/api/v1/surge", json={"latitude": 31.52, "longitude": 74.35}).status_code == 200
    assert geospatial_client.post(
        "/api/v1/zones",
        json={"name": "Airport", "zone_type": "AIRPORT", "polygon_wkt": zone.polygon_wkt, "surge_multiplier": 1.2},
    ).status_code == 201
    assert geospatial_client.get("/api/v1/zones").status_code == 200
    assert geospatial_client.delete(f"/api/v1/zones/{zone.id}").status_code == 204

    assert nearby.calls[0][0].required_vehicle_type == "SEDAN"
    assert eta.calls[0][0] == Coordinates(31.52, 74.35)
    assert validate.calls[0][0:2] == (31.52, 74.35)
    assert surge.calls[0][0:2] == (31.52, 74.35)


def test_geospatial_route_errors_validation_and_admin_guard(geospatial_app: FastAPI, geospatial_client: Any) -> None:
    override(geospatial_app, get_calculate_eta_uc, StubUseCase(exc=RoutingError("mapbox failed")))
    override(geospatial_app, get_find_nearby_drivers_uc, StubUseCase([]))
    override(geospatial_app, get_surge_uc, StubUseCase(SurgeResult(31.52, 74.35, 1.0)))
    response = geospatial_client.post(
        "/api/v1/routes",
        json={"origin": {"latitude": 31.52, "longitude": 74.35}, "destination": {"latitude": 31.6, "longitude": 74.4}},
    )
    assert response.status_code == 502
    assert geospatial_client.get("/api/v1/drivers/nearby?lat=99&lng=74").status_code == 422
    assert geospatial_client.post("/api/v1/surge", json={"latitude": -99, "longitude": 74}).status_code == 422

    geospatial_app.dependency_overrides[get_current_user] = lambda: token(USER_ID, role="passenger")
    override(geospatial_app, get_manage_zones_uc, StubUseCase())
    assert geospatial_client.post(
        "/api/v1/zones",
        json={"name": "Airport", "zone_type": "AIRPORT", "polygon_wkt": "POLYGON EMPTY", "surge_multiplier": 1.2},
    ).status_code == 403

    geospatial_app.dependency_overrides[get_current_user] = lambda: token(role="admin")

    class MissingZoneManager:
        async def deactivate_zone(self, zone_id: Any) -> bool:
            return False

    override(geospatial_app, get_manage_zones_uc, MissingZoneManager())
    assert geospatial_client.delete(f"/api/v1/zones/{uuid4()}").status_code == 404


@pytest.mark.asyncio
async def test_location_client_maps_response_skips_bad_rows_and_handles_failures(monkeypatch: pytest.MonkeyPatch) -> None:
    class FakeResponse:
        def __init__(self, payload: dict[str, Any], status_code: int = 200) -> None:
            self._payload = payload
            self.status_code = status_code

        def json(self) -> dict[str, Any]:
            return self._payload

        def raise_for_status(self) -> None:
            if self.status_code >= 400:
                request = httpx.Request("GET", "https://location.test")
                response = httpx.Response(self.status_code, request=request)
                raise httpx.HTTPStatusError("bad", request=request, response=response)

    class FakeAsyncClient:
        def __init__(self, *args: Any, **kwargs: Any) -> None:
            self.headers = kwargs.get("headers", {})
            self.calls: list[tuple[str, dict[str, Any]]] = []

        async def get(self, path: str, params: dict[str, Any]) -> FakeResponse:
            self.calls.append((path, params))
            return FakeResponse(
                {
                    "drivers": [
                        {"driver_id": str(DRIVER_ID), "lat": 31.52, "lng": 74.35, "distance_km": 1.2, "vehicle_type": "SEDAN", "rating": 4.8},
                        {"driver_id": "bad"},
                    ]
                }
            )

        async def aclose(self) -> None:
            return None

    monkeypatch.setattr(httpx, "AsyncClient", FakeAsyncClient)
    client = LocationClient("https://location.test", "secret")
    await client.start()
    result = await client.get_nearby_drivers(31.52, 74.35, 5, 20)

    assert result == [DriverCandidate(driver_id=DRIVER_ID, latitude=31.52, longitude=74.35, distance_km=1.2, vehicle_type="SEDAN", rating=4.8)]
    assert client._client is not None
    fake_client = cast(Any, client._client)
    assert fake_client.calls[0][0] == "/api/v1/location/drivers/nearby"
    assert fake_client.calls[0][1] == {"lat": 31.52, "lng": 74.35, "radius_km": 5, "max_results": 20}
    assert "Bearer " in fake_client.headers["Authorization"]


@pytest.mark.asyncio
async def test_mapbox_client_mock_and_route_error_paths() -> None:
    client = MapboxClient("")
    route = await client.calculate_route(Coordinates(31.52, 74.35), Coordinates(31.6, 74.4))
    matrix = await client.calculate_eta_matrix([Coordinates(31.52, 74.35)], [Coordinates(31.6, 74.4)])

    assert route.polyline == "mock_polyline"
    assert matrix == [[120.0]]


def test_h3_fake_and_use_case_contract_helpers() -> None:
    h3 = FakeH3()
    assert h3.geo_to_h3(31.52, 74.35, 9).startswith("h3-9")
    assert h3.get_k_ring("abc", 2) == ["abc", "abc-2"]
    assert h3.estimate_k_from_radius(5, 9) == 2


@pytest.mark.asyncio
async def test_dependency_composed_find_nearby_use_case_contract() -> None:
    location = FakeLocationProvider([make_candidate()])
    routing = FakeRouting()
    h3 = FakeH3()
    uc = FindNearbyDriversUseCase(location, routing, h3)
    result = await uc.execute(MatchingCriteria(pickup=Coordinates(31.52, 74.35), radius_km=5))
    assert result[0].driver_id == DRIVER_ID
