from __future__ import annotations

from typing import Any

import pytest
from ride.infrastructure.kafka_consumer import RideKafkaConsumer
from ride.infrastructure.websocket_manager import DriverEvent

from tests.ride.conftest import DRIVER_ID, FakeCache, FakeRideWebSockets


def _unused_session_factory() -> Any:
    raise AssertionError("bidding-mode matching notifications must not touch ride state")


@pytest.mark.asyncio
async def test_matching_completed_for_hybrid_broadcasts_new_job_without_assignment() -> None:
    ws = FakeRideWebSockets()
    consumer = RideKafkaConsumer(
        bootstrap_servers="localhost:9092",
        session_factory=_unused_session_factory,
        cache=FakeCache(),
        ws=ws,
    )

    await consumer._process_message(
        {
            "value": {
                "event_type": "driver.matching.completed",
                "payload": {
                    "ride_id": "11111111-1111-1111-1111-111111111111",
                    "pricing_mode": "HYBRID",
                    "selected_driver": {"driver_id": str(DRIVER_ID)},
                },
            }
        }
    )

    assert ws.driver_events == [
        (
            DRIVER_ID,
            DriverEvent.NEW_JOB,
            {
                "ride_id": "11111111-1111-1111-1111-111111111111",
                "pricing_mode": "HYBRID",
            },
        )
    ]


@pytest.mark.asyncio
async def test_matching_completed_for_fixed_broadcasts_new_job_without_assignment() -> None:
    ws = FakeRideWebSockets()
    consumer = RideKafkaConsumer(
        bootstrap_servers="localhost:9092",
        session_factory=_unused_session_factory,
        cache=FakeCache(),
        ws=ws,
    )

    await consumer._process_message(
        {
            "value": {
                "event_type": "driver.matching.completed",
                "payload": {
                    "ride_id": "22222222-2222-2222-2222-222222222222",
                    "pricing_mode": "FIXED",
                    "selected_driver": {"driver_id": str(DRIVER_ID)},
                },
            }
        }
    )

    assert ws.driver_events == [
        (
            DRIVER_ID,
            DriverEvent.NEW_JOB,
            {
                "ride_id": "22222222-2222-2222-2222-222222222222",
                "pricing_mode": "FIXED",
            },
        )
    ]
