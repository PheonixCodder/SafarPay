from __future__ import annotations

import os
import time
from collections.abc import Callable
from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import UUID, uuid4

import httpx
import pytest

from sp.infrastructure.security.jwt import create_access_token

pytestmark = pytest.mark.skipif(
    os.getenv("SAFARPAY_RUN_DOCKER_E2E") != "1",
    reason="Set SAFARPAY_RUN_DOCKER_E2E=1 to run Docker-backed lifecycle tests.",
)

PASSENGER_EMAIL = os.getenv("SAFARPAY_E2E_PASSENGER_EMAIL", "ubaidullahismail09@gmail.com")
DRIVER_EMAIL = os.getenv("SAFARPAY_E2E_DRIVER_EMAIL", "ubaidullahismail0@gmail.com")

RIDE_BASE_URL = os.getenv("SAFARPAY_E2E_RIDE_URL", "http://localhost:8008/api/v1")
BIDDING_BASE_URL = os.getenv("SAFARPAY_E2E_BIDDING_URL", "http://localhost:8002/api/v1/bidding")
LOCATION_BASE_URL = os.getenv("SAFARPAY_E2E_LOCATION_URL", "http://localhost:8003/api/v1/location")
DB_DSN = os.getenv(
    "SAFARPAY_E2E_DB_DSN",
    "postgresql://safarpay:safarpay_secret@localhost:5432/safarpay_db",
)
JWT_SECRET = os.getenv("JWT_SECRET") or ""
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")

PASSENGER_USER_ID = UUID("10000000-0000-0000-0000-000000000001")
DRIVER_USER_ID = UUID("10000000-0000-0000-0000-000000000002")
DRIVER_ID = UUID("10000000-0000-0000-0000-000000000003")
VEHICLE_ID = UUID("10000000-0000-0000-0000-000000000004")

PICKUP = {"lat": 31.5321824, "lng": 74.4165028}
DROPOFF = {"lat": 31.4938223, "lng": 74.3689832}

if not JWT_SECRET:
    env_file = os.path.join(os.getcwd(), ".env")
    if os.path.exists(env_file):
        with open(env_file, encoding="utf-8") as file:
            for line in file:
                if line.startswith("JWT_SECRET="):
                    JWT_SECRET = line.split("=", 1)[1].strip().strip('"').strip("'")
                    break
JWT_SECRET = JWT_SECRET or "change-me-in-production"


class ApiClient:
    def __init__(self, token: str) -> None:
        self._client = httpx.Client(timeout=15)
        self._headers = {"Authorization": f"Bearer {token}"}

    def get(self, url: str, **kwargs: Any) -> httpx.Response:
        return self._client.get(url, headers=self._headers, **kwargs)

    def post(self, url: str, **kwargs: Any) -> httpx.Response:
        return self._client.post(url, headers=self._headers, **kwargs)

    def close(self) -> None:
        self._client.close()


@pytest.fixture(scope="module")
def psycopg_module() -> Any:
    return pytest.importorskip("psycopg")


@pytest.fixture(scope="module")
def e2e_context(psycopg_module: Any) -> dict[str, UUID]:
    assert_services_are_healthy()
    with psycopg_module.connect(DB_DSN, autocommit=False) as conn:
        context = seed_lifecycle_context(conn)
        conn.commit()
    return context


@pytest.fixture()
def passenger_client(e2e_context: dict[str, UUID]) -> ApiClient:
    token = make_token(e2e_context["passenger_user_id"], PASSENGER_EMAIL, "passenger")
    client = ApiClient(token)
    yield client
    client.close()


@pytest.fixture()
def driver_client(e2e_context: dict[str, UUID]) -> ApiClient:
    token = make_token(e2e_context["driver_user_id"], DRIVER_EMAIL, "driver")
    client = ApiClient(token)
    yield client
    client.close()


def test_fixed_ride_lifecycle_reaches_completed_with_payment_side_effects(
    e2e_context: dict[str, UUID],
    passenger_client: ApiClient,
    driver_client: ApiClient,
    psycopg_module: Any,
) -> None:
    driver_id = e2e_context["driver_id"]
    set_driver_online(driver_client, driver_id)
    ride = create_city_ride(passenger_client, pricing_mode="FIXED", min_price=540, max_price=540)
    ride_id = UUID(ride["id"])

    wait_for_driver_request(driver_client, ride_id)
    accepted = post_ok(driver_client, f"{RIDE_BASE_URL}/rides/{ride_id}/accept", json={}).json()
    assert accepted["status"] == "ACCEPTED"
    assert accepted["assigned_driver_id"] == str(driver_id)

    complete_ride(driver_client, ride_id, final_price=540)
    assert_ride_completed(passenger_client, ride_id, driver_id)
    assert_financial_side_effects(psycopg_module, ride_id, driver_id)
    assert_no_active_driver_ride(driver_client)


