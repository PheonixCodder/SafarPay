from __future__ import annotations

# ruff: noqa: E402,I001

import sys
from contextlib import asynccontextmanager
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any
from uuid import UUID, uuid4

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sp.infrastructure.security.dependencies import (
    get_current_driver,
    get_current_user,
    get_optional_driver_id,
)
from sp.infrastructure.security.jwt import TokenPayload

ROOT = Path(__file__).resolve().parents[2]
LOCATION_SRC = ROOT / "services" / "location"
if str(LOCATION_SRC) not in sys.path:
    sys.path.insert(0, str(LOCATION_SRC))
loaded_location = sys.modules.get("location")
if loaded_location is not None and str(LOCATION_SRC) not in str(getattr(loaded_location, "__file__", "")):
    del sys.modules["location"]

from location.api.router import router as location_router
from location.domain.models import (
    ActorType,
    Address,
    Coordinates,
    DriverLocation,
    DriverStatus,
    LocationHistory,
    LocationUpdate,
    PassengerLocation,
)


PASSENGER_ID = UUID("11111111-aaaa-1111-aaaa-111111111111")
OTHER_USER_ID = UUID("22222222-aaaa-2222-aaaa-222222222222")
DRIVER_ID = UUID("33333333-aaaa-3333-aaaa-333333333333")
OTHER_DRIVER_ID = UUID("44444444-aaaa-4444-aaaa-444444444444")
RIDE_ID = UUID("55555555-aaaa-5555-aaaa-555555555555")


def token(user_id: UUID = PASSENGER_ID, role: str = "passenger") -> TokenPayload:
    now = datetime.now(timezone.utc)
    return TokenPayload(
        user_id=user_id,
        email=f"{user_id}@example.test",
        role=role,
        session_id=uuid4(),
        iat=now,
        exp=now + timedelta(hours=1),
    )


def location_payload(**overrides: Any) -> dict[str, Any]:
    payload = {
        "lat": 31.5204,
        "lng": 74.3587,
        "accuracy": 10.0,
        "speed": 35.0,
        "heading": 180.0,
        "ts": int(datetime.now(timezone.utc).timestamp() * 1000),
    }
    payload.update(overrides)
    return payload


def make_update(
    actor_id: UUID = DRIVER_ID,
    actor_type: ActorType = ActorType.DRIVER,
    *,
    ride_id: UUID | None = None,
    recorded_at: datetime | None = None,
    lat: float = 31.5204,
    lng: float = 74.3587,
) -> LocationUpdate:
    return LocationUpdate(
        actor_id=actor_id,
        actor_type=actor_type,
        latitude=lat,
        longitude=lng,
        accuracy_meters=10,
        speed_kmh=30,
        heading_degrees=90,
        recorded_at=recorded_at or datetime.now(timezone.utc),
        ride_id=ride_id,
    )


def make_driver_location(
    driver_id: UUID = DRIVER_ID,
    *,
    status: DriverStatus = DriverStatus.ONLINE,
    ride_id: UUID | None = None,
    stale: bool = False,
) -> DriverLocation:
    updated_at = datetime.now(timezone.utc) - timedelta(seconds=100) if stale else datetime.now(timezone.utc)
    return DriverLocation(
        driver_id=driver_id,
        status=status,
        last_update=make_update(driver_id, ActorType.DRIVER, ride_id=ride_id, recorded_at=updated_at),
        updated_at=updated_at,
        ride_id=ride_id,
    )


def make_passenger_location(user_id: UUID = PASSENGER_ID, *, ride_id: UUID | None = None) -> PassengerLocation:
    return PassengerLocation(
        user_id=user_id,
        last_update=make_update(user_id, ActorType.PASSENGER, ride_id=ride_id),
        updated_at=datetime.now(timezone.utc),
        ride_id=ride_id,
    )


def make_history(actor_id: UUID = DRIVER_ID, actor_type: ActorType = ActorType.DRIVER) -> LocationHistory:
    now = datetime.now(timezone.utc)
    return LocationHistory(
        id=uuid4(),
        actor_type=actor_type,
        actor_id=actor_id,
        latitude=31.5204,
        longitude=74.3587,
        accuracy_meters=10,
        speed_kmh=30,
        heading_degrees=90,
        recorded_at=now,
        ingested_at=now,
        ride_id=RIDE_ID,
    )


