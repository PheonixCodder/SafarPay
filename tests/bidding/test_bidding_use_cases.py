from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from typing import Any, cast
from uuid import uuid4

import pytest
from bidding.application.schemas import PlaceBidRequest
from bidding.application.use_cases import (
    AcceptBidUseCase,
    CancelSessionUseCase,
    CreateBiddingSessionUseCase,
    DriverAcceptCounterOfferUseCase,
    ExpireSessionsUseCase,
    GetItemBidsUseCase,
    PassengerCounterOfferUseCase,
    PlaceBidUseCase,
    WithdrawBidUseCase,
)
from bidding.domain.exceptions import (
    BiddingClosedError,
    BidNotFoundError,
    BidTooLowError,
    LockAcquisitionError,
    UnauthorisedBiddingAccessError,
)
from bidding.domain.models import BiddingSessionStatus, BidStatus, CounterOfferStatus, PricingMode
from bidding.infrastructure.websocket_manager import BiddingEvent

from tests.bidding.conftest import (
    DRIVER_ID,
    OTHER_DRIVER_ID,
    OTHER_PASSENGER_ID,
    PASSENGER_ID,
    FakeBiddingWebSockets,
    FakeBidRepo,
    FakeCache,
    FakeCounterRepo,
    FakeRideClient,
    FakeSessionRepo,
    FakeWebhook,
    make_bid,
    make_counter,
    make_session,
)


@pytest.mark.asyncio
async def test_create_bidding_session_skips_fixed_and_notifies_drivers_for_bidding_modes() -> None:
    repo = FakeSessionRepo()
    webhook = FakeWebhook()
    ws = FakeBiddingWebSockets()
    ride_id = uuid4()
    driver_ids = [DRIVER_ID, OTHER_DRIVER_ID]

    response = await CreateBiddingSessionUseCase(
        cast(Any, repo),
        cast(Any, FakeCache()),
        cast(Any, webhook),
        cast(Any, ws),
    ).execute(
        ride_id,
        {
            "pricing_mode": "HYBRID",
            "passenger_user_id": str(PASSENGER_ID),
            "baseline_price": 400,
        },
        driver_ids,
    )

    assert response.baseline_price == 400
    assert repo.saved[0].passenger_user_id == PASSENGER_ID
    assert repo.saved[0].pricing_mode == PricingMode.HYBRID
    assert [call[0] for call in webhook.opportunities] == driver_ids
    assert [event[0] for event in ws.driver_events] == driver_ids

    with pytest.raises(BiddingClosedError):
        await CreateBiddingSessionUseCase(
            cast(Any, FakeSessionRepo()),
            cast(Any, FakeCache()),
            cast(Any, FakeWebhook()),
            cast(Any, FakeBiddingWebSockets()),
        ).execute(ride_id, {"pricing_mode": "FIXED"}, [])

    with pytest.raises(BiddingClosedError, match="passenger id"):
        await CreateBiddingSessionUseCase(
            cast(Any, FakeSessionRepo()),
            cast(Any, FakeCache()),
            cast(Any, FakeWebhook()),
            cast(Any, FakeBiddingWebSockets()),
        ).execute(ride_id, {"pricing_mode": "HYBRID"}, driver_ids)

    with pytest.raises(BiddingClosedError, match="Unsupported pricing_mode"):
        await CreateBiddingSessionUseCase(
            cast(Any, FakeSessionRepo()),
            cast(Any, FakeCache()),
            cast(Any, FakeWebhook()),
            cast(Any, FakeBiddingWebSockets()),
        ).execute(
            ride_id,
            {"pricing_mode": "hybrid", "passenger_user_id": str(PASSENGER_ID)},
            driver_ids,
        )