def test_hybrid_ride_lifecycle_accepts_driver_offer_and_reaches_completed(
    e2e_context: dict[str, UUID],
    passenger_client: ApiClient,
    driver_client: ApiClient,
    psycopg_module: Any,
) -> None:
    driver_id = e2e_context["driver_id"]
    set_driver_online(driver_client, driver_id)
    ride = create_city_ride(passenger_client, pricing_mode="HYBRID", min_price=500, max_price=700)
    ride_id = UUID(ride["id"])

    wait_for_driver_request(driver_client, ride_id)
    session = wait_for_bidding_session(passenger_client, ride_id)
    session_id = UUID(session.get("id") or session["session_id"])

    bid = post_ok(
        driver_client,
        f"{BIDDING_BASE_URL}/sessions/{session_id}/bids",
        json={"bid_amount": 620, "eta_minutes": 8, "message": "E2E lifecycle offer"},
        expected=201,
    ).json()
    bid_id = UUID(bid["id"])

    passenger_session = get_ok(passenger_client, f"{BIDDING_BASE_URL}/sessions/{session_id}").json()
    assert any(item["id"] == str(bid_id) for item in passenger_session["bids"])

    post_ok(
        passenger_client,
        f"{BIDDING_BASE_URL}/sessions/{session_id}/accept",
        json={"bid_id": str(bid_id)},
    )

    wait_for_condition(
        lambda: get_ok(passenger_client, f"{RIDE_BASE_URL}/rides/{ride_id}").json()["assigned_driver_id"]
        == str(driver_id),
        description="hybrid ride assignment",
    )
    complete_ride(driver_client, ride_id, final_price=620)
    assert_ride_completed(passenger_client, ride_id, driver_id)
    assert_financial_side_effects(psycopg_module, ride_id, driver_id)
    assert_no_active_driver_ride(driver_client)


def assert_services_are_healthy() -> None:
    services = {
        "ride": "http://localhost:8008/health",
        "bidding": "http://localhost:8002/health",
        "location": "http://localhost:8003/health",
        "payment": "http://localhost:8009/health",
    }
    with httpx.Client(timeout=5) as client:
        for service, url in services.items():
            try:
                response = client.get(url)
            except httpx.HTTPError as exc:
                pytest.skip(f"{service} service is not reachable at {url}: {exc}")
            if response.status_code != 200:
                pytest.skip(f"{service} service is not healthy: HTTP {response.status_code}")


def seed_lifecycle_context(conn: Any) -> dict[str, UUID]:
    now = datetime.now(timezone.utc)
    passenger_user_id = ensure_user(
        conn, PASSENGER_USER_ID, PASSENGER_EMAIL, "passenger", "SafarPay E2E Passenger", now
    )
    driver_user_id = ensure_user(
        conn, DRIVER_USER_ID, DRIVER_EMAIL, "driver", "SafarPay E2E Driver", now
    )
    driver_id = ensure_verified_driver(conn, driver_user_id, now)
    vehicle_id = ensure_vehicle(conn, now)
    ensure_driver_vehicle(conn, driver_id, vehicle_id, now)
    ensure_driver_capability(conn, driver_id, vehicle_id, now)
    ensure_wallet_and_policy(conn, driver_id, now)
    cancel_existing_active_rides(conn, passenger_user_id, driver_id)
    return {
        "passenger_user_id": passenger_user_id,
        "driver_user_id": driver_user_id,
        "driver_id": driver_id,
    }


def ensure_user(conn: Any, fallback_id: UUID, email: str, role: str, full_name: str, now: datetime) -> UUID:
    existing = conn.execute("SELECT id FROM auth.users WHERE email = %s", (email,)).fetchone()
    if existing:
        user_id = existing[0]
        conn.execute(
            """
            UPDATE auth.users
            SET full_name = %s,
                role = %s,
                is_active = true,
                is_verified = true,
                updated_at = %s
            WHERE id = %s
            """,
            (full_name, role, now, user_id),
        )
        return user_id

    row = conn.execute(
        """
        INSERT INTO auth.users
            (id, full_name, email, phone, role, is_active, is_verified, created_at, updated_at)
        VALUES (%s, %s, %s, NULL, %s, true, true, %s, %s)
        RETURNING id
        """,
        (fallback_id, full_name, email, role, now, now),
    ).fetchone()
    return row[0]


