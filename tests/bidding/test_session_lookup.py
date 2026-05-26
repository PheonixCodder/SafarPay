from __future__ import annotations

from datetime import datetime, timedelta, timezone
from uuid import UUID, uuid4

import pytest
from fastapi import HTTPException
from sp.infrastructure.security.jwt import TokenPayload

from bidding.api.router import get_bids_for_ride_session
from bidding.domain.models import BiddingSession, BiddingSessionStatus, PricingMode


class FakeSessionRepository:
    def __init__(self, session: BiddingSession | None) -> None:
        self.session = session
        self.requested_ride_id: UUID | None = None

    async def find_by_ride(self, ride_id: UUID) -> BiddingSession | None:
        self.requested_ride_id = ride_id
        return self.session


class FakeGetItemBidsUseCase:
    def __init__(self) -> None:
        self.requested_session_id: UUID | None = None

    async def execute(self, session_id: UUID) -> dict[str, object]:
        self.requested_session_id = session_id
        return {
            "session_id": session_id,
            "service_request_id": uuid4(),
            "status": "OPEN",
            "pricing_mode": "HYBRID",
            "passenger_user_id": uuid4(),
            "baseline_price": 250.0,
            "bids": [],
            "lowest_bid": None,
            "counter_offers": None,
        }


def _token(user_id: UUID, role: str = "passenger") -> TokenPayload:
    now = datetime.now(timezone.utc)
    return TokenPayload(
        user_id=user_id,
        email="passenger@example.com",
        role=role,
        session_id=uuid4(),
        iat=now,
        exp=now + timedelta(minutes=15),
    )


@pytest.mark.asyncio
async def test_get_bids_for_ride_session_returns_owned_passenger_session() -> None:
    passenger_id = uuid4()
    ride_id = uuid4()
    session = BiddingSession(
        id=uuid4(),
        service_request_id=ride_id,
        status=BiddingSessionStatus.OPEN,
        opened_at=datetime.now(timezone.utc),
        passenger_user_id=passenger_id,
        pricing_mode=PricingMode.HYBRID,
        baseline_price=250.0,
    )
    repo = FakeSessionRepository(session)
    use_case = FakeGetItemBidsUseCase()

    response = await get_bids_for_ride_session(
        ride_id=ride_id,
        current_user=_token(passenger_id),
        current_driver_id=None,
        session_repo=repo,
        use_case=use_case,
    )

    assert repo.requested_ride_id == ride_id
    assert use_case.requested_session_id == session.id
    assert response["session_id"] == session.id


@pytest.mark.asyncio
async def test_get_bids_for_ride_session_rejects_unrelated_passenger() -> None:
    session = BiddingSession(
        id=uuid4(),
        service_request_id=uuid4(),
        status=BiddingSessionStatus.OPEN,
        opened_at=datetime.now(timezone.utc),
        passenger_user_id=uuid4(),
        pricing_mode=PricingMode.HYBRID,
    )

    with pytest.raises(HTTPException) as exc:
        await get_bids_for_ride_session(
            ride_id=session.service_request_id,
            current_user=_token(uuid4()),
            current_driver_id=None,
            session_repo=FakeSessionRepository(session),
            use_case=FakeGetItemBidsUseCase(),
        )

    assert exc.value.status_code == 403
