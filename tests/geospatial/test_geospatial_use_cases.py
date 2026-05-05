from __future__ import annotations

# ruff: noqa: E402,I001

import sys
from datetime import datetime, time, timezone
from pathlib import Path
from typing import Any, cast
from uuid import uuid4

import pytest

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from geospatial.application.use_cases import (
    CalculateETAUseCase,
    CalculateSurgeMultiplierUseCase,
    FindNearbyDriversUseCase,
    ManageServiceZonesUseCase,
    MatchDriverForRideUseCase,
    ValidatePickupInServiceAreaUseCase,
)
from geospatial.domain.exceptions import NoDriversAvailableError
from geospatial.domain.models import Coordinates, MatchingCriteria, ZoneType

from tests.geospatial.conftest import (
    DRIVER_ID,
    OTHER_DRIVER_ID,
    RIDE_ID,
    FakeH3,
    FakeLocationProvider,
    FakeRouting,
    FakeSpatialRepo,
    make_candidate,
    make_zone,
)


def test_matching_criteria_and_service_zone_time_windows() -> None:
    assert MatchingCriteria(pickup=Coordinates(31.5, 74.3), radius_km=1, max_candidates=1).is_valid
    assert not MatchingCriteria(pickup=Coordinates(31.5, 74.3), radius_km=0).is_valid

    assert make_zone(is_active=False).is_currently_active() is False
    assert make_zone().is_currently_active() is True

    now = datetime.now(timezone.utc).time()
    active = make_zone(active_from=time(0, 0), active_until=time(23, 59))
    assert active.is_currently_active() is True
    wrapping = make_zone(active_from=time(23, 0), active_until=time(6, 0))
    assert wrapping.is_currently_active() == (now >= time(23, 0) or now <= time(6, 0))


@pytest.mark.asyncio
async def test_find_nearby_drivers_filters_enriches_h3_scores_and_limits_results() -> None:
    candidates = [
        make_candidate(DRIVER_ID, distance=1, vehicle_type="SEDAN", rating=4.9, priority=1),
        make_candidate(OTHER_DRIVER_ID, distance=3, vehicle_type="BIKE", rating=4.8),
        make_candidate(uuid4(), distance=2, vehicle_type="SEDAN", rating=3.0),
    ]
    location = FakeLocationProvider(candidates)
    routing = FakeRouting()
    h3 = FakeH3()
    uc = FindNearbyDriversUseCase(cast(Any, location), cast(Any, routing), cast(Any, h3), h3_resolution=9)

    result = await uc.execute(
        MatchingCriteria(
            pickup=Coordinates(31.52, 74.35),
            radius_km=5,
            max_candidates=1,
            required_vehicle_type="SEDAN",
            min_rating=4.0,
        )
    )

    assert location.calls[0]["limit"] == 2
    assert len(result) == 1
    assert result[0].driver_id == DRIVER_ID
    assert result[0].estimated_arrival_minutes == 5
    assert result[0].h3_cell is not None
    assert result[0].composite_score > 0


@pytest.mark.asyncio
async def test_find_nearby_drivers_uses_distance_eta_fallback_when_matrix_fails() -> None:
    location = FakeLocationProvider([make_candidate(distance=3)])
    routing = FakeRouting()
    routing.fail_matrix = True

    result = await FindNearbyDriversUseCase(
        cast(Any, location),
        cast(Any, routing),
    ).execute(MatchingCriteria(pickup=Coordinates(31.52, 74.35), radius_km=5))

    assert result[0].estimated_arrival_minutes == 6


@pytest.mark.asyncio
async def test_match_driver_for_ride_applies_zone_and_surge_and_raises_when_empty() -> None:
    spatial = FakeSpatialRepo()
    find_uc = FindNearbyDriversUseCase(
        cast(Any, FakeLocationProvider([make_candidate(DRIVER_ID, distance=1)])),
        cast(Any, FakeRouting()),
    )

    result = await MatchDriverForRideUseCase(cast(Any, find_uc), cast(Any, spatial)).execute(
        RIDE_ID,
        MatchingCriteria(pickup=Coordinates(31.52, 74.35), radius_km=5),
    )

    assert result.selected_driver is not None
    assert result.selected_driver.driver_id == DRIVER_ID
    assert result.surge_multiplier == 1.5
    assert result.pickup_zone == "Lahore Core"

    empty_find = FindNearbyDriversUseCase(cast(Any, FakeLocationProvider([])), cast(Any, FakeRouting()))
    with pytest.raises(NoDriversAvailableError):
        await MatchDriverForRideUseCase(cast(Any, empty_find), cast(Any, spatial)).execute(
            RIDE_ID,
            MatchingCriteria(pickup=Coordinates(31.52, 74.35), radius_km=5),
        )


@pytest.mark.asyncio
async def test_eta_surge_pickup_validation_and_zone_management_use_cases() -> None:
    routing = FakeRouting()
    route = await CalculateETAUseCase(cast(Any, routing)).execute(
        Coordinates(31.5, 74.3),
        Coordinates(31.6, 74.4),
    )
    assert route.distance_km == 5.0

    repo = FakeSpatialRepo()
    surge = await CalculateSurgeMultiplierUseCase(cast(Any, repo)).execute(31.52, 74.35)
    assert surge.surge_multiplier == 1.5

    inactive = make_zone(is_active=False)
    repo.zones.append(inactive)
    valid, zones, surge_multiplier = await ValidatePickupInServiceAreaUseCase(cast(Any, repo)).execute(31.52, 74.35)
    assert valid is True
    assert inactive not in zones
    assert surge_multiplier == 1.5

    manager = ManageServiceZonesUseCase(cast(Any, repo))
    zone = make_zone(name="Airport", zone_type=ZoneType.AIRPORT)
    assert await manager.create_zone(zone) == zone
    assert zone in await manager.list_zones()
    assert await manager.get_zone(zone.id) == zone
    assert await manager.deactivate_zone(zone.id) is True
    assert repo.deactivated == [zone.id]