def ensure_verified_driver(conn: Any, driver_user_id: UUID, now: datetime) -> UUID:
    existing = conn.execute(
        "SELECT id FROM verification.drivers WHERE user_id = %s",
        (driver_user_id,),
    ).fetchone()
    if existing:
        driver_id = existing[0]
        conn.execute(
            """
            UPDATE verification.drivers
            SET verification_status = 'VERIFIED',
                updated_at = %s
            WHERE id = %s
            """,
            (now, driver_id),
        )
    else:
        driver_id = DRIVER_ID
        conn.execute(
            """
            INSERT INTO verification.drivers
                (id, user_id, verification_status, review_attempts, created_at, updated_at)
            VALUES (%s, %s, 'VERIFIED', 0, %s, %s)
            """,
            (driver_id, driver_user_id, now, now),
        )

    conn.execute(
        """
        INSERT INTO verification.driver_stats
            (driver_id, rating_avg, total_rides, acceptance_rate, cancellation_rate, online_minutes_today)
        VALUES (%s, 4.90, 42, 95.00, 2.00, 0)
        ON CONFLICT (driver_id) DO UPDATE
        SET rating_avg = EXCLUDED.rating_avg,
            total_rides = EXCLUDED.total_rides,
            acceptance_rate = EXCLUDED.acceptance_rate,
            cancellation_rate = EXCLUDED.cancellation_rate,
            online_minutes_today = EXCLUDED.online_minutes_today
        """,
        (driver_id,),
    )
    return driver_id


def ensure_vehicle(conn: Any, now: datetime) -> UUID:
    conn.execute(
        """
        INSERT INTO verification.vehicles
            (id, brand, model, year, color, plate_number, max_passengers, vehicle_type,
             verification_status, is_active, created_at, updated_at)
        VALUES (%s, 'Toyota', 'Yaris', 2022, 'White', 'SP-E2E-001', 4, 'CAR',
                'VERIFIED', true, %s, %s)
        ON CONFLICT (plate_number) DO UPDATE
        SET verification_status = 'VERIFIED',
            is_active = true,
            vehicle_type = 'CAR',
            updated_at = EXCLUDED.updated_at
        """,
        (VEHICLE_ID, now, now),
    )
    row = conn.execute("SELECT id FROM verification.vehicles WHERE plate_number = 'SP-E2E-001'").fetchone()
    return row[0]


def ensure_driver_vehicle(conn: Any, driver_id: UUID, vehicle_id: UUID, now: datetime) -> None:
    conn.execute(
        """
        INSERT INTO verification.driver_vehicles
            (id, driver_id, vehicle_id, vehicle_type, is_currently_selected, assigned_at, created_at, updated_at)
        VALUES (%s, %s, %s, 'CAR', true, %s, %s, %s)
        ON CONFLICT (driver_id, vehicle_type) DO UPDATE
        SET vehicle_id = EXCLUDED.vehicle_id,
            is_currently_selected = true,
            updated_at = EXCLUDED.updated_at
        """,
        (UUID("10000000-0000-0000-0000-000000000005"), driver_id, vehicle_id, now, now, now),
    )


def ensure_driver_capability(conn: Any, driver_id: UUID, vehicle_id: UUID, now: datetime) -> None:
    conn.execute(
        """
        INSERT INTO verification.driver_service_capabilities
            (id, driver_id, vehicle_id, service_type, is_active, created_at, updated_at)
        VALUES (%s, %s, %s, 'CITY_RIDE', true, %s, %s)
        ON CONFLICT (driver_id, service_type, vehicle_id) DO UPDATE
        SET is_active = true,
            updated_at = EXCLUDED.updated_at
        """,
        (UUID("10000000-0000-0000-0000-000000000006"), driver_id, vehicle_id, now, now),
    )


