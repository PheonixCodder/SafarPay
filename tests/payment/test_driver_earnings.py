from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import UUID

from fastapi import FastAPI
from fastapi.testclient import TestClient
from payment.api.router import router as payment_router
from payment.application.schemas import (
    DriverEarningsBreakdownItem,
    DriverEarningsResponse,
    DriverEarningsSummary,
    DriverEarningsTrip,
)
from payment.application.use_cases import DriverEarningsUseCases
from payment.infrastructure.dependencies import get_driver_earnings_uc
from sp.infrastructure.security.dependencies import get_current_driver

DRIVER_ID = UUID("11111111-1111-4111-8111-111111111111")
RIDE_ID = UUID("22222222-2222-4222-8222-222222222222")


def _earnings_response() -> DriverEarningsResponse:
    completed_at = datetime(2026, 5, 22, 12, 30, tzinfo=timezone.utc)
    return DriverEarningsResponse(
        period="today",
        currency="PKR",
        summary=DriverEarningsSummary(
            net_earnings=850.0,
            gross_fares=1000.0,
            commission_total=150.0,
            available_balance=1200.0,
            reserved_balance=0.0,
            completed_trips=1,
            active_minutes=22,
            rating_avg=4.8,
            cash_collected=1000.0,
            platform_collected=0.0,
        ),
        daily_breakdown=[
            DriverEarningsBreakdownItem(
                label="Fri",
                date="2026-05-22",
                gross_fares=1000.0,
                commission_total=150.0,
                net_earnings=850.0,
                completed_trips=1,
            )
        ],
        recent_trips=[
            DriverEarningsTrip(
                ride_id=RIDE_ID,
                completed_at=completed_at,
                pickup_label="Gulberg",
                dropoff_label="DHA Phase 5",
                service_type="CITY_RIDE",
                final_fare=1000.0,
                commission=150.0,
                net_earning=850.0,
                collection_mode="DRIVER_COLLECTED",
            )
        ],
        withdraw_available=False,
        withdraw_unavailable_reason="Withdrawals are not enabled yet.",
    )


class FakeEarningsRepository:
    def __init__(self) -> None:
        self.calls: list[tuple[UUID, str]] = []

    async def get_driver_earnings(self, driver_id: UUID, period: str) -> DriverEarningsResponse:
        self.calls.append((driver_id, period))
        return _earnings_response()


def test_driver_earnings_use_case_scopes_to_driver_and_period() -> None:
    repo = FakeEarningsRepository()
    uc = DriverEarningsUseCases(repo)

    import anyio

    response = anyio.run(uc.get_earnings, DRIVER_ID, "today")

    assert repo.calls == [(DRIVER_ID, "today")]
    assert response.summary.net_earnings == 850.0
    assert response.summary.commission_total == 150.0
    assert response.recent_trips[0].pickup_label == "Gulberg"


def test_driver_earnings_route_returns_payment_read_model() -> None:
    app = FastAPI()
    app.include_router(payment_router, prefix="/api/v1")

    class StubUseCase:
        def __init__(self) -> None:
            self.calls: list[tuple[UUID, str]] = []

        async def get_earnings(self, driver_id: UUID, period: str) -> DriverEarningsResponse:
            self.calls.append((driver_id, period))
            return _earnings_response()

    stub = StubUseCase()
    app.dependency_overrides[get_current_driver] = lambda: DRIVER_ID
    app.dependency_overrides[get_driver_earnings_uc] = lambda: stub

    client = TestClient(app)
    response = client.get("/api/v1/earnings/me?period=today")

    assert response.status_code == 200
    payload: dict[str, Any] = response.json()
    assert payload["summary"]["net_earnings"] == 850.0
    assert payload["recent_trips"][0]["ride_id"] == str(RIDE_ID)
    assert stub.calls == [(DRIVER_ID, "today")]
