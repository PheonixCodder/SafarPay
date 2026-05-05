from __future__ import annotations

from typing import Any
from uuid import uuid4

import pytest
from bidding.application.use_cases import _bid_to_resp
from bidding.domain.exceptions import (
    BiddingClosedError,
    BiddingSessionNotFoundError,
    BidNotFoundError,
    BidTooLowError,
    LockAcquisitionError,
    UnauthorisedBiddingAccessError,
)
from bidding.domain.models import BidStatus, CounterOfferStatus, PricingMode
from bidding.infrastructure.dependencies import (
    get_accept_bid_uc,
    get_counter_offer_repo,
    get_driver_accept_counter_uc,
    get_item_bids_uc,
    get_passenger_counter_uc,
    get_place_bid_uc,
    get_withdraw_bid_uc,
)
from fastapi import FastAPI
from sp.infrastructure.security.dependencies import get_current_driver, get_current_user

from tests.bidding.conftest import (
    DRIVER_ID,
    OTHER_DRIVER_ID,
    PASSENGER_ID,
    make_bid,
    make_counter,
    make_session,
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


class CounterRepoStub:
    def __init__(self, counters: list[Any]) -> None:
        self.counters = counters

    async def find_by_session(self, session_id: Any) -> list[Any]:
        return self.counters


def override(app: FastAPI, dependency: Any, value: Any) -> Any:
    app.dependency_overrides[dependency] = lambda: value
    return value


def counter_response(counter: Any) -> dict[str, Any]:
    return {
        "id": counter.id,
        "session_id": counter.session_id,
        "price": counter.price,
        "eta_minutes": counter.eta_minutes,
        "user_id": counter.user_id,
        "driver_id": counter.driver_id,
        "bid_id": counter.bid_id,
        "status": counter.status.value,
        "responded_at": counter.responded_at,
        "reason": counter.reason,
        "created_at": counter.created_at,
    }


def test_all_bidding_routes_success_and_actor_parameters(bidding_app: FastAPI, bidding_client: Any) -> None:
    session = make_session(pricing_mode=PricingMode.HYBRID)
    bid = make_bid(session)
    counter = make_counter(session)
    item_response = {
        "session_id": session.id,
        "service_request_id": session.service_request_id,
        "status": "OPEN",
        "pricing_mode": "HYBRID",
        "passenger_user_id": PASSENGER_ID,
        "baseline_price": 400,
        "bids": [_bid_to_resp(bid).model_dump()],
        "lowest_bid": bid.bid_amount,
        "counter_offers": [
            {
                "id": counter.id,
                "price": counter.price,
                "eta_minutes": counter.eta_minutes,
                "status": counter.status.value,
                "user_id": counter.user_id,
                "driver_id": counter.driver_id,
                "bid_id": counter.bid_id,
                "created_at": counter.created_at,
            }
        ],
    }

    place = override(bidding_app, get_place_bid_uc, StubUseCase(_bid_to_resp(bid)))
    accept = override(bidding_app, get_accept_bid_uc, StubUseCase(_bid_to_resp(bid)))
    get_items = override(bidding_app, get_item_bids_uc, StubUseCase(item_response))
    withdraw = override(bidding_app, get_withdraw_bid_uc, StubUseCase(_bid_to_resp(bid)))
    passenger_counter = override(bidding_app, get_passenger_counter_uc, StubUseCase(counter_response(counter)))
    driver_accept_counter = override(bidding_app, get_driver_accept_counter_uc, StubUseCase(_bid_to_resp(bid)))
    override(bidding_app, get_counter_offer_repo, CounterRepoStub([counter]))

    assert bidding_client.post(
        f"/api/v1/bidding/sessions/{session.id}/bids",
        json={"bid_amount": 380, "eta_minutes": 10},
    ).status_code == 201
    assert bidding_client.post(
        f"/api/v1/bidding/sessions/{session.id}/accept",
        json={"bid_id": str(bid.id)},
    ).status_code == 200
    assert bidding_client.get(f"/api/v1/bidding/sessions/{session.id}").status_code == 200
    assert bidding_client.post(f"/api/v1/bidding/sessions/{session.id}/bids/{bid.id}/withdraw").status_code == 200
    assert bidding_client.post(
        f"/api/v1/bidding/sessions/{session.id}/passenger-counter",
        json={"counter_price": 375, "counter_eta_minutes": 12},
    ).status_code == 201
    assert bidding_client.post(
        f"/api/v1/bidding/sessions/{session.id}/counter/{counter.id}/accept",
    ).status_code == 200
    assert bidding_client.get(f"/api/v1/bidding/sessions/{session.id}/counter-offers").status_code == 200

    assert place.calls[0][2] == DRIVER_ID
    assert accept.calls[0][2] == PASSENGER_ID
    assert withdraw.calls[0][2] == DRIVER_ID
    assert passenger_counter.calls[0][-1]["passenger_id"] == PASSENGER_ID
    assert driver_accept_counter.calls[0][-1]["driver_id"] == DRIVER_ID
    assert get_items.calls[0][0] == session.id


@pytest.mark.parametrize(
    ("dependency", "exc", "route", "method", "body", "status_code"),
    [
        (get_place_bid_uc, BidTooLowError("too low"), "bids", "post", {"bid_amount": 400}, 409),
        (get_place_bid_uc, BiddingClosedError("closed"), "bids", "post", {"bid_amount": 400}, 422),
        (get_place_bid_uc, BiddingSessionNotFoundError("missing"), "bids", "post", {"bid_amount": 400}, 404),
        (get_place_bid_uc, UnauthorisedBiddingAccessError("forbidden"), "bids", "post", {"bid_amount": 400}, 403),
        (get_accept_bid_uc, LockAcquisitionError("locked"), "accept", "post", {"bid_id": str(uuid4())}, 409),
        (get_accept_bid_uc, BidNotFoundError("bad bid"), "accept", "post", {"bid_id": str(uuid4())}, 422),
        (get_accept_bid_uc, UnauthorisedBiddingAccessError("forbidden"), "accept", "post", {"bid_id": str(uuid4())}, 403),
        (get_item_bids_uc, BiddingSessionNotFoundError("missing"), "", "get", None, 404),
        (get_withdraw_bid_uc, BidNotFoundError("bad bid"), "withdraw", "post", None, 422),
        (get_withdraw_bid_uc, UnauthorisedBiddingAccessError("forbidden"), "withdraw", "post", None, 403),
        (get_passenger_counter_uc, BiddingClosedError("not hybrid"), "passenger-counter", "post", {"counter_price": 300}, 422),
        (get_passenger_counter_uc, BiddingSessionNotFoundError("missing"), "passenger-counter", "post", {"counter_price": 300}, 404),
        (get_driver_accept_counter_uc, LockAcquisitionError("locked"), "counter-accept", "post", None, 409),
        (get_driver_accept_counter_uc, BidNotFoundError("missing"), "counter-accept", "post", None, 422),
    ],
)
def test_bidding_route_error_mappings(
    bidding_app: FastAPI,
    bidding_client: Any,
    dependency: Any,
    exc: Exception,
    route: str,
    method: str,
    body: dict[str, Any] | None,
    status_code: int,
) -> None:
    session_id = uuid4()
    bid_id = uuid4()
    counter_id = uuid4()
    override(bidding_app, dependency, StubUseCase(exc=exc))

    if route == "bids":
        path = f"/api/v1/bidding/sessions/{session_id}/bids"
    elif route == "accept":
        path = f"/api/v1/bidding/sessions/{session_id}/accept"
    elif route == "withdraw":
        path = f"/api/v1/bidding/sessions/{session_id}/bids/{bid_id}/withdraw"
    elif route == "passenger-counter":
        path = f"/api/v1/bidding/sessions/{session_id}/passenger-counter"
    elif route == "counter-accept":
        path = f"/api/v1/bidding/sessions/{session_id}/counter/{counter_id}/accept"
    else:
        path = f"/api/v1/bidding/sessions/{session_id}"

    response = getattr(bidding_client, method)(path, json=body) if body is not None else getattr(bidding_client, method)(path)

    assert response.status_code == status_code


def test_bidding_schema_validation_errors_return_422(bidding_app: FastAPI, bidding_client: Any) -> None:
    session_id = uuid4()
    override(bidding_app, get_place_bid_uc, StubUseCase())
    override(bidding_app, get_passenger_counter_uc, StubUseCase())
    override(bidding_app, get_accept_bid_uc, StubUseCase())
    assert bidding_client.post(
        f"/api/v1/bidding/sessions/{session_id}/bids",
        json={"bid_amount": 0},
    ).status_code == 422
    assert bidding_client.post(
        f"/api/v1/bidding/sessions/{session_id}/passenger-counter",
        json={"counter_price": -1},
    ).status_code == 422
    assert bidding_client.post(
        f"/api/v1/bidding/sessions/{session_id}/accept",
        json={"bid_id": "not-a-uuid"},
    ).status_code == 422


def test_counter_offers_endpoint_returns_all_statuses(bidding_app: FastAPI, bidding_client: Any) -> None:
    session = make_session(pricing_mode=PricingMode.HYBRID)
    pending = make_counter(session, status=CounterOfferStatus.PENDING)
    accepted = make_counter(session, status=CounterOfferStatus.ACCEPTED)
    accepted.driver_id = DRIVER_ID
    override(bidding_app, get_counter_offer_repo, CounterRepoStub([pending, accepted]))

    response = bidding_client.get(f"/api/v1/bidding/sessions/{session.id}/counter-offers")

    assert response.status_code == 200
    statuses = [item["status"] for item in response.json()]
    assert statuses == ["PENDING", "ACCEPTED"]
    assert response.json()[1]["driver_id"] == str(DRIVER_ID)


def test_driver_and_passenger_dependency_overrides_are_separate(bidding_app: FastAPI, bidding_client: Any) -> None:
    session = make_session()
    bid = make_bid(session, driver_id=OTHER_DRIVER_ID)
    bidding_app.dependency_overrides[get_current_user] = lambda: token(PASSENGER_ID, role="passenger")
    bidding_app.dependency_overrides[get_current_driver] = lambda: OTHER_DRIVER_ID
    place = override(bidding_app, get_place_bid_uc, StubUseCase(_bid_to_resp(bid)))
    accept = override(bidding_app, get_accept_bid_uc, StubUseCase(_bid_to_resp(bid)))

    bidding_client.post(f"/api/v1/bidding/sessions/{session.id}/bids", json={"bid_amount": 300})
    bidding_client.post(f"/api/v1/bidding/sessions/{session.id}/accept", json={"bid_id": str(bid.id)})

    assert place.calls[0][2] == OTHER_DRIVER_ID
    assert accept.calls[0][2] == PASSENGER_ID
    assert place.calls[0][2] != accept.calls[0][2]


def test_bid_response_preserves_status_and_driver_identity() -> None:
    session = make_session()
    bid = make_bid(session, driver_id=DRIVER_ID, status=BidStatus.ACTIVE)
    response = _bid_to_resp(bid)

    assert response.driver_id == DRIVER_ID
    assert response.status == "ACTIVE"
