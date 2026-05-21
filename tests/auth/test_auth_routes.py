from __future__ import annotations

from datetime import date, datetime, timedelta, timezone
from typing import Any
from uuid import UUID, uuid4

import pytest
from auth.api.router import router
from auth.domain.exceptions import (
    GoogleTokenError,
    InvalidSessionError,
    InvalidVerificationTokenError,
    OTPExpiredError,
    OTPInvalidError,
    OTPMaxAttemptsError,
    OTPRateLimitError,
    UserAlreadyExistsError,
)
from auth.domain.models import Session, User, UserRole
from auth.infrastructure.dependencies import (
    get_google_verify_use_case,
    get_google_existing_phone_use_case,
    get_link_phone_use_case,
    get_otp_rate_limiter,
    get_refresh_use_case,
    get_register_use_case,
    get_send_otp_use_case,
    get_session_repo,
    get_update_profile_use_case,
    get_user_repo,
    get_verify_otp_use_case,
)
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sp.infrastructure.security.dependencies import get_current_user
from sp.infrastructure.security.jwt import TokenPayload

USER_ID = uuid4()
SESSION_ID = uuid4()


def token_payload() -> TokenPayload:
    now = datetime.now(timezone.utc)
    return TokenPayload(
        user_id=USER_ID,
        email="p@example.com",
        role="passenger",
        session_id=SESSION_ID,
        iat=now,
        exp=now + timedelta(minutes=15),
    )


class FakeRateLimiter:
    def __init__(self) -> None:
        self.send_error: Exception | None = None
        self.verify_error: Exception | None = None

    async def check_send_limit(self, phone: str) -> None:
        if self.send_error:
            raise self.send_error

    async def check_verify_limit(self, ip_address: str) -> None:
        if self.verify_error:
            raise self.verify_error


class FakeOTPUseCase:
    def __init__(
        self,
        error: Exception | None = None,
        result: dict[str, Any] | str | None = None,
    ) -> None:
        self.error = error
        self.result = result

    async def execute(self, *args: Any, **kwargs: Any) -> Any:
        if self.error:
            raise self.error
        return self.result or {
            "next_step": "complete_profile",
            "registration_token": "registration-token",
        }


class FakeTokenUseCase:
    def __init__(self, error: Exception | None = None, phone_required: bool = False) -> None:
        self.error = error
        self.phone_required = phone_required

    async def execute(self, *args: Any, **kwargs: Any) -> dict[str, Any]:
        if self.error:
            raise self.error
        return {
            "access_token": "access",
            "refresh_token": "refresh",
            "expires_in": 900,
            "phone_required": self.phone_required,
        }


class FakeUpdateProfileUseCase:
    def __init__(self, error: Exception | None = None) -> None:
        self.error = error
        self.calls: list[dict[str, Any]] = []

    async def execute(self, user_id: UUID, **kwargs: Any) -> User:
        if self.error:
            raise self.error
        self.calls.append({"user_id": user_id, **kwargs})
        return User(
            id=user_id,
            role=UserRole.PASSENGER,
            full_name=kwargs.get("full_name") or "Passenger",
            email=kwargs.get("email") or "p@example.com",
            phone="+923001234567",
            gender=kwargs.get("gender"),
            date_of_birth=kwargs.get("date_of_birth"),
            is_verified=True,
        )


class FakeSessionRepo:
    def __init__(self) -> None:
        self.other_id = uuid4()
        self.sessions = {
            SESSION_ID: Session(
                id=SESSION_ID,
                user_id=USER_ID,
                refresh_token_hash="hash",
                expires_at=datetime.now(timezone.utc) + timedelta(days=1),
                user_agent="ua-current",
                ip_address="127.0.0.1",
            ),
            self.other_id: Session(
                id=self.other_id,
                user_id=USER_ID,
                refresh_token_hash="other",
                expires_at=datetime.now(timezone.utc) + timedelta(days=1),
                user_agent="ua-other",
                ip_address="127.0.0.2",
            ),
        }

    async def find_active_by_user(self, user_id: UUID) -> list[Session]:
        return [s for s in self.sessions.values() if s.user_id == user_id and not s.is_revoked]

    async def find_by_id(self, session_id: UUID) -> Session | None:
        return self.sessions.get(session_id)

    async def find_by_hash(self, token_hash: str) -> Session | None:
        return next((s for s in self.sessions.values() if s.refresh_token_hash == token_hash), None)

    async def update(self, session: Session) -> Session:
        self.sessions[session.id] = session
        return session


class FakeUserRepo:
    def __init__(self, user: User | None = None) -> None:
        self.user = user or User(
            id=USER_ID,
            role=UserRole.PASSENGER,
            full_name="Passenger",
            email="p@example.com",
            phone="+923001234567",
            gender="male",
            date_of_birth=date(1998, 5, 17),
            is_verified=True,
        )

    async def find_by_id(self, user_id: UUID) -> User | None:
        return self.user if user_id == self.user.id else None