@pytest.mark.asyncio
async def test_place_bid_creates_first_bid_and_auto_accept_outbox() -> None:
    session = make_session(pricing_mode=PricingMode.BID_BASED)
    bid_repo = FakeBidRepo()
    cache = FakeCache()
    ws = FakeBiddingWebSockets()

    response = await PlaceBidUseCase(
        cast(Any, FakeSessionRepo(session)),
        cast(Any, bid_repo),
        cast(Any, cache),
        cast(Any, ws),
        ride_client=cast(Any, FakeRideClient()),
        publisher=cast(Any, object()),
    ).execute(
        session.id,
        PlaceBidRequest(bid_amount=380, eta_minutes=8, message="nearby"),
        DRIVER_ID,
        idempotency_key="place-1",
    )

    assert response.driver_id == DRIVER_ID
    assert response.bid_amount == 380
    assert bid_repo.saved[0].status == BidStatus.ACTIVE
    assert [event[1] for event in bid_repo.outbox] == ["bid.placed", "bid.auto_accept_requested"]
    assert ws.session_events[0][1] == BiddingEvent.NEW_BID
    assert cache.redis.values["idem:place_bid:place-1"] != "IN_PROGRESS"


@pytest.mark.asyncio
async def test_place_bid_rebid_rules_lowest_hydration_rate_limit_and_idempotency() -> None:
    session = make_session()
    existing = make_bid(session, amount=380)
    lower = make_bid(session, driver_id=OTHER_DRIVER_ID, amount=360)
    bid_repo = FakeBidRepo([existing, lower])
    cache = FakeCache()

    with pytest.raises(BidTooLowError):
        await PlaceBidUseCase(
            cast(Any, FakeSessionRepo(session)),
            cast(Any, bid_repo),
            cast(Any, cache),
            cast(Any, FakeBiddingWebSockets()),
        ).execute(session.id, PlaceBidRequest(bid_amount=390, eta_minutes=None), DRIVER_ID)

    with pytest.raises(BidTooLowError):
        await PlaceBidUseCase(
            cast(Any, FakeSessionRepo(session)),
            cast(Any, bid_repo),
            cast(Any, cache),
            cast(Any, FakeBiddingWebSockets()),
        ).execute(session.id, PlaceBidRequest(bid_amount=370, eta_minutes=None), uuid4())

    cache.redis.counts[f"rate_limit:driver:{DRIVER_ID}"] = 10
    with pytest.raises(UnauthorisedBiddingAccessError, match="Rate limit"):
        await PlaceBidUseCase(
            cast(Any, FakeSessionRepo(session)),
            cast(Any, bid_repo),
            cast(Any, cache),
            cast(Any, FakeBiddingWebSockets()),
        ).execute(session.id, PlaceBidRequest(bid_amount=350, eta_minutes=None), DRIVER_ID)

    cached = {
        "id": str(existing.id),
        "bidding_session_id": str(session.id),
        "driver_id": str(DRIVER_ID),
        "driver_vehicle_id": None,
        "bid_amount": 380,
        "currency": "PKR",
        "eta_minutes": 10,
        "message": "test bid",
        "status": "ACTIVE",
        "placed_at": existing.placed_at.isoformat(),
    }
    cache.redis.values["idem:place_bid:cached"] = json.dumps(cached)
    response = await PlaceBidUseCase(
        cast(Any, FakeSessionRepo(session)),
        cast(Any, bid_repo),
        cast(Any, cache),
        cast(Any, FakeBiddingWebSockets()),
    ).execute(session.id, PlaceBidRequest(bid_amount=350, eta_minutes=None), DRIVER_ID, idempotency_key="cached")
    assert response.id == existing.id

    cache.redis.force_set_failure = True
    with pytest.raises(LockAcquisitionError):
        await PlaceBidUseCase(
            cast(Any, FakeSessionRepo(session)),
            cast(Any, bid_repo),
            cast(Any, cache),
            cast(Any, FakeBiddingWebSockets()),
        ).execute(session.id, PlaceBidRequest(bid_amount=350, eta_minutes=None), DRIVER_ID, idempotency_key="busy")


