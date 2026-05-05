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
RIDE_SRC = ROOT / "services" / "ride"
if str(RIDE_SRC) not in sys.path:
    sys.path.insert(0, str(RIDE_SRC))
loaded_ride = sys.modules.get("ride")
if loaded_ride is not None and str(RIDE_SRC) not in str(getattr(loaded_ride, "__file__", "")):
    del sys.modules["ride"]

from ride.api.router import router as ride_router  # noqa: E402
from ride.domain.models import (  # noqa: E402
    DriverCandidate,
    PricingMode,
    ProofImage,
    ProofType,
    RideStatus,
    ServiceCategory,
    ServiceRequest,
    ServiceType,
    Stop,
    StopType,
    VerificationCode,
)


PASSENGER_ID = UUID("11111111-1111-1111-1111-111111111111")
OTHER_USER_ID = UUID("22222222-2222-2222-2222-222222222222")
DRIVER_ID = UUID("33333333-3333-3333-3333-333333333333")
OTHER_DRIVER_ID = UUID("44444444-4444-4444-4444-444444444444")


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


def make_stop(
    ride_id: UUID,
    stop_type: StopType,
    sequence_order: int,
    *,
    arrived: bool = False,
    completed: bool = False,
) -> Stop:
    now = datetime.now(timezone.utc)
    return Stop(
        id=uuid4(),
        service_request_id=ride_id,
        sequence_order=sequence_order,
        stop_type=stop_type,
        latitude=31.5204 + sequence_order,
        longitude=74.3587 + sequence_order,
        place_name=f"{stop_type.value.title()} {sequence_order}",
        address_line_1="Test address",
        address_line_2=None,
        city="Lahore",
        state=None,
        country="PK",
        postal_code=None,
        contact_name=None,
        contact_phone=None,
        instructions=None,
        arrived_at=now if arrived or completed else None,
        completed_at=now if completed else None,
    )


def make_ride(
    *,
    passenger_id: UUID = PASSENGER_ID,
    driver_id: UUID | None = None,
    pricing_mode: PricingMode = PricingMode.FIXED,
    status: RideStatus = RideStatus.MATCHING,
    requires_otp_start: bool = False,
    requires_otp_end: bool = False,
) -> ServiceRequest:
    ride = ServiceRequest(
        id=uuid4(),
        passenger_id=passenger_id,
        service_type=ServiceType.CITY_RIDE,
        category=ServiceCategory.MINI,
        pricing_mode=pricing_mode,
        status=status,
        assigned_driver_id=driver_id,
        baseline_min_price=400.0,
        baseline_max_price=500.0,
        auto_accept_driver=True,
        requires_otp_start=requires_otp_start,
        requires_otp_end=requires_otp_end,
    )
    ride.stops = [
        make_stop(ride.id, StopType.PICKUP, 1),
        make_stop(ride.id, StopType.DROPOFF, 2),
    ]
    return ride


def make_code(ride_id: UUID, code: str = "123456") -> VerificationCode:
    return VerificationCode(
        id=uuid4(),
        service_request_id=ride_id,
        code=code,
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=10),
    )


def make_proof(
    ride_id: UUID,
    *,
    user_id: UUID | None = PASSENGER_ID,
    driver_id: UUID | None = None,
) -> ProofImage:
    return ProofImage.create(
        service_request_id=ride_id,
        proof_type=ProofType.PICKUP,
        file_key=f"proofs/{ride_id}/pickup.jpg",
        file_name="pickup.jpg",
        mime_type="image/jpeg",
        uploaded_by_user_id=user_id,
        uploaded_by_driver_id=driver_id,
    )


def ride_payload(pricing_mode: str = "FIXED") -> dict[str, Any]:
    return {
        "service_type": "CITY_RIDE",
        "category": "MINI",
        "pricing_mode": pricing_mode,
        "baseline_min_price": 400,
        "baseline_max_price": 500,
        "auto_accept_driver": True,
        "stops": [
            {
                "sequence_order": 1,
                "stop_type": "PICKUP",
                "latitude": 31.52,
                "longitude": 74.35,
            },
            {
                "sequence_order": 2,
                "stop_type": "DROPOFF",
                "latitude": 31.6,
                "longitude": 74.4,
            },
        ],
        "detail": {
            "service_type": "CITY_RIDE",
            "passenger_count": 1,
            "preferred_vehicle_type": "SEDAN",
        },
    }


class FakeCache:
    def __init__(self) -> None:
        self.sets: list[tuple[str, str, Any, int | None]] = []
        self.deletes: list[tuple[str, str]] = []

    async def set(self, namespace: str, key: str, value: Any, ttl: int | None = None) -> None:
        self.sets.append((namespace, key, value, ttl))

    async def delete(self, namespace: str, key: str) -> None:
        self.deletes.append((namespace, key))


class FakePublisher:
    def __init__(self) -> None:
        self.events: list[Any] = []

    async def publish(self, event: Any) -> None:
        self.events.append(event)


class FakeRideWebSockets:
    def __init__(self) -> None:
        self.passenger_events: list[tuple[UUID, Any, dict[str, Any]]] = []
        self.driver_events: list[tuple[UUID, Any, dict[str, Any]]] = []
        self.driver_broadcasts: list[tuple[list[UUID], Any, dict[str, Any]]] = []

    async def broadcast_to_passenger(self, passenger_id: UUID, event: Any, payload: dict[str, Any]) -> None:
        self.passenger_events.append((passenger_id, event, payload))

    async def broadcast_to_driver(self, driver_id: UUID, event: Any, payload: dict[str, Any]) -> None:
        self.driver_events.append((driver_id, event, payload))

    async def broadcast_to_drivers(self, driver_ids: list[UUID], event: Any, payload: dict[str, Any]) -> None:
        self.driver_broadcasts.append((driver_ids, event, payload))


