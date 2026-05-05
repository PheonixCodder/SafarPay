from __future__ import annotations

import asyncio
from datetime import datetime, timedelta, timezone
from typing import Any, cast

import pytest
from location.application.schemas import DriverStatusRequest, LocationUpdateRequest
from location.application.use_cases import (
    GeocodeUseCase,
    GetCurrentDriverLocationUseCase,
    GetLocationHistoryUseCase,
    GetNearbyDriversUseCase,
    GetRideLocationsUseCase,
    ReverseGeocodeUseCase,
    SetDriverStatusUseCase,
    UpdateDriverLocationUseCase,
    UpdatePassengerLocationUseCase,
)
from location.domain.exceptions import (
    GPSAccuracyTooLowError,
    ImpossibleJumpError,
    InvalidCoordinatesError,
    RateLimitExceededError,
    StaleLocationError,
    UnauthorisedLocationAccessError,
)
from location.domain.models import ActorType, DriverStatus, LocationUpdate

from tests.location.conftest import (
    DRIVER_ID,
    OTHER_DRIVER_ID,
    OTHER_USER_ID,
    PASSENGER_ID,
    RIDE_ID,
    FakeHistory,
    FakeLimiter,
    FakeLocationStore,
    FakeMapbox,
    FakePublisher,
    FakeWs,
    location_payload,
    make_driver_location,
    make_history,
    make_passenger_location,
    make_update,
)


def req(**overrides: Any) -> LocationUpdateRequest:
    return LocationUpdateRequest.model_validate(location_payload(**overrides))


def test_location_update_domain_validation_and_actor_separation() -> None:
    update = make_update(DRIVER_ID, ActorType.DRIVER)
    update.validate()
    assert update.distance_km_to(update) == 0

    with pytest.raises(InvalidCoordinatesError):
        LocationUpdate(
            actor_id=DRIVER_ID,
            actor_type=ActorType.DRIVER,
            latitude=91,
            longitude=74,
            accuracy_meters=10,
            recorded_at=datetime.now(timezone.utc),
        ).validate()

    with pytest.raises(GPSAccuracyTooLowError):
        make_update(DRIVER_ID, ActorType.DRIVER).validate(min_accuracy_meters=1)

    previous = make_update(recorded_at=datetime.now(timezone.utc) - timedelta(seconds=1))
    jump = make_update(recorded_at=datetime.now(timezone.utc), lat=35, lng=75)
    with pytest.raises(ImpossibleJumpError):
        jump.validate(previous=previous)

    passenger_update = make_update(PASSENGER_ID, ActorType.PASSENGER)
    assert passenger_update.actor_id == PASSENGER_ID
    assert passenger_update.actor_type == ActorType.PASSENGER
    assert passenger_update.actor_id != DRIVER_ID


def test_driver_status_transitions_and_staleness() -> None:
    driver = make_driver_location(status=DriverStatus.OFFLINE)
    driver.mark_online()
    assert driver.status == DriverStatus.ONLINE
    driver.mark_on_ride(RIDE_ID)
    assert driver.status == DriverStatus.ON_RIDE
    assert driver.ride_id == RIDE_ID
    driver.mark_offline()
    assert driver.status == DriverStatus.OFFLINE
    assert make_driver_location(stale=True).is_stale()


@pytest.mark.asyncio
async def test_update_driver_location_pipeline_rate_limit_validation_broadcast_history_and_event() -> None:
    store = FakeLocationStore()
    history = FakeHistory()
    limiter = FakeLimiter()
    ws = FakeWs()
    publisher = FakePublisher()
    uc = UpdateDriverLocationUseCase(
        cast(Any, store),
        cast(Any, history),
        cast(Any, limiter),
        cast(Any, ws),
        cast(Any, publisher),
    )

    await uc.execute(DRIVER_ID, req(), ride_id=RIDE_ID)
    await asyncio.sleep(0)

    assert limiter.calls == [(DRIVER_ID, ActorType.DRIVER, True)]
    assert store.drivers[DRIVER_ID].status == DriverStatus.ON_RIDE
    driver_update = store.drivers[DRIVER_ID].last_update
    assert driver_update is not None
    assert driver_update.actor_type == ActorType.DRIVER
    assert ws.broadcasts[0][0:2] == (RIDE_ID, DRIVER_ID)
    assert history.appended[0].actor_id == DRIVER_ID
    assert publisher.driver_locations[0][0] == DRIVER_ID

    with pytest.raises(RateLimitExceededError):
        await UpdateDriverLocationUseCase(
            cast(Any, store),
            cast(Any, history),
            cast(Any, FakeLimiter(False)),
            cast(Any, ws),
        ).execute(DRIVER_ID, req())


