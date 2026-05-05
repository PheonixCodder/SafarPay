from __future__ import annotations

from contextlib import asynccontextmanager
from datetime import datetime, time, timedelta, timezone
from typing import Any
from uuid import UUID, uuid4

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from geospatial.api.router import router as geospatial_router
from geospatial.domain.models import (
    Coordinates,
    DriverCandidate,
    Route,
    RouteStep,
    ServiceZone,
    SurgeResult,
    ZoneType,
)
from sp.infrastructure.security.dependencies import get_current_user
from sp.infrastructure.security.jwt import TokenPayload

ADMIN_ID = UUID("aaaaaaaa-bbbb-1111-bbbb-aaaaaaaaaaaa")
USER_ID = UUID("bbbbbbbb-bbbb-2222-bbbb-bbbbbbbbbbbb")
DRIVER_ID = UUID("cccccccc-bbbb-3333-bbbb-cccccccccccc")
OTHER_DRIVER_ID = UUID("dddddddd-bbbb-4444-bbbb-dddddddddddd")
RIDE_ID = UUID("eeeeeeee-bbbb-5555-bbbb-eeeeeeeeeeee")


def token(user_id: UUID = ADMIN_ID, role: str = "admin") -> TokenPayload:
    now = datetime.now(timezone.utc)
    return TokenPayload(
        user_id=user_id,
        email=f"{user_id}@example.test",
        role=role,
        session_id=uuid4(),
        iat=now,
        exp=now + timedelta(days=365),
    )


def make_candidate(
    driver_id: UUID = DRIVER_ID,
    *,
    distance: float = 1.0,
    eta: int | None = None,
    vehicle_type: str = "SEDAN",
    rating: float | None = 4.8,
    priority: float = 0.5,
) -> DriverCandidate:
    return DriverCandidate(
        driver_id=driver_id,
        latitude=31.52,
        longitude=74.35,
        distance_km=distance,
        estimated_arrival_minutes=eta,
        vehicle_type=vehicle_type,
        rating=rating,
        priority_score=priority,
    )


def make_zone(
    *,
    name: str = "Lahore Core",
    zone_type: ZoneType = ZoneType.SURGE,
    surge: float = 1.5,
    active_from: time | None = None,
    active_until: time | None = None,
    is_active: bool = True,
) -> ServiceZone:
    zone = ServiceZone.create(
        name=name,
        zone_type=zone_type,
        polygon_wkt="POLYGON((0 0, 0 1, 1 1, 1 0, 0 0))",
        surge_multiplier=surge,
        active_from=active_from,
        active_until=active_until,
    )
    zone.is_active = is_active
    return zone


def make_route() -> Route:
    return Route(
        distance_km=5.0,
        duration_minutes=15.0,
        polyline="abc",
        steps=[RouteStep(instruction="Turn left", distance_meters=100, duration_seconds=30, polyline="step")],
    )


class FakeLocationProvider:
    def __init__(self, candidates: list[DriverCandidate] | None = None) -> None:
        self.candidates = candidates if candidates is not None else [make_candidate(), make_candidate(OTHER_DRIVER_ID, distance=3, rating=4.0)]
        self.calls: list[dict[str, Any]] = []

    async def get_nearby_drivers(
        self,
        latitude: float,
        longitude: float,
        radius_km: float,
        limit: int,
    ) -> list[DriverCandidate]:
        self.calls.append({"latitude": latitude, "longitude": longitude, "radius_km": radius_km, "limit": limit})
        return list(self.candidates)


class FakeRouting:
    def __init__(self) -> None:
        self.route = make_route()
        self.matrix: list[list[float | None]] = [[300], [600], [900]]
        self.fail_matrix = False
        self.fail_route: Exception | None = None

    async def calculate_route(self, origin: Coordinates, destination: Coordinates) -> Route:
        if self.fail_route:
            raise self.fail_route
        return self.route

    async def calculate_eta_matrix(self, origins: list[Coordinates], destinations: list[Coordinates]) -> list[list[float | None]]:
        if self.fail_matrix:
            raise RuntimeError("matrix failed")
        return self.matrix[: len(origins)]


class FakeH3:
    def geo_to_h3(self, latitude: float, longitude: float, resolution: int) -> str:
        return f"h3-{resolution}-{round(latitude, 2)}-{round(longitude, 2)}"

    def get_k_ring(self, h3_index: str, k: int) -> list[str]:
        return [h3_index, f"{h3_index}-{k}"]

    def estimate_k_from_radius(self, radius_km: float, resolution: int) -> int:
        return 2


class FakeSpatialRepo:
    def __init__(self) -> None:
        self.zones = [make_zone()]
        self.surge = SurgeResult(
            latitude=31.52,
            longitude=74.35,
            surge_multiplier=1.5,
            zone_id=self.zones[0].id,
            zone_name=self.zones[0].name,
            zone_type=self.zones[0].zone_type,
        )
        self.saved: list[ServiceZone] = []
        self.deactivated: list[UUID] = []
        self.deactivate_result = True

    async def save_zone(self, zone: ServiceZone) -> None:
        self.saved.append(zone)
        self.zones.append(zone)

    async def get_zone(self, zone_id: UUID) -> ServiceZone | None:
        return next((zone for zone in self.zones if zone.id == zone_id), None)

    async def get_active_zones_for_point(self, latitude: float, longitude: float) -> list[ServiceZone]:
        return list(self.zones)

    async def list_active_zones(self) -> list[ServiceZone]:
        return list(self.zones)

    async def deactivate_zone(self, zone_id: UUID) -> bool:
        self.deactivated.append(zone_id)
        return self.deactivate_result

    async def get_surge_for_point(self, latitude: float, longitude: float) -> SurgeResult:
        return self.surge


class FakePublisher:
    def __init__(self) -> None:
        self.events: list[Any] = []

    async def publish(self, event: Any) -> None:
        self.events.append(event)


@asynccontextmanager
async def noop_lifespan(app: FastAPI):
    yield


@pytest.fixture
def geospatial_app() -> FastAPI:
    app = FastAPI(lifespan=noop_lifespan)
    app.include_router(geospatial_router, prefix="/api/v1")
    app.dependency_overrides[get_current_user] = lambda: token()
    return app


@pytest.fixture
def geospatial_client(geospatial_app: FastAPI) -> TestClient:
    return TestClient(geospatial_app)