@pytest.fixture
def route_state() -> dict[str, Any]:
    return {
        "rate_limiter": FakeRateLimiter(),
        "send_otp": FakeOTPUseCase(),
        "verify_otp": FakeOTPUseCase(),
        "register": FakeTokenUseCase(),
        "google_verify": FakeTokenUseCase(phone_required=True),
        "google_existing_phone": FakeTokenUseCase(),
        "link_phone": FakeTokenUseCase(),
        "refresh": FakeTokenUseCase(),
        "update_profile": FakeUpdateProfileUseCase(),
        "sessions": FakeSessionRepo(),
        "users": FakeUserRepo(),
    }


@pytest.fixture
def client(route_state: dict[str, Any]) -> TestClient:
    app = FastAPI()
    app.include_router(router, prefix="/api/v1/auth")
    app.dependency_overrides[get_otp_rate_limiter] = lambda: route_state["rate_limiter"]
    app.dependency_overrides[get_send_otp_use_case] = lambda: route_state["send_otp"]
    app.dependency_overrides[get_verify_otp_use_case] = lambda: route_state["verify_otp"]
    app.dependency_overrides[get_register_use_case] = lambda: route_state["register"]
    app.dependency_overrides[get_google_verify_use_case] = lambda: route_state["google_verify"]
    app.dependency_overrides[get_google_existing_phone_use_case] = lambda: route_state["google_existing_phone"]
    app.dependency_overrides[get_link_phone_use_case] = lambda: route_state["link_phone"]
    app.dependency_overrides[get_refresh_use_case] = lambda: route_state["refresh"]
    app.dependency_overrides[get_update_profile_use_case] = lambda: route_state["update_profile"]
    app.dependency_overrides[get_session_repo] = lambda: route_state["sessions"]
    app.dependency_overrides[get_user_repo] = lambda: route_state["users"]
    app.dependency_overrides[get_current_user] = token_payload
    return TestClient(app)


def test_send_otp_route_success_validation_rate_limit_and_failure(
    client: TestClient, route_state: dict[str, Any]
) -> None:
    assert client.post("/api/v1/auth/otp/send", json={"phone": "+923001234567"}).status_code == 200
    assert client.post("/api/v1/auth/otp/send", json={"phone": "bad"}).status_code == 422

    route_state["rate_limiter"].send_error = OTPRateLimitError("too many")
    response = client.post("/api/v1/auth/otp/send", json={"phone": "+923001234567"})
    assert response.status_code == 429

    route_state["rate_limiter"].send_error = None
    route_state["send_otp"].error = RuntimeError("provider down")
    assert client.post("/api/v1/auth/otp/send", json={"phone": "+923001234567"}).status_code == 500


def test_verify_otp_route_success_and_error_mappings(
    client: TestClient, route_state: dict[str, Any]
) -> None:
    response = client.post(
        "/api/v1/auth/otp/verify",
        json={"phone": "+923001234567", "code": "123456"},
    )
    assert response.status_code == 200
    assert response.json()["next_step"] == "complete_profile"
    assert response.json()["registration_token"] == "registration-token"
    assert client.post(
        "/api/v1/auth/otp/verify",
        json={"phone": "+923001234567", "code": "123"},
    ).status_code == 422

    route_state["verify_otp"] = FakeOTPUseCase(
        result={
            "next_step": "login",
            "access_token": "access",
            "refresh_token": "refresh",
            "expires_in": 900,
            "phone_required": False,
        }
    )
    login_response = client.post(
        "/api/v1/auth/otp/verify",
        json={"phone": "+923001234567", "code": "123456"},
    )
    assert login_response.status_code == 200
    assert login_response.json()["next_step"] == "login"
    assert login_response.json()["access_token"] == "access"
    assert "refresh_token=refresh" in login_response.headers["set-cookie"]

    for error, expected in [
        (OTPRateLimitError("limited"), 429),
        (OTPExpiredError("expired"), 400),
        (OTPInvalidError("bad"), 400),
        (OTPMaxAttemptsError("max"), 429),
    ]:
        route_state["rate_limiter"].verify_error = error if isinstance(error, OTPRateLimitError) else None
        route_state["verify_otp"].error = None if isinstance(error, OTPRateLimitError) else error
        assert client.post(
            "/api/v1/auth/otp/verify",
            json={"phone": "+923001234567", "code": "123456"},
        ).status_code == expected


