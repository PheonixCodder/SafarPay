from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, cast
from uuid import UUID, uuid4

import pytest
from bidding.application.use_cases import (
    DriverAcceptCounterOfferUseCase,
    PassengerCounterOfferUseCase,
)
from bidding.domain.models import (
    Bid,
    BiddingSession,
    BiddingSessionStatus,
    CounterOffer,
    CounterOfferStatus,
    PricingMode,
)
from bidding.infrastructure.websocket_manager import BiddingEvent


class FakeSessionRepo:
    def __init__(self, session: BiddingSession) -> None:
        self.session = session
        self.updated_status: str | None = None

    async def find_by_id(self, session_id):
        return self.session if session_id == self.session.id else None

    async def update_status(self, session_id, status):
        self.updated_status = status


class FakeNested:
    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False


class FakeBidRepo:
    def __init__(self) -> None:
        self.saved: list[Bid] = []
        self.updated: list[Bid] = []
        self.outbox: list[tuple[UUID, str, dict]] = []
        self.existing_by_driver: Bid | None = None

    def begin_nested(self):
        return FakeNested()

    async def find_by_driver_and_session(self, driver_id, session_id):
        if self.existing_by_driver and self.existing_by_driver.driver_id == driver_id:
            return self.existing_by_driver
        return None

    async def save(self, bid: Bid):
        self.saved.append(bid)
        return bid

    async def update_bid(self, bid: Bid):
        self.updated.append(bid)
        return bid

    async def save_outbox_event(self, bid_id, event_type, payload):
        self.outbox.append((bid_id, event_type, payload))


class FakeCounterRepo:
    def __init__(self, counter_offer: CounterOffer | None = None) -> None:
        self.counter_offer = counter_offer
        self.saved: list[CounterOffer] = []
        self.updated: list[CounterOffer] = []

    async def save(self, counter_offer: CounterOffer):
        self.saved.append(counter_offer)
        self.counter_offer = counter_offer
        return counter_offer

    async def find_by_id(self, counter_offer_id):
        if self.counter_offer and self.counter_offer.id == counter_offer_id:
            return self.counter_offer
        return None

    async def update(self, counter_offer: CounterOffer):
        self.updated.append(counter_offer)
        self.counter_offer = counter_offer


class FakeCache:
    def __init__(self) -> None:
        self.locked = False
        self.deleted: list[tuple[str, str, str]] = []

    async def set(self, namespace, key, value, *, nx=False, ttl=None):
        if nx and self.locked:
            return False
        self.locked = True
        return True

    async def delete_if_equals(self, namespace, key, value):
        self.deleted.append((namespace, key, value))
        self.locked = False


class FakeWebSockets:
    def __init__(self) -> None:
        self.events: list[tuple[UUID, BiddingEvent, dict]] = []

    async def broadcast_to_session(self, session_id, event, payload):
        self.events.append((session_id, event, payload))


def make_session() -> BiddingSession:
    return BiddingSession(
        id=uuid4(),
        service_request_id=uuid4(),
        status=BiddingSessionStatus.OPEN,
        opened_at=datetime.now(timezone.utc),
        passenger_user_id=uuid4(),
        pricing_mode=PricingMode.HYBRID,
        baseline_price=400.0,
    )


@pytest.mark.asyncio
async def test_passenger_counter_offer_does_not_create_fake_driver_bid() -> None:
    session = make_session()
    passenger_user_id = session.passenger_user_id
    assert passenger_user_id is not None
    bid_repo = FakeBidRepo()
    counter_repo = FakeCounterRepo()
    ws = FakeWebSockets()
    uc = PassengerCounterOfferUseCase(
        session_repo=cast(Any, FakeSessionRepo(session)),
        bid_repo=cast(Any, bid_repo),
        counter_offer_repo=cast(Any, counter_repo),
        ws=cast(Any, ws),
    )

    response = await uc.execute(
        session_id=session.id,
        passenger_id=passenger_user_id,
        counter_price=380.0,
        counter_eta_minutes=15,
    )

    assert bid_repo.saved == []
    assert response.user_id == session.passenger_user_id
    assert response.driver_id is None
    assert counter_repo.saved[0].bid_id is None
    assert ws.events[0][1] == BiddingEvent.PASSENGER_COUNTER_BID


@pytest.mark.asyncio
async def test_driver_accept_counter_creates_real_driver_bid_and_closes_session() -> None:
    session = make_session()
    passenger_user_id = session.passenger_user_id
    assert passenger_user_id is not None
    driver_id = uuid4()
    counter_offer = CounterOffer(
        id=uuid4(),
        session_id=session.id,
        price=390.0,
        eta_minutes=12,
        user_id=passenger_user_id,
        status=CounterOfferStatus.PENDING,
    )
    bid_repo = FakeBidRepo()
    counter_repo = FakeCounterRepo(counter_offer)
    cache = FakeCache()
    ws = FakeWebSockets()
    uc = DriverAcceptCounterOfferUseCase(
        session_repo=cast(Any, FakeSessionRepo(session)),
        bid_repo=cast(Any, bid_repo),
        counter_offer_repo=cast(Any, counter_repo),
        cache=cast(Any, cache),
        ws=cast(Any, ws),
    )

    response = await uc.execute(
        session_id=session.id,
        counter_offer_id=counter_offer.id,
        driver_id=driver_id,
    )

    assert response.driver_id == driver_id
    assert response.bid_amount == counter_offer.price
    assert bid_repo.saved[0].driver_id == driver_id
    assert bid_repo.saved[0].status.value == "ACCEPTED"
    assert counter_repo.updated[0].status == CounterOfferStatus.ACCEPTED
    assert counter_repo.updated[0].driver_id == driver_id
    assert counter_repo.updated[0].bid_id == response.id
    assert session.status == BiddingSessionStatus.CLOSED
    assert cache.deleted == [("bids", f"lock:{session.id}", "locked")]
