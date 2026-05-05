from __future__ import annotations

from uuid import uuid4

import pytest

from location.application.use_cases import GetRideLocationsUseCase
from location.domain.exceptions import UnauthorisedLocationAccessError
from location.domain.models import ActorType
from location.infrastructure.rate_limiter import LocationRateLimiter


class FakeLocationStore:
    def __init__(self, ride_id, driver_id, passenger_user_id) -> None:
        self.ride_id = ride_id
        self.driver_id = driver_id
        self.passenger_user_id = passenger_user_id

    async def get_ride_participants(self, ride_id):
        if ride_id != self.ride_id:
            return None
        return self.driver_id, self.passenger_user_id

    async def get_driver_location(self, driver_id):
        return None

    async def get_passenger_location(self, user_id):
        return None


@pytest.mark.asyncio
async def test_ride_locations_authorizes_passenger_user_id() -> None:
    ride_id = uuid4()
    driver_id = uuid4()
    passenger_user_id = uuid4()
    uc = GetRideLocationsUseCase(FakeLocationStore(ride_id, driver_id, passenger_user_id))

    response = await uc.execute(
        ride_id=ride_id,
        caller_user_id=passenger_user_id,
        caller_driver_id=None,
    )

    assert response.ride_id == ride_id


@pytest.mark.asyncio
async def test_ride_locations_authorizes_resolved_driver_id() -> None:
    ride_id = uuid4()
    driver_user_id = uuid4()
    driver_id = uuid4()
    passenger_user_id = uuid4()
    uc = GetRideLocationsUseCase(FakeLocationStore(ride_id, driver_id, passenger_user_id))

    response = await uc.execute(
        ride_id=ride_id,
        caller_user_id=driver_user_id,
        caller_driver_id=driver_id,
    )

    assert response.ride_id == ride_id


@pytest.mark.asyncio
async def test_ride_locations_rejects_unrelated_passenger() -> None:
    ride_id = uuid4()
    uc = GetRideLocationsUseCase(FakeLocationStore(ride_id, uuid4(), uuid4()))

    with pytest.raises(UnauthorisedLocationAccessError):
        await uc.execute(
            ride_id=ride_id,
            caller_user_id=uuid4(),
            caller_driver_id=None,
        )


@pytest.mark.asyncio
async def test_ride_locations_rejects_unrelated_driver() -> None:
    ride_id = uuid4()
    uc = GetRideLocationsUseCase(FakeLocationStore(ride_id, uuid4(), uuid4()))

    with pytest.raises(UnauthorisedLocationAccessError):
        await uc.execute(
            ride_id=ride_id,
            caller_user_id=uuid4(),
            caller_driver_id=uuid4(),
        )


class FakeCache:
    def __init__(self) -> None:
        self.calls: list[tuple[str, str, int]] = []

    async def increment(self, namespace: str, key: str, ttl: int) -> int:
        self.calls.append((namespace, key, ttl))
        return len([call for call in self.calls if call[0] == namespace and call[1] == key])


@pytest.mark.asyncio
async def test_rate_limiter_separates_driver_and_passenger_keys_for_same_uuid() -> None:
    actor_id = uuid4()
    cache = FakeCache()
    limiter = LocationRateLimiter(cache)

    assert await limiter.allow(actor_id, actor_type=ActorType.DRIVER)
    assert await limiter.allow(actor_id, actor_type=ActorType.PASSENGER)

    keys = [key for _, key, _ in cache.calls]
    assert keys == [f"driver:{actor_id}", f"passenger:{actor_id}"]