def ensure_wallet_and_policy(conn: Any, driver_id: UUID, now: datetime) -> None:
    conn.execute(
        """
        INSERT INTO payment.wallets
            (id, driver_id, available_balance, reserved_balance, current_balance,
             currency, status, negative_limit, max_reserved_limit, created_at, updated_at)
        VALUES (%s, %s, 10000.00, 0.00, 10000.00, 'PKR', 'ACTIVE', 0.00, 100000.00, %s, %s)
        ON CONFLICT (driver_id) DO UPDATE
        SET available_balance = GREATEST(payment.wallets.available_balance, 10000.00),
            current_balance = GREATEST(payment.wallets.current_balance, 10000.00),
            status = 'ACTIVE',
            updated_at = EXCLUDED.updated_at
        """,
        (UUID("10000000-0000-0000-0000-000000000007"), driver_id, now, now),
    )
    conn.execute(
        """
        INSERT INTO payment.commission_policies
            (id, name, rate, currency, is_active, effective_from, created_at, updated_at)
        VALUES (%s, 'E2E Standard Commission', 0.1500, 'PKR', true, %s, %s, %s)
        ON CONFLICT (id) DO UPDATE
        SET rate = 0.1500,
            is_active = true,
            updated_at = EXCLUDED.updated_at
        """,
        (UUID("10000000-0000-0000-0000-000000000008"), now - timedelta(days=1), now, now),
    )


def cancel_existing_active_rides(conn: Any, passenger_user_id: UUID, driver_id: UUID) -> None:
    conn.execute(
        """
        UPDATE service_request.service_requests
        SET status = 'CANCELLED',
            cancelled_at = COALESCE(cancelled_at, now()),
            cancellation_reason = COALESCE(cancellation_reason, 'E2E setup cleanup')
        WHERE status IN ('MATCHING', 'ACCEPTED', 'ARRIVING', 'IN_PROGRESS')
          AND (user_id = %s OR assigned_driver_id = %s)
        """,
        (passenger_user_id, driver_id),
    )


def make_token(user_id: UUID, email: str, role: str) -> str:
    return create_access_token(
        user_id=user_id,
        email=email,
        role=role,
        session_id=uuid4(),
        secret=JWT_SECRET,
        algorithm=JWT_ALGORITHM,
        expiration_minutes=60,
    )


def set_driver_online(driver_client: ApiClient, driver_id: UUID) -> None:
    post_ok(driver_client, f"{LOCATION_BASE_URL}/drivers/{driver_id}/status", json={"status": "ONLINE"})
    post_ok(
        driver_client,
        f"{LOCATION_BASE_URL}/drivers/{driver_id}/location",
        json={
            "lat": PICKUP["lat"],
            "lng": PICKUP["lng"],
            "accuracy": 6.0,
            "speed": 0.0,
            "heading": 90.0,
            "ts": int(time.time() * 1000),
        },
        expected=204,
    )


def create_city_ride(
    passenger_client: ApiClient,
    *,
    pricing_mode: str,
    min_price: float,
    max_price: float,
) -> dict[str, Any]:
    payload = {
        "service_type": "CITY_RIDE",
        "category": "MINI",
        "pricing_mode": pricing_mode,
        "baseline_min_price": min_price,
        "baseline_max_price": max_price,
        "auto_accept_driver": False,
        "passenger_payment_method": "CASH",
        "stops": [
            {
                "sequence_order": 1,
                "stop_type": "PICKUP",
                "latitude": PICKUP["lat"],
                "longitude": PICKUP["lng"],
                "place_name": "E2E Pickup",
                "address_line_1": "E2E Pickup Address",
                "city": "Lahore",
                "country": "PK",
            },
            {
                "sequence_order": 2,
                "stop_type": "DROPOFF",
                "latitude": DROPOFF["lat"],
                "longitude": DROPOFF["lng"],
                "place_name": "E2E Dropoff",
                "address_line_1": "E2E Dropoff Address",
                "city": "Lahore",
                "country": "PK",
            },
        ],
        "detail": {
            "service_type": "CITY_RIDE",
            "passenger_count": 1,
            "is_ac": False,
            "preferred_vehicle_type": "CAR",
            "driver_gender_preference": "NO_PREFERENCE",
            "is_shared_ride": False,
            "is_pet_allowed": False,
            "requires_otp_start": False,
            "requires_otp_end": False,
            "estimated_price": max_price,
        },
    }
    return post_ok(passenger_client, f"{RIDE_BASE_URL}/rides", json=payload, expected=201).json()