class FakeRideRepo:
    def __init__(self, ride: ServiceRequest | None = None) -> None:
        self.ride = ride
        self.created_detail: dict[str, Any] | None = None
        self.status_updates: list[tuple[UUID, RideStatus, dict[str, Any]]] = []
        self.find_by_passenger_calls: list[tuple[UUID, list[RideStatus] | None, int, int]] = []

    async def create_full(
        self,
        ride: ServiceRequest,
        stops: list[Stop],
        detail_data: dict[str, Any],
    ) -> ServiceRequest:
        ride.stops = stops
        self.ride = ride
        self.created_detail = detail_data
        return ride

    async def find_by_id(self, ride_id: UUID) -> ServiceRequest | None:
        return self.ride if self.ride and self.ride.id == ride_id else None

    async def find_by_passenger(
        self,
        passenger_id: UUID,
        status_filter: list[RideStatus] | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> list[ServiceRequest]:
        self.find_by_passenger_calls.append((passenger_id, status_filter, limit, offset))
        if self.ride and self.ride.passenger_id == passenger_id:
            return [self.ride]
        return []

    async def update_status(self, ride_id: UUID, status: RideStatus, **kwargs: Any) -> None:
        self.status_updates.append((ride_id, status, kwargs))


class FakeStopRepo:
    def __init__(self, stop: Stop | None = None) -> None:
        self.stop = stop
        self.created: list[Stop] = []
        self.arrived: list[tuple[UUID, datetime]] = []
        self.completed: list[tuple[UUID, datetime]] = []

    async def create(self, stop: Stop) -> Stop:
        self.created.append(stop)
        self.stop = stop
        return stop

    async def find_by_id(self, stop_id: UUID) -> Stop | None:
        return self.stop if self.stop and self.stop.id == stop_id else None

    async def update_arrived_at(self, stop_id: UUID, arrived_at: datetime) -> None:
        self.arrived.append((stop_id, arrived_at))

    async def update_completed_at(self, stop_id: UUID, completed_at: datetime) -> None:
        self.completed.append((stop_id, completed_at))


class FakeCodeRepo:
    def __init__(self, code: VerificationCode | None = None) -> None:
        self.code = code
        self.created: list[VerificationCode] = []
        self.updated: list[VerificationCode] = []

    async def create(self, code: VerificationCode) -> VerificationCode:
        self.created.append(code)
        self.code = code
        return code

    async def find_active_by_ride(self, ride_id: UUID) -> VerificationCode | None:
        if self.code and self.code.service_request_id == ride_id and not self.code.is_verified:
            return self.code
        return None

    async def update_verification(self, code: VerificationCode) -> None:
        self.updated.append(code)


class FakeProofRepo:
    def __init__(self, proofs: list[ProofImage] | None = None) -> None:
        self.proofs = proofs or []
        self.created: list[ProofImage] = []

    async def create(self, proof: ProofImage) -> ProofImage:
        self.created.append(proof)
        self.proofs.append(proof)
        return proof

    async def find_by_ride(self, ride_id: UUID) -> list[ProofImage]:
        return [proof for proof in self.proofs if proof.service_request_id == ride_id]


class FakeGeo:
    def __init__(self) -> None:
        self.calls: list[dict[str, Any]] = []
        self.candidates = [
            DriverCandidate(
                driver_id=DRIVER_ID,
                latitude=31.5,
                longitude=74.3,
                distance_km=1.2,
                vehicle_type="SEDAN",
                rating=4.8,
                priority_score=0.9,
                estimated_arrival_minutes=5,
            )
        ]

    async def find_nearby_drivers(self, latitude: float, longitude: float, radius_km: float, **kwargs: Any) -> list[DriverCandidate]:
        self.calls.append({"latitude": latitude, "longitude": longitude, "radius_km": radius_km, **kwargs})
        return self.candidates


class FakeWebhook:
    def __init__(self) -> None:
        self.jobs: list[tuple[UUID, UUID, dict[str, Any], str]] = []

    async def dispatch_ride_job(
        self,
        driver_id: UUID,
        ride_id: UUID,
        ride_payload: dict[str, Any],
        idempotency_key: str,
    ) -> None:
        self.jobs.append((driver_id, ride_id, ride_payload, idempotency_key))


class FakeStorage:
    async def generate_presigned_put_url(self, file_key: str, content_type: str) -> str:
        return f"https://s3.test/put/{file_key}?content_type={content_type}"

    async def generate_presigned_get_url(self, file_key: str) -> str:
        return f"https://s3.test/get/{file_key}"


@asynccontextmanager
async def noop_lifespan(app: FastAPI):
    yield


@pytest.fixture
def ride_app() -> FastAPI:
    app = FastAPI(lifespan=noop_lifespan)
    app.include_router(ride_router, prefix="/api/v1")
    app.dependency_overrides[get_current_user] = lambda: token()
    app.dependency_overrides[get_current_driver] = lambda: DRIVER_ID
    app.dependency_overrides[get_optional_driver_id] = lambda: None
    return app


@pytest.fixture
def ride_client(ride_app: FastAPI) -> TestClient:
    return TestClient(ride_app)