def test_register_google_link_refresh_cookie_routes(
    client: TestClient, route_state: dict[str, Any]
) -> None:
    register = client.post(
        "/api/v1/auth/register",
        json={
            "registration_token": "vt",
            "full_name": "Passenger",
            "email": "p@example.com",
            "gender": "male",
            "date_of_birth": "1998-05-17",
        },
    )
    assert register.status_code == 201
    assert "refresh_token=refresh" in register.headers["set-cookie"]
    assert client.post(
        "/api/v1/auth/register",
        json={
            "registration_token": "vt",
            "full_name": "x",
            "email": "bad",
            "gender": "male",
            "date_of_birth": "1998-05-17",
        },
    ).status_code == 422

    route_state["register"].error = InvalidVerificationTokenError()
    assert client.post(
        "/api/v1/auth/register",
        json={
            "registration_token": "vt",
            "full_name": "Passenger",
            "email": "p@example.com",
            "gender": "male",
            "date_of_birth": "1998-05-17",
        },
    ).status_code == 400
    route_state["register"].error = UserAlreadyExistsError()
    assert client.post(
        "/api/v1/auth/register",
        json={
            "registration_token": "vt",
            "full_name": "Passenger",
            "email": "p@example.com",
            "gender": "male",
            "date_of_birth": "1998-05-17",
        },
    ).status_code == 409

    google = client.post("/api/v1/auth/google/verify-token", json={"id_token": "google"})
    assert google.status_code == 200
    assert google.json()["phone_required"] is True
    route_state["google_verify"] = FakeOTPUseCase(
        result={
            "next_step": "verify_existing_phone",
            "masked_phone": "******8782",
            "google_login_token": "google-login-token",
            "phone_required": False,
        }
    )
    google_existing = client.post("/api/v1/auth/google/verify-token", json={"id_token": "google"})
    assert google_existing.status_code == 200
    assert google_existing.json()["next_step"] == "verify_existing_phone"
    assert google_existing.json()["masked_phone"] == "******8782"
    assert google_existing.json()["google_login_token"] == "google-login-token"
    assert "refresh_token" not in google_existing.headers.get("set-cookie", "")
    route_state["google_verify"] = FakeTokenUseCase(phone_required=True)
    route_state["google_verify"].error = GoogleTokenError("bad google")
    assert client.post("/api/v1/auth/google/verify-token", json={"id_token": "google"}).status_code == 401

    verify_existing = client.post(
        "/api/v1/auth/google/verify-existing-phone",
        json={"google_login_token": "google-login-token", "code": "123456"},
    )
    assert verify_existing.status_code == 200
    assert "refresh_token=refresh" in verify_existing.headers["set-cookie"]
    route_state["google_existing_phone"].error = InvalidVerificationTokenError()
    assert client.post(
        "/api/v1/auth/google/verify-existing-phone",
        json={"google_login_token": "bad", "code": "123456"},
    ).status_code == 400

    assert client.post("/api/v1/auth/google/link-phone", json={"verification_token": "vt"}).status_code == 200
    route_state["link_phone"].error = InvalidVerificationTokenError()
    assert client.post("/api/v1/auth/google/link-phone", json={"verification_token": "vt"}).status_code == 400

    assert client.post("/api/v1/auth/refresh", cookies={"refresh_token": "old"}).status_code == 200
    assert client.post("/api/v1/auth/refresh", json={"refresh_token": "old"}).status_code == 200
    assert client.post("/api/v1/auth/refresh").status_code == 400
    route_state["refresh"].error = InvalidSessionError()
    assert client.post("/api/v1/auth/refresh", cookies={"refresh_token": "old"}).status_code == 401


def test_session_logout_and_profile_routes(client: TestClient, route_state: dict[str, Any]) -> None:
    sessions = client.get("/api/v1/auth/sessions")
    assert sessions.status_code == 200
    assert any(item["is_current"] for item in sessions.json())

    other_id = route_state["sessions"].other_id
    assert client.delete(f"/api/v1/auth/sessions/{other_id}").status_code == 204
    assert route_state["sessions"].sessions[other_id].is_revoked
    assert client.delete(f"/api/v1/auth/sessions/{SESSION_ID}").status_code == 400
    assert client.delete(f"/api/v1/auth/sessions/{uuid4()}").status_code == 404

    logout = client.post("/api/v1/auth/logout")
    assert logout.status_code == 204
    assert route_state["sessions"].sessions[SESSION_ID].is_revoked
    assert "refresh_token" in logout.headers["set-cookie"]

    profile = client.get("/api/v1/auth/me")
    assert profile.status_code == 200
    assert profile.json()["is_onboarded"] is True
    assert profile.json()["gender"] == "male"
    assert profile.json()["date_of_birth"] == "1998-05-17"

    update_profile = client.patch(
        "/api/v1/auth/me",
        json={
            "full_name": "Updated Passenger",
            "email": "updated@example.com",
            "gender": "female",
            "date_of_birth": "1997-07-09",
            "phone": "+923009999999",
        },
    )
    assert update_profile.status_code == 200
    assert update_profile.json()["full_name"] == "Updated Passenger"
    assert update_profile.json()["email"] == "updated@example.com"
    assert update_profile.json()["gender"] == "female"
    assert update_profile.json()["date_of_birth"] == "1997-07-09"
    assert route_state["update_profile"].calls[-1]["user_id"] == USER_ID
    assert "phone" not in route_state["update_profile"].calls[-1]

    route_state["update_profile"].error = UserAlreadyExistsError()
    assert client.patch("/api/v1/auth/me", json={"email": "taken@example.com"}).status_code == 409

    route_state["users"].user = User(id=uuid4(), role=UserRole.PASSENGER)
    assert client.get("/api/v1/auth/me").status_code == 404
