from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import UUID, uuid4

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sp.infrastructure.security.dependencies import get_current_user
from sp.infrastructure.security.jwt import TokenPayload
from verification.api.router import get_use_cases, router
from verification.application.schemas import (
    DocumentUploadUrlsResponse,
    PresignedUrlResponse,
    RequirementGroupStatusResponse,
    ReviewSubmissionResponse,
    VerificationStatusResponse,
)
from verification.domain.exceptions import DriverNotFoundError, InvalidDocumentStateError

USER_ID = uuid4()
DRIVER_ID = uuid4()


def token_payload() -> TokenPayload:
    now = datetime.now(timezone.utc)
    return TokenPayload(
        user_id=USER_ID,
        email="driver@example.com",
        role="passenger",
        session_id=uuid4(),
        iat=now,
        exp=now + timedelta(minutes=15),
    )


def upload_response(*keys: str) -> DocumentUploadUrlsResponse:
    return DocumentUploadUrlsResponse(
        urls={key: PresignedUrlResponse(key=f"{key}-key", url=f"https://s3/{key}") for key in keys}
    )


def status_response(overall_status: str = "not_started") -> VerificationStatusResponse:
    empty = RequirementGroupStatusResponse(status="not_submitted", documents=[])
    return VerificationStatusResponse(
        driver_id=None if overall_status == "not_started" else DRIVER_ID,
        overall_status=overall_status,  # type: ignore[arg-type]
        identity=empty,
        license=empty,
        selfie=empty,
        vehicle=empty,
    )


class FakeVerificationUseCases:
    def __init__(self) -> None:
        self.error: Exception | None = None
        self.unexpected = False
        self.status = status_response()

    def _raise_if_needed(self) -> None:
        if self.unexpected:
            raise RuntimeError("boom")
        if self.error:
            raise self.error

    async def get_verification_status(self, user_id: UUID) -> VerificationStatusResponse:
        self._raise_if_needed()
        return self.status

    async def submit_identity_documents(self, user_id: UUID, request: Any) -> DocumentUploadUrlsResponse:
        self._raise_if_needed()
        return upload_response("id_front", "id_back")

    async def submit_license_documents(self, user_id: UUID, request: Any) -> DocumentUploadUrlsResponse:
        self._raise_if_needed()
        return upload_response("license_front", "license_back")

    async def submit_selfie(self, user_id: UUID, request: Any) -> DocumentUploadUrlsResponse:
        self._raise_if_needed()
        return upload_response("selfie_id")

    async def submit_vehicle_info_and_documents(self, user_id: UUID, request: Any) -> DocumentUploadUrlsResponse:
        self._raise_if_needed()
        return upload_response(
            "registration_doc_front",
            "registration_doc_back",
            "vehicle_photo_front",
            "vehicle_photo_back",
        )

    async def request_verification_review(self, user_id: UUID) -> ReviewSubmissionResponse:
        self._raise_if_needed()
        return ReviewSubmissionResponse(status="UNDER_REVIEW", estimated_time_seconds=30)


@pytest.fixture
def route_state() -> dict[str, Any]:
    return {"use_cases": FakeVerificationUseCases()}


@pytest.fixture
def client(route_state: dict[str, Any]) -> TestClient:
    app = FastAPI()
    app.include_router(router, prefix="/api")
    app.dependency_overrides[get_use_cases] = lambda: route_state["use_cases"]
    app.dependency_overrides[get_current_user] = token_payload
    return TestClient(app)


def test_get_me_route_all_statuses_and_errors(client: TestClient, route_state: dict[str, Any]) -> None:
    for state in ["not_started", "pending", "under_review", "verified", "rejected"]:
        route_state["use_cases"].status = status_response(state)
        response = client.get("/api/v1/verification/me")
        assert response.status_code == 200
        assert response.json()["overall_status"] == state

    route_state["use_cases"].error = DriverNotFoundError("bad state")
    assert client.get("/api/v1/verification/me").status_code == 400
    route_state["use_cases"].error = None
    route_state["use_cases"].unexpected = True
    assert client.get("/api/v1/verification/me").status_code == 500


def test_document_submission_routes_validation_and_domain_errors(
    client: TestClient, route_state: dict[str, Any]
) -> None:
    assert client.post(
        "/api/v1/verification/driver/cnic",
        json={"id_number": "12345", "expiry_date": "2030-01-01"},
    ).status_code == 201
    assert client.post(
        "/api/v1/verification/driver/license",
        json={"license_number": "L-1", "expiry_date": "2030-01-01"},
    ).status_code == 201
    assert client.post("/api/v1/verification/driver/selfie", json={}).status_code == 201
    assert client.post(
        "/api/v1/verification/driver/vehicle",
        json={
            "brand": "Toyota",
            "model": "Yaris",
            "color": "White",
            "vehicle_type": "economy",
            "max_passengers": 4,
            "plate_number": "ABC-123",
            "production_year": 2024,
        },
    ).status_code == 201

    assert client.post(
        "/api/v1/verification/driver/vehicle",
        json={
            "brand": "",
            "model": "Yaris",
            "color": "White",
            "vehicle_type": "economy",
            "plate_number": "ABC-123",
            "production_year": 2024,
        },
    ).status_code == 422

    route_state["use_cases"].error = InvalidDocumentStateError("under review")
    assert client.post("/api/v1/verification/driver/selfie", json={}).status_code == 400
    route_state["use_cases"].error = None
    route_state["use_cases"].unexpected = True
    assert client.post("/api/v1/verification/driver/selfie", json={}).status_code == 500


def test_submit_review_route_success_and_failures(client: TestClient, route_state: dict[str, Any]) -> None:
    response = client.post("/api/v1/verification/submit-review")
    assert response.status_code == 200
    assert response.json()["status"] == "UNDER_REVIEW"

    route_state["use_cases"].error = InvalidDocumentStateError("missing docs")
    assert client.post("/api/v1/verification/submit-review").status_code == 400
    route_state["use_cases"].error = None
    route_state["use_cases"].unexpected = True
    assert client.post("/api/v1/verification/submit-review").status_code == 500