@pytest.mark.asyncio
async def test_accept_bid_is_passenger_owned_locks_session_and_closes_with_outbox() -> None:
    session = make_session(passenger_id=PASSENGER_ID)
    bid = make_bid(session)
    bid_repo = FakeBidRepo([bid])
    cache = FakeCache()
    webhook = FakeWebhook()
    ws = FakeBiddingWebSockets()

    response = await AcceptBidUseCase(
        cast(Any, FakeSessionRepo(session)),
        cast(Any, bid_repo),
        cast(Any, cache),
        cast(Any, webhook),
        cast(Any, ws),
        publisher=cast(Any, object()),
    ).execute(session.id, bid.id, PASSENGER_ID, idempotency_key="accept-1")

    assert response.status == "ACCEPTED"
    assert session.status == BiddingSessionStatus.CLOSED
    assert bid_repo.outbox[0][1] == "bid.accepted"
    assert bid_repo.outbox[0][2]["passenger_user_id"] == str(PASSENGER_ID)
    assert [event[1] for event in ws.session_events] == [BiddingEvent.BID_ACCEPTED, BiddingEvent.SESSION_CLOSED]
    assert webhook.accepted[0][0] == DRIVER_ID
    assert cache.deleted_if_equals == [("bids", f"lock:{session.id}", "locked")]


@pytest.mark.asyncio
async def test_accept_bid_rejects_wrong_passenger_bad_bid_status_and_lock_contention() -> None:
    session = make_session(passenger_id=PASSENGER_ID)
    bid = make_bid(session, status=BidStatus.WITHDRAWN)

    with pytest.raises(UnauthorisedBiddingAccessError):
        await AcceptBidUseCase(
            cast(Any, FakeSessionRepo(session)),
            cast(Any, FakeBidRepo([bid])),
            cast(Any, FakeCache()),
            cast(Any, FakeWebhook()),
            cast(Any, FakeBiddingWebSockets()),
        ).execute(session.id, bid.id, OTHER_PASSENGER_ID)

    with pytest.raises(BiddingClosedError, match="Only ACTIVE"):
        await AcceptBidUseCase(
            cast(Any, FakeSessionRepo(session)),
            cast(Any, FakeBidRepo([bid])),
            cast(Any, FakeCache()),
            cast(Any, FakeWebhook()),
            cast(Any, FakeBiddingWebSockets()),
        ).execute(session.id, bid.id, PASSENGER_ID)

    locked_cache = FakeCache()
    await locked_cache.set("bids", f"lock:{session.id}", "locked", nx=True, ttl=30)
    with pytest.raises(LockAcquisitionError):
        await AcceptBidUseCase(
            cast(Any, FakeSessionRepo(session)),
            cast(Any, FakeBidRepo([make_bid(session)])),
            cast(Any, locked_cache),
            cast(Any, FakeWebhook()),
            cast(Any, FakeBiddingWebSockets()),
        ).execute(session.id, bid.id, PASSENGER_ID)


@pytest.mark.asyncio
async def test_withdraw_bid_enforces_driver_owner_and_recalculates_leader() -> None:
    session = make_session()
    bid = make_bid(session, amount=350)
    other_bid = make_bid(session, driver_id=OTHER_DRIVER_ID, amount=370)
    bid_repo = FakeBidRepo([bid, other_bid])
    cache = FakeCache()
    zset_key = cache._key("bids", f"session:{session.id}")
    await cache.redis.zadd(zset_key, {str(bid.id): bid.bid_amount, str(other_bid.id): other_bid.bid_amount})
    ws = FakeBiddingWebSockets()

    with pytest.raises(UnauthorisedBiddingAccessError):
        await WithdrawBidUseCase(
            cast(Any, FakeSessionRepo(session)),
            cast(Any, bid_repo),
            cast(Any, cache),
            cast(Any, ws),
        ).execute(session.id, bid.id, OTHER_DRIVER_ID)

    response = await WithdrawBidUseCase(
        cast(Any, FakeSessionRepo(session)),
        cast(Any, bid_repo),
        cast(Any, cache),
        cast(Any, ws),
        publisher=cast(Any, object()),
    ).execute(session.id, bid.id, DRIVER_ID)

    assert response.status == "WITHDRAWN"
    assert str(bid.id) not in cache.redis.zsets[zset_key]
    assert [event[1] for event in ws.session_events] == [BiddingEvent.BID_WITHDRAWN, BiddingEvent.BID_LEADER_UPDATED]


