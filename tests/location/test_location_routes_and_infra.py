from __future__ import annotations

# ruff: noqa: E402,I001

import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, cast

import pytest
from fastapi import FastAPI
from sp.infrastructure.security.dependencies import get_current_driver, get_current_user

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from location.application.use_cases import (
    _driver_to_response,
    _passenger_to_response,
)
from location.domain.exceptions import (
    ActorNotFoundError,
    GPSAccuracyTooLowError,
    RateLimitExceededError,
    UnauthorisedLocationAccessError,
)
from location.domain.models import ActorType, DriverStatus
from location.infrastructure.dependencies import (
    get_current_driver_location_uc,
    get_geocode_uc,
    get_location_history_uc,
    get_nearby_drivers_uc,
    get_reverse_geocode_uc,
    get_ride_locations_uc,
    get_set_driver_status_uc,
    get_update_driver_location_uc,
)
from location.infrastructure.kafka_consumer import LocationKafkaConsumer
from location.infrastructure.rate_limiter import LocationRateLimiter

from tests.location.conftest import (
    DRIVER_ID,
    OTHER_DRIVER_ID,
    PASSENGER_ID,
    RIDE_ID,
    FakeLocationStore,
    FakeWs,
    location_payload,
    make_driver_location,
    make_history,
    make_passenger_location,
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


def override(app: FastAPI, dep: Any, value: Any) -> Any:
    app.dependency_overrides[dep] = lambda: value
    return value


def test_all_location_http_routes_success_and_identity_parameters(location_app: FastAPI, location_client: Any) -> None:
    driver = make_driver_location(DRIVER_ID, ride_id=RIDE_ID)
    passenger = make_passenger_location(PASSENGER_ID, ride_id=RIDE_ID)
    history = make_history()
    driver_response = _driver_to_response(driver)
    passenger_response = _passenger_to_response(passenger)
    assert driver_response is not None
    assert passenger_response is not None
    update = override(location_app, get_update_driver_location_uc, StubUseCase())
    current = override(location_app, get_current_driver_location_uc, StubUseCase(driver_response))
    status_uc = override(location_app, get_set_driver_status_uc, StubUseCase({"success": True, "message": "ok"}))
    nearby = override(
        location_app,
        get_nearby_drivers_uc,
        StubUseCase({"drivers": [driver_response.model_dump()], "radius_km": 5.0, "count": 1}),
    )
    ride_locations = override(
        location_app,
        get_ride_locations_uc,
        StubUseCase(
            {
                "ride_id": RIDE_ID,
                "driver": driver_response.model_dump(),
                "passenger": passenger_response.model_dump(),
            }
        ),
    )
    override(
        location_app,
        get_location_history_uc,
        StubUseCase(
            {
                "actor_id": DRIVER_ID,
                "actor_type": "DRIVER",
                "points": [
                    {
                        "lat": history.latitude,
                        "lng": history.longitude,
                        "speed": history.speed_kmh,
                        "heading": history.heading_degrees,
                        "accuracy": history.accuracy_meters,
                        "recorded_at": history.recorded_at,
                    }
                ],
                "total": 1,
            }
        ),
    )
    geocode = override(
        location_app,
        get_geocode_uc,
        StubUseCase({"formatted": "Lahore", "coordinates": {"latitude": 31.52, "longitude": 74.35}}),
    )
    reverse = override(
        location_app,
        get_reverse_geocode_uc,
        StubUseCase({"formatted": "Lahore", "coordinates": {"latitude": 31.52, "longitude": 74.35}}),
    )

    assert location_client.post(f"/api/v1/location/drivers/{DRIVER_ID}/location", json=location_payload()).status_code == 204
    assert location_client.get(f"/api/v1/location/drivers/{DRIVER_ID}/location").status_code == 200
    assert location_client.post(f"/api/v1/location/drivers/{DRIVER_ID}/status", json={"status": "ONLINE"}).status_code == 200
    assert location_client.get("/api/v1/location/drivers/nearby?lat=31.5&lng=74.3").status_code == 200
    assert location_client.get(f"/api/v1/location/rides/{RIDE_ID}/locations").status_code == 200
    since = (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat()
    until = datetime.now(timezone.utc).isoformat()
    assert location_client.get(
        f"/api/v1/location/actors/{DRIVER_ID}/history",
        params={"since": since, "until": until},
    ).status_code == 200
    assert location_client.post("/api/v1/location/geocode", json={"address": "Model Town Lahore"}).status_code == 200
    assert location_client.post("/api/v1/location/reverse", json={"latitude": 31.52, "longitude": 74.35}).status_code == 200

    assert update.calls[0][0]["driver_id"] == DRIVER_ID
    assert current.calls[0][0] == DRIVER_ID
    assert status_uc.calls[0][0]["driver_id"] == DRIVER_ID
    assert nearby.calls[0][0]["latitude"] == 31.5
    assert ride_locations.calls[0][0]["caller_user_id"] == PASSENGER_ID
    assert geocode.calls[0][0] == "Model Town Lahore"
    assert reverse.calls[0][0:2] == (31.52, 74.35)


@pytest.mark.parametrize(
    ("dependency", "exc", "method", "path", "body", "status_code"),
    [
        (get_update_driver_location_uc, GPSAccuracyTooLowError("bad gps"), "post", f"/api/v1/location/drivers/{DRIVER_ID}/location", location_payload(), 422),
        (get_current_driver_location_uc, ActorNotFoundError("missing"), "get", f"/api/v1/location/drivers/{DRIVER_ID}/location", None, 404),
        (get_ride_locations_uc, UnauthorisedLocationAccessError("forbidden"), "get", f"/api/v1/location/rides/{RIDE_ID}/locations", None, 403),
        (get_set_driver_status_uc, RateLimitExceededError("rate"), "post", f"/api/v1/location/drivers/{DRIVER_ID}/status", {"status": "ONLINE"}, 429),
    ],
)
def test_location_route_error_mapping(
    location_app: FastAPI,
    location_client: Any,
    dependency: Any,
    exc: Exception,
    method: str,
    path: str,
    body: dict[str, Any] | None,
    status_code: int,
) -> None:
    override(location_app, dependency, StubUseCase(exc=exc))

    response = getattr(location_client, method)(path, json=body) if body is not None else getattr(location_client, method)(path)

    assert response.status_code == status_code


def test_location_route_actor_guards_and_schema_validation(location_app: FastAPI, location_client: Any) -> None:
    override(location_app, get_update_driver_location_uc, StubUseCase())
    override(location_app, get_nearby_drivers_uc, StubUseCase({"drivers": [], "radius_km": 5.0, "count": 0}))
    location_app.dependency_overrides[get_current_driver] = lambda: OTHER_DRIVER_ID
    assert location_client.post(f"/api/v1/location/drivers/{DRIVER_ID}/location", json=location_payload()).status_code == 403

    location_app.dependency_overrides[get_current_user] = lambda: token(role="admin")
    assert location_client.post(f"/api/v1/location/drivers/{DRIVER_ID}/location", json=location_payload()).status_code == 204

    assert location_client.post(f"/api/v1/location/drivers/{DRIVER_ID}/location", json=location_payload(lat=100)).status_code == 422
    assert location_client.get("/api/v1/location/drivers/nearby?lat=99&lng=74").status_code == 422


@pytest.mark.asyncio
async def test_location_rate_limiter_uses_separate_online_on_ride_and_actor_keys() -> None:
    class CounterCache:
        def __init__(self) -> None:
            self.counts: dict[tuple[str, str], int] = {}
            self.calls: list[tuple[str, str, int]] = []

        async def increment(self, namespace: str, key: str, ttl: int) -> int:
            self.calls.append((namespace, key, ttl))
            compound = (namespace, key)
            self.counts[compound] = self.counts.get(compound, 0) + 1
            return self.counts[compound]

    cache = CounterCache()
    limiter = LocationRateLimiter(cache)

    assert await limiter.allow(DRIVER_ID, actor_type=ActorType.DRIVER) is True
    assert await limiter.allow(DRIVER_ID, actor_type=ActorType.DRIVER) is True
    assert await limiter.allow(DRIVER_ID, actor_type=ActorType.DRIVER) is False
    assert await limiter.allow(DRIVER_ID, actor_type=ActorType.DRIVER, is_on_ride=True) is True
    assert await limiter.allow(PASSENGER_ID, actor_type=ActorType.PASSENGER) is True
    assert cache.calls[0][0] == "loc_rate"
    assert cache.calls[3][0] == "loc_rate_ride"
    assert f"passenger:{PASSENGER_ID}" in cache.calls[4][1]


@pytest.mark.asyncio
async def test_location_kafka_consumer_maintains_participant_cache_and_driver_status() -> None:
    store = FakeLocationStore()
    ws = FakeWs()
    consumer = LocationKafkaConsumer("localhost:9092", cast(Any, store), cast(Any, ws))

    await consumer._dispatch({
        "event_type": "service.request.accepted",
        "payload": {
            "ride_id": str(RIDE_ID),
            "driver_id": str(DRIVER_ID),
            "passenger_user_id": str(PASSENGER_ID),
        },
    })
    assert ws.subscribed == [(RIDE_ID, PASSENGER_ID)]
    assert store.participants[RIDE_ID] == (DRIVER_ID, PASSENGER_ID)
    assert store.status_updates[0] == (DRIVER_ID, DriverStatus.ON_RIDE, RIDE_ID)

    await consumer._dispatch({
        "event_type": "service.request.completed",
        "payload": {"ride_id": str(RIDE_ID), "driver_id": str(DRIVER_ID)},
    })
    assert ws.unsubscribed_all == [RIDE_ID]
    assert RIDE_ID not in store.participants
    assert store.status_updates[-1] == (DRIVER_ID, DriverStatus.ONLINE, None)

    await consumer._dispatch({"event_type": "service.request.accepted", "payload": {"ride_id": "bad"}})
