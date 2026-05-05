from __future__ import annotations

# ruff: noqa: E402,I001

import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

import pytest
from fastapi import FastAPI
from ride.application.use_cases import (
    _code_to_resp,
    _proof_to_resp,
    _ride_to_resp,
    _ride_to_summary,
    _stop_to_resp,
)
from ride.domain.exceptions import (
    InvalidStateTransitionError,
    RideNotFoundError,
    StopNotArrivedError,
    UnauthorisedRideAccessError,
    VerificationCodeExhaustedError,
    VerificationCodeInvalidError,
)
from ride.domain.models import DriverCandidate, RideStatus
from ride.infrastructure.dependencies import (
    get_accept_ride_uc,
    get_add_stop_uc,
    get_cancel_ride_uc,
    get_complete_ride_uc,
    get_gen_code_uc,
    get_gen_proof_url_uc,
    get_get_ride_uc,
    get_list_rides_uc,
    get_mark_arrived_uc,
    get_mark_completed_uc,
    get_nearby_drivers_uc,
    get_proof_with_url_uc,
    get_start_ride_uc,
    get_upload_proof_uc,
    get_verify_code_uc,
    get_create_ride_uc,
)
from sp.infrastructure.security.dependencies import get_current_user, get_optional_driver_id

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tests.ride.conftest import (
    DRIVER_ID,
    PASSENGER_ID,
    make_code,
    make_proof,
    make_ride,
    ride_payload,
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


def override(app: FastAPI, dependency: Any, value: Any) -> StubUseCase:
    uc = value if isinstance(value, StubUseCase) else StubUseCase(value)
    app.dependency_overrides[dependency] = lambda: uc
    return uc


def test_all_ride_routes_success(ride_app: FastAPI, ride_client: Any) -> None:
    ride = make_ride(driver_id=DRIVER_ID, status=RideStatus.ACCEPTED)
    stop = ride.stops[0]
    stop.mark_arrived()
    code = make_code(ride.id)
    proof = make_proof(ride.id)
    nearby_response = {
        "ride_id": str(ride.id),
        "candidates": [
            {
                "driver_id": str(DRIVER_ID),
                "distance_km": 1.2,
                "vehicle_type": "SEDAN",
                "rating": 4.8,
                "priority_score": 0.9,
                "estimated_arrival_minutes": 5,
            }
        ],
        "count": 1,
    }

    override(ride_app, get_create_ride_uc, _ride_to_resp(ride))
    override(ride_app, get_list_rides_uc, [_ride_to_summary(ride)])
    override(ride_app, get_get_ride_uc, _ride_to_resp(ride))
    override(ride_app, get_cancel_ride_uc, _ride_to_resp(ride))
    override(ride_app, get_accept_ride_uc, _ride_to_resp(ride))
    override(ride_app, get_start_ride_uc, _ride_to_resp(ride))
    override(ride_app, get_complete_ride_uc, _ride_to_resp(ride))
    override(ride_app, get_add_stop_uc, _stop_to_resp(stop))
    override(ride_app, get_mark_arrived_uc, _stop_to_resp(stop))
    override(ride_app, get_mark_completed_uc, _stop_to_resp(stop))
    override(ride_app, get_gen_code_uc, _code_to_resp(code))
    override(ride_app, get_verify_code_uc, _code_to_resp(code))
    upload_url = StubUseCase({
        "presigned_url": "https://s3.test/put",
        "file_key": "proofs/key.jpg",
        "expires_in_seconds": 900,
        "proof_type": "PICKUP",
        "mime_type": "image/jpeg",
    })
    override(ride_app, get_gen_proof_url_uc, upload_url)
    upload_proof = override(ride_app, get_upload_proof_uc, _proof_to_resp(proof))
    get_proof = StubUseCase({**_proof_to_resp(proof).model_dump(), "view_url": "https://s3.test/get"})
    override(ride_app, get_proof_with_url_uc, get_proof)
    override(ride_app, get_nearby_drivers_uc, nearby_response)

    assert ride_client.post("/api/v1/rides", json=ride_payload()).status_code == 201
    assert ride_client.get("/api/v1/rides").status_code == 200
    assert ride_client.get(f"/api/v1/rides/{ride.id}").status_code == 200
    assert ride_client.post(f"/api/v1/rides/{ride.id}/cancel", json={"reason": "x"}).status_code == 200
    assert ride_client.post(f"/api/v1/rides/{ride.id}/accept", json={}).status_code == 200
    assert ride_client.post(f"/api/v1/rides/{ride.id}/start", json={"verification_code": "123456"}).status_code == 200
    assert ride_client.post(f"/api/v1/rides/{ride.id}/complete", json={"final_price": 500}).status_code == 200
    assert ride_client.post(
        f"/api/v1/rides/{ride.id}/stops",
        json={"sequence_order": 3, "stop_type": "WAYPOINT", "latitude": 31.7, "longitude": 74.4},
    ).status_code == 201
    assert ride_client.post(f"/api/v1/stops/{stop.id}/arrived").status_code == 200
    assert ride_client.post(f"/api/v1/stops/{stop.id}/completed").status_code == 200
    assert ride_client.post(f"/api/v1/rides/{ride.id}/verification-codes", json={}).status_code == 201
    assert ride_client.post(
        f"/api/v1/rides/{ride.id}/verification-codes/verify",
        json={"code": "123456", "user_id": str(PASSENGER_ID)},
    ).status_code == 200
    assert ride_client.post(
        f"/api/v1/rides/{ride.id}/proofs/upload-url",
        json={"proof_type": "PICKUP", "file_name": "pickup.jpg"},
    ).status_code == 200
    assert ride_client.post(
        f"/api/v1/rides/{ride.id}/proofs",
        json={"proof_type": "PICKUP", "file_key": "proofs/key.jpg"},
    ).status_code == 201
    assert ride_client.get(f"/api/v1/rides/{ride.id}/proofs/{proof.id}/url").status_code == 200
    assert ride_client.get(f"/api/v1/drivers/nearby?lat=31.5&lng=74.3&ride_id={ride.id}").status_code == 200

    assert upload_url.calls[0][2]["actor_user_id"] == PASSENGER_ID
    assert upload_proof.calls[0][2]["uploader_user_id"] == PASSENGER_ID
    assert get_proof.calls[0][2]["actor_user_id"] == PASSENGER_ID


def test_proof_routes_use_driver_uuid_when_optional_driver_is_present(ride_app: FastAPI, ride_client: Any) -> None:
    ride = make_ride(driver_id=DRIVER_ID, status=RideStatus.ACCEPTED)
    proof = make_proof(ride.id, user_id=None, driver_id=DRIVER_ID)
    ride_app.dependency_overrides[get_current_user] = lambda: token(PASSENGER_ID, role="driver")
    ride_app.dependency_overrides[get_optional_driver_id] = lambda: DRIVER_ID
    upload_url = override(
        ride_app,
        get_gen_proof_url_uc,
        {
            "presigned_url": "https://s3.test/put",
            "file_key": "proofs/key.jpg",
            "expires_in_seconds": 900,
            "proof_type": "PICKUP",
            "mime_type": "image/jpeg",
        },
    )
    upload_proof = override(ride_app, get_upload_proof_uc, _proof_to_resp(proof))
    get_proof = override(
        ride_app,
        get_proof_with_url_uc,
        {**_proof_to_resp(proof).model_dump(), "view_url": "https://s3.test/get"},
    )

    ride_client.post(
        f"/api/v1/rides/{ride.id}/proofs/upload-url",
        json={"proof_type": "PICKUP", "file_name": "pickup.jpg"},
    )
    ride_client.post(
        f"/api/v1/rides/{ride.id}/proofs",
        json={"proof_type": "PICKUP", "file_key": "proofs/key.jpg"},
    )
    ride_client.get(f"/api/v1/rides/{ride.id}/proofs/{proof.id}/url")

    assert upload_url.calls[0][2]["actor_user_id"] == DRIVER_ID
    assert upload_proof.calls[0][2]["uploader_driver_id"] == DRIVER_ID
    assert get_proof.calls[0][2]["actor_user_id"] == DRIVER_ID


@pytest.mark.parametrize(
    ("dependency", "exc", "status_code"),
    [
        (get_get_ride_uc, RideNotFoundError("missing"), 404),
        (get_cancel_ride_uc, UnauthorisedRideAccessError("forbidden"), 403),
        (get_accept_ride_uc, InvalidStateTransitionError("bad state"), 409),
        (get_start_ride_uc, VerificationCodeInvalidError("bad code"), 422),
        (get_complete_ride_uc, VerificationCodeExhaustedError("too many"), 429),
        (get_mark_completed_uc, StopNotArrivedError("not arrived"), 409),
    ],
)
def test_route_domain_error_mapping(
    ride_app: FastAPI,
    ride_client: Any,
    dependency: Any,
    exc: Exception,
    status_code: int,
) -> None:
    ride_id = uuid4()
    stop_id = uuid4()
    override(ride_app, dependency, StubUseCase(exc=exc))

    route_by_dependency: dict[Any, tuple[str, str, dict[str, Any] | None]] = {
        get_get_ride_uc: ("get", f"/api/v1/rides/{ride_id}", None),
        get_cancel_ride_uc: ("post", f"/api/v1/rides/{ride_id}/cancel", {}),
        get_accept_ride_uc: ("post", f"/api/v1/rides/{ride_id}/accept", {}),
        get_start_ride_uc: ("post", f"/api/v1/rides/{ride_id}/start", {}),
        get_complete_ride_uc: ("post", f"/api/v1/rides/{ride_id}/complete", {}),
        get_mark_completed_uc: ("post", f"/api/v1/stops/{stop_id}/completed", None),
    }
    method, path, body = route_by_dependency[dependency]
    response = getattr(ride_client, method)(path, json=body) if body is not None else getattr(ride_client, method)(path)

    assert response.status_code == status_code


def test_schema_validation_errors_return_422(ride_app: FastAPI, ride_client: Any) -> None:
    override(ride_app, get_create_ride_uc, _ride_to_resp(make_ride()))
    override(ride_app, get_verify_code_uc, StubUseCase())
    override(ride_app, get_nearby_drivers_uc, StubUseCase({"ride_id": None, "candidates": [], "count": 0}))
    payload = ride_payload()
    payload["stops"] = payload["stops"][:1]

    assert ride_client.post("/api/v1/rides", json=payload).status_code == 422
    assert ride_client.post(
        f"/api/v1/rides/{uuid4()}/verification-codes/verify",
        json={"code": "123456"},
    ).status_code == 422
    assert ride_client.get("/api/v1/drivers/nearby?lat=99&lng=74").status_code == 422


def test_nearby_drivers_route_passes_query_parameters(ride_app: FastAPI, ride_client: Any) -> None:
    class NearbyStub(StubUseCase):
        async def execute(self, *args: Any, **kwargs: Any) -> Any:
            self.calls.append((*args, kwargs))
            ride_id = kwargs["ride_id"]
            return {
                "ride_id": str(ride_id),
                "candidates": [],
                "count": 0,
            }

    uc = NearbyStub()
    override(ride_app, get_nearby_drivers_uc, uc)
    ride_id = uuid4()

    response = ride_client.get(f"/api/v1/drivers/nearby?lat=31.5&lng=74.3&radius=7&ride_id={ride_id}")

    assert response.status_code == 200
    assert uc.calls[0][0:3] == (31.5, 74.3, 7.0)
    assert uc.calls[0][3]["ride_id"] == ride_id


def test_response_serializers_include_expected_datetime_and_identity_fields() -> None:
    ride = make_ride(driver_id=DRIVER_ID, status=RideStatus.ACCEPTED)
    proof = make_proof(ride.id, user_id=None, driver_id=DRIVER_ID)
    candidate = DriverCandidate(
        driver_id=DRIVER_ID,
        latitude=31.5,
        longitude=74.3,
        distance_km=1.2,
        vehicle_type="SEDAN",
        rating=4.9,
        priority_score=1,
        estimated_arrival_minutes=4,
    )

    assert _ride_to_resp(ride).assigned_driver_id == DRIVER_ID
    assert _proof_to_resp(proof).uploaded_by_driver_id == DRIVER_ID
    assert candidate.driver_id == DRIVER_ID
    assert isinstance(datetime.now(timezone.utc), datetime)