@pytest.mark.asyncio
async def test_get_item_bids_includes_lowest_bid_metadata_and_counter_history() -> None:
    session = make_session(pricing_mode=PricingMode.HYBRID)
    bid = make_bid(session, amount=390)
    counter = make_counter(session, price=375)
    cache = FakeCache()
    await cache.redis.zadd(cache._key("bids", f"session:{session.id}"), {str(bid.id): bid.bid_amount})

    response = await GetItemBidsUseCase(
        cast(Any, FakeSessionRepo(session)),
        cast(Any, FakeBidRepo([bid])),
        cast(Any, FakeCounterRepo([counter])),
        cast(Any, cache),
    ).execute(session.id)

    assert response.passenger_user_id == PASSENGER_ID
    assert response.pricing_mode == "HYBRID"
    assert response.lowest_bid == 390
    assert response.counter_offers is not None
    assert response.counter_offers[0].id == counter.id


@pytest.mark.asyncio
async def test_passenger_counter_is_hybrid_only_and_does_not_create_driver_bid() -> None:
    session = make_session(pricing_mode=PricingMode.HYBRID)
    bid_repo = FakeBidRepo()
    counter_repo = FakeCounterRepo()
    ws = FakeBiddingWebSockets()

    response = await PassengerCounterOfferUseCase(
        cast(Any, FakeSessionRepo(session)),
        cast(Any, bid_repo),
        cast(Any, counter_repo),
        cast(Any, ws),
    ).execute(session.id, PASSENGER_ID, counter_price=370, counter_eta_minutes=11)

    assert response.user_id == PASSENGER_ID
    assert response.driver_id is None
    assert bid_repo.saved == []
    assert ws.session_events[0][1] == BiddingEvent.PASSENGER_COUNTER_BID

    with pytest.raises(BiddingClosedError, match="HYBRID"):
        bid_based_session = make_session(pricing_mode=PricingMode.BID_BASED)
        await PassengerCounterOfferUseCase(
            cast(Any, FakeSessionRepo(bid_based_session)),
            cast(Any, FakeBidRepo()),
            cast(Any, FakeCounterRepo()),
            cast(Any, FakeBiddingWebSockets()),
        ).execute(bid_based_session.id, PASSENGER_ID, counter_price=370)


@pytest.mark.asyncio
async def test_driver_accept_counter_creates_or_updates_real_bid_and_closes_session() -> None:
    session = make_session(pricing_mode=PricingMode.HYBRID)
    counter = make_counter(session, price=365)
    bid_repo = FakeBidRepo()
    counter_repo = FakeCounterRepo([counter])
    cache = FakeCache()
    ws = FakeBiddingWebSockets()

    response = await DriverAcceptCounterOfferUseCase(
        cast(Any, FakeSessionRepo(session)),
        cast(Any, bid_repo),
        cast(Any, counter_repo),
        cast(Any, cache),
        cast(Any, ws),
        publisher=cast(Any, object()),
    ).execute(session.id, counter.id, DRIVER_ID)

    assert response.driver_id == DRIVER_ID
    assert response.status == "ACCEPTED"
    assert bid_repo.saved[0].driver_id == DRIVER_ID
    assert counter.status == CounterOfferStatus.ACCEPTED
    assert counter.driver_id == DRIVER_ID
    assert counter.bid_id == response.id
    assert [event[1] for event in bid_repo.outbox] == ["bid.counter_offer.responded", "bid.accepted"]
    assert session.status == BiddingSessionStatus.CLOSED

    session2 = make_session(pricing_mode=PricingMode.HYBRID)
    existing = make_bid(session2, amount=390)
    counter2 = make_counter(session2, price=360)
    bid_repo2 = FakeBidRepo([existing])
    await DriverAcceptCounterOfferUseCase(
        cast(Any, FakeSessionRepo(session2)),
        cast(Any, bid_repo2),
        cast(Any, FakeCounterRepo([counter2])),
        cast(Any, FakeCache()),
        cast(Any, FakeBiddingWebSockets()),
    ).execute(session2.id, counter2.id, DRIVER_ID)
    assert bid_repo2.saved == []
    assert bid_repo2.updated[0].id == existing.id
    assert bid_repo2.updated[0].bid_amount == 360