def wait_for_driver_request(driver_client: ApiClient, ride_id: UUID) -> None:
    def condition() -> bool:
        response = get_ok(
            driver_client,
            f"{RIDE_BASE_URL}/driver/requests",
            params={"lat": PICKUP["lat"], "lng": PICKUP["lng"], "radius_km": 5.0, "limit": 20},
        )
        return any(item["id"] == str(ride_id) for item in response.json())

    wait_for_condition(condition, description=f"driver request for ride {ride_id}")


def wait_for_bidding_session(passenger_client: ApiClient, ride_id: UUID) -> dict[str, Any]:
    session: dict[str, Any] | None = None

    def condition() -> bool:
        nonlocal session
        response = passenger_client.get(f"{BIDDING_BASE_URL}/sessions/by-ride/{ride_id}")
        if response.status_code == 200:
            session = response.json()
            return True
        if response.status_code == 404:
            return False
        response.raise_for_status()
        return False

    wait_for_condition(condition, description=f"bidding session for ride {ride_id}", timeout_seconds=25)
    assert session is not None
    return session


def complete_ride(driver_client: ApiClient, ride_id: UUID, *, final_price: float) -> None:
    ride = get_ok(driver_client, f"{RIDE_BASE_URL}/rides/{ride_id}").json()
    pickup_stop = ride["pickup_stop"]
    assert pickup_stop is not None
    post_ok(driver_client, f"{RIDE_BASE_URL}/stops/{pickup_stop['id']}/arrived")
    started = post_ok(driver_client, f"{RIDE_BASE_URL}/rides/{ride_id}/start", json={}).json()
    assert started["status"] == "IN_PROGRESS"
    completed = post_ok(
        driver_client,
        f"{RIDE_BASE_URL}/rides/{ride_id}/complete",
        json={"final_price": final_price},
    ).json()
    assert completed["status"] == "COMPLETED"


def assert_ride_completed(passenger_client: ApiClient, ride_id: UUID, driver_id: UUID) -> None:
    ride = get_ok(passenger_client, f"{RIDE_BASE_URL}/rides/{ride_id}").json()
    assert ride["status"] == "COMPLETED"
    assert ride["assigned_driver_id"] == str(driver_id)
    assert ride["completed_at"] is not None


def assert_financial_side_effects(psycopg_module: Any, ride_id: UUID, driver_id: UUID) -> None:
    with psycopg_module.connect(DB_DSN, autocommit=True) as conn:
        payment = conn.execute(
            "SELECT status, amount_final FROM payment.ride_payments WHERE ride_id = %s",
            (ride_id,),
        ).fetchone()
        assert payment is not None
        assert payment[0] in {"PAID", "COLLECTION_UNCONFIRMED"}
        assert float(payment[1]) > 0

        reservation = conn.execute(
            """
            SELECT status, reserved_amount, captured_amount
            FROM payment.commission_reservations
            WHERE ride_id = %s AND driver_id = %s
            """,
            (ride_id, driver_id),
        ).fetchone()
        assert reservation is not None
        assert reservation[0] == "CAPTURED"
        assert float(reservation[1]) > 0
        assert float(reservation[2]) > 0


def assert_no_active_driver_ride(driver_client: ApiClient) -> None:
    response = driver_client.get(
        f"{RIDE_BASE_URL}/driver/rides/active",
        params={"lat": PICKUP["lat"], "lng": PICKUP["lng"]},
    )
    if response.status_code == 404:
        return
    response.raise_for_status()
    body = response.json()
    assert body in ({}, None) or body.get("status") not in {"ACCEPTED", "ARRIVING", "IN_PROGRESS"}


def wait_for_condition(
    condition: Callable[[], bool],
    *,
    description: str,
    timeout_seconds: float = 15,
    interval_seconds: float = 0.5,
) -> None:
    deadline = time.monotonic() + timeout_seconds
    last_error: Exception | None = None
    while time.monotonic() < deadline:
        try:
            if condition():
                return
        except Exception as exc:  # noqa: BLE001
            last_error = exc
        time.sleep(interval_seconds)
    if last_error is not None:
        raise AssertionError(f"Timed out waiting for {description}; last error: {last_error}") from last_error
    raise AssertionError(f"Timed out waiting for {description}")


def get_ok(client: ApiClient, url: str, **kwargs: Any) -> httpx.Response:
    response = client.get(url, **kwargs)
    assert response.status_code == 200, response.text
    return response


def post_ok(client: ApiClient, url: str, *, expected: int = 200, **kwargs: Any) -> httpx.Response:
    response = client.post(url, **kwargs)
    assert response.status_code == expected, response.text
    return response