class FakeLocationStore:
    def __init__(self) -> None:
        self.drivers: dict[UUID, DriverLocation] = {}
        self.passengers: dict[UUID, PassengerLocation] = {}
        self.participants: dict[UUID, tuple[UUID, UUID]] = {}
        self.removed: list[UUID] = []
        self.status_updates: list[tuple[UUID, DriverStatus, UUID | None]] = []

    async def set_driver_location(
        self,
        driver_id: UUID,
        update: LocationUpdate,
        status: DriverStatus = DriverStatus.ONLINE,
        ride_id: UUID | None = None,
    ) -> None:
        self.drivers[driver_id] = DriverLocation(
            driver_id=driver_id,
            status=status,
            last_update=update,
            updated_at=update.recorded_at,
            ride_id=ride_id,
        )

    async def get_driver_location(self, driver_id: UUID) -> DriverLocation | None:
        return self.drivers.get(driver_id)

    async def set_passenger_location(self, user_id: UUID, update: LocationUpdate, ride_id: UUID | None = None) -> None:
        self.passengers[user_id] = PassengerLocation(
            user_id=user_id,
            last_update=update,
            updated_at=update.recorded_at,
            ride_id=ride_id,
        )

    async def get_passenger_location(self, user_id: UUID) -> PassengerLocation | None:
        return self.passengers.get(user_id)

    async def get_drivers_in_radius(
        self,
        latitude: float,
        longitude: float,
        radius_km: float,
        max_results: int = 50,
    ) -> list[DriverLocation]:
        return list(self.drivers.values())[:max_results]

    async def set_driver_status(self, driver_id: UUID, status: DriverStatus, ride_id: UUID | None = None) -> None:
        self.status_updates.append((driver_id, status, ride_id))
        current = self.drivers.get(driver_id) or make_driver_location(driver_id)
        current.status = status
        current.ride_id = ride_id
        self.drivers[driver_id] = current

    async def remove_driver(self, driver_id: UUID) -> None:
        self.removed.append(driver_id)
        self.drivers.pop(driver_id, None)

    async def set_ride_participants(self, ride_id: UUID, driver_id: UUID, passenger_user_id: UUID) -> None:
        self.participants[ride_id] = (driver_id, passenger_user_id)

    async def get_ride_participants(self, ride_id: UUID) -> tuple[UUID, UUID] | None:
        return self.participants.get(ride_id)

    async def delete_ride_participants(self, ride_id: UUID) -> None:
        self.participants.pop(ride_id, None)


class FakeHistory:
    def __init__(self) -> None:
        self.appended: list[LocationUpdate] = []
        self.records: list[LocationHistory] = []

    async def append(self, update: LocationUpdate) -> None:
        self.appended.append(update)

    async def get_actor_history(
        self,
        actor_id: UUID,
        actor_type: ActorType,
        since: datetime,
        until: datetime,
    ) -> list[LocationHistory]:
        return [r for r in self.records if r.actor_id == actor_id and r.actor_type == actor_type]


class FakeLimiter:
    def __init__(self, allowed: bool = True) -> None:
        self.allowed = allowed
        self.calls: list[tuple[UUID, ActorType, bool]] = []

    async def allow(self, actor_id: UUID, *, actor_type: ActorType, is_on_ride: bool = False) -> bool:
        self.calls.append((actor_id, actor_type, is_on_ride))
        return self.allowed


class FakeWs:
    def __init__(self) -> None:
        self.broadcasts: list[tuple[UUID, UUID, float, float]] = []
        self.subscribed: list[tuple[UUID, UUID]] = []
        self.unsubscribed_all: list[UUID] = []

    async def broadcast_driver_location(
        self,
        ride_id: UUID,
        driver_id: UUID,
        latitude: float,
        longitude: float,
        heading: float | None,
        speed: float | None,
    ) -> int:
        self.broadcasts.append((ride_id, driver_id, latitude, longitude))
        return 1

    def subscribe_ride(self, ride_id: UUID, user_id: UUID) -> None:
        self.subscribed.append((ride_id, user_id))

    def unsubscribe_all_from_ride(self, ride_id: UUID) -> None:
        self.unsubscribed_all.append(ride_id)


class FakePublisher:
    def __init__(self) -> None:
        self.driver_locations: list[tuple[UUID, LocationUpdate]] = []
        self.statuses: list[tuple[UUID, DriverStatus]] = []

    async def publish_driver_location_updated(self, driver_id: UUID, update: LocationUpdate) -> None:
        self.driver_locations.append((driver_id, update))

    async def publish_driver_status_changed(self, driver_id: UUID, status: DriverStatus) -> None:
        self.statuses.append((driver_id, status))


class FakeMapbox:
    def __init__(self) -> None:
        self.geocode_results = [Coordinates(latitude=31.52, longitude=74.35)]
        self.reverse_result = Address(
            formatted="Model Town, Lahore",
            coordinates=Coordinates(latitude=31.52, longitude=74.35),
            city="Lahore",
            country="PK",
        )

    async def geocode(self, address: str) -> list[Coordinates]:
        return self.geocode_results

    async def reverse_geocode(self, latitude: float, longitude: float) -> Address:
        return self.reverse_result


@asynccontextmanager
async def noop_lifespan(app: FastAPI):
    yield


@pytest.fixture
def location_app() -> FastAPI:
    app = FastAPI(lifespan=noop_lifespan)
    app.include_router(location_router, prefix="/api/v1/location")
    app.dependency_overrides[get_current_user] = lambda: token()
    app.dependency_overrides[get_current_driver] = lambda: DRIVER_ID
    app.dependency_overrides[get_optional_driver_id] = lambda: None
    return app


@pytest.fixture
def location_client(location_app: FastAPI) -> TestClient:
    return TestClient(location_app)