@pytest.mark.asyncio
async def test_driver_accept_counter_rejects_wrong_status_wrong_mode_missing_counter_and_lock() -> None:
    session = make_session(pricing_mode=PricingMode.HYBRID)
    accepted_counter = make_counter(session, status=CounterOfferStatus.ACCEPTED)

    with pytest.raises(BiddingClosedError, match="pending"):
        await DriverAcceptCounterOfferUseCase(
            cast(Any, FakeSessionRepo(session)),
            cast(Any, FakeBidRepo()),
            cast(Any, FakeCounterRepo([accepted_counter])),
            cast(Any, FakeCache()),
            cast(Any, FakeBiddingWebSockets()),
        ).execute(session.id, accepted_counter.id, DRIVER_ID)

    with pytest.raises(BidNotFoundError):
        await DriverAcceptCounterOfferUseCase(
            cast(Any, FakeSessionRepo(session)),
            cast(Any, FakeBidRepo()),
            cast(Any, FakeCounterRepo()),
            cast(Any, FakeCache()),
            cast(Any, FakeBiddingWebSockets()),
        ).execute(session.id, uuid4(), DRIVER_ID)

    locked = FakeCache()
    await locked.set("bids", f"lock:{session.id}", "locked", nx=True, ttl=30)
    with pytest.raises(LockAcquisitionError):
        await DriverAcceptCounterOfferUseCase(
            cast(Any, FakeSessionRepo(session)),
            cast(Any, FakeBidRepo()),
            cast(Any, FakeCounterRepo([make_counter(session)])),
            cast(Any, locked),
            cast(Any, FakeBiddingWebSockets()),
        ).execute(session.id, uuid4(), DRIVER_ID)


@pytest.mark.asyncio
async def test_cancel_and_expire_sessions_are_idempotent_and_broadcast_closure() -> None:
    session = make_session()
    repo = FakeSessionRepo(session)
    ws = FakeBiddingWebSockets()

    await CancelSessionUseCase(cast(Any, repo), cast(Any, FakeWebhook()), cast(Any, ws)).execute(session.service_request_id)

    assert session.status == BiddingSessionStatus.CLOSED
    assert ws.session_events[0][1] == BiddingEvent.SESSION_CANCELLED

    expired = make_session()
    expired.expires_at = datetime.now(timezone.utc) - timedelta(seconds=1)
    active = make_session()
    active.expires_at = datetime.now(timezone.utc) + timedelta(minutes=1)
    expire_repo = FakeSessionRepo()
    expire_repo.active_sessions = [expired, active]
    expire_ws = FakeBiddingWebSockets()

    count = await ExpireSessionsUseCase(
        cast(Any, expire_repo),
        cast(Any, expire_ws),
        cast(Any, FakeWebhook()),
    ).execute()

    assert count == 1
    assert expired.status == BiddingSessionStatus.EXPIRED
    assert active.status == BiddingSessionStatus.OPEN