@pytest.mark.asyncio
async def test_update_passenger_location_uses_passenger_identity_without_broadcast() -> None:
    store = FakeLocationStore()
    history = FakeHistory()
    limiter = FakeLimiter()

    await UpdatePassengerLocationUseCase(
        cast(Any, store),
        cast(Any, history),
        cast(Any, limiter),
    ).execute(PASSENGER_ID, req(), ride_id=RIDE_ID)
    await asyncio.sleep(0)

    assert limiter.calls == [(PASSENGER_ID, ActorType.PASSENGER, True)]
    passenger_update = store.passengers[PASSENGER_ID].last_update
    assert passenger_update is not None
    assert passenger_update.actor_type == ActorType.PASSENGER
    assert history.appended[0].actor_id == PASSENGER_ID
    assert history.appended[0].actor_id != DRIVER_ID


@pytest.mark.asyncio
async def test_current_driver_and_ride_locations_authorize_by_participant_cache() -> None:
    store = FakeLocationStore()
    store.drivers[DRIVER_ID] = make_driver_location(DRIVER_ID, ride_id=RIDE_ID)
    store.passengers[PASSENGER_ID] = make_passenger_location(PASSENGER_ID, ride_id=RIDE_ID)
    store.participants[RIDE_ID] = (DRIVER_ID, PASSENGER_ID)

    driver = await GetCurrentDriverLocationUseCase(cast(Any, store)).execute(DRIVER_ID)
    assert driver.driver_id == DRIVER_ID

    response = await GetRideLocationsUseCase(cast(Any, store)).execute(
        RIDE_ID,
        caller_user_id=PASSENGER_ID,
        caller_driver_id=None,
    )
    assert response.driver is not None
    assert response.passenger is not None

    response = await GetRideLocationsUseCase(cast(Any, store)).execute(
        RIDE_ID,
        caller_user_id=OTHER_USER_ID,
        caller_driver_id=DRIVER_ID,
    )
    assert response.driver is not None

    with pytest.raises(UnauthorisedLocationAccessError):
        await GetRideLocationsUseCase(cast(Any, store)).execute(
            RIDE_ID,
            caller_user_id=OTHER_USER_ID,
            caller_driver_id=OTHER_DRIVER_ID,
        )

    with pytest.raises(StaleLocationError):
        stale_store = FakeLocationStore()
        stale_store.drivers[DRIVER_ID] = make_driver_location(DRIVER_ID, stale=True)
        await GetCurrentDriverLocationUseCase(cast(Any, stale_store)).execute(DRIVER_ID)


@pytest.mark.asyncio
async def test_nearby_history_status_and_geocoding_use_cases() -> None:
    store = FakeLocationStore()
    store.drivers[DRIVER_ID] = make_driver_location(DRIVER_ID)
    store.drivers[OTHER_DRIVER_ID] = make_driver_location(OTHER_DRIVER_ID, status=DriverStatus.ON_RIDE)

    nearby = await GetNearbyDriversUseCase(cast(Any, store)).execute(31.5, 74.3, 5)
    assert nearby.count == 2

    history = FakeHistory()
    history.records = [make_history()]
    response = await GetLocationHistoryUseCase(cast(Any, history)).execute(
        DRIVER_ID,
        "DRIVER",
        datetime.now(timezone.utc) - timedelta(hours=1),
        datetime.now(timezone.utc),
        caller_role="support",
    )
    assert response.total == 1
    with pytest.raises(UnauthorisedLocationAccessError):
        await GetLocationHistoryUseCase(cast(Any, history)).execute(
            DRIVER_ID,
            "DRIVER",
            datetime.now(timezone.utc) - timedelta(hours=1),
            datetime.now(timezone.utc),
            caller_role="passenger",
        )

    publisher = FakePublisher()
    status = await SetDriverStatusUseCase(cast(Any, store), cast(Any, publisher)).execute(
        DRIVER_ID,
        DriverStatusRequest(status="OFFLINE"),
    )
    await asyncio.sleep(0)
    assert status.success is True
    assert store.removed == [DRIVER_ID]
    assert publisher.statuses[0] == (DRIVER_ID, DriverStatus.OFFLINE)

    geocoder = FakeMapbox()
    assert (await GeocodeUseCase(cast(Any, geocoder)).execute("Model Town")).coordinates.latitude == 31.52
    assert (await ReverseGeocodeUseCase(cast(Any, geocoder)).execute(31.52, 74.35)).city == "Lahore"
