from __future__ import annotations

from typing import Any
from uuid import uuid4

import pytest
from sp.infrastructure.messaging.events import (
    EventPayloadValidationError,
    ServiceRequestAcceptedEvent,
    ServiceRequestCreatedEvent,
)
from sp.infrastructure.messaging.publisher import EventPublisher
from sp.infrastructure.messaging.subscriber import EventSubscriber


class CapturingProducer:
    def __init__(self) -> None:
        self.sent: list[dict[str, Any]] = []

    async def send(
        self,
        topic: str,
        value: dict[str, Any],
        key: str | None = None,
        headers: list[tuple] | None = None,
    ) -> bool:
        self.sent.append({"topic": topic, "value": value, "key": key, "headers": headers})
        return True

    async def close(self) -> None:
        pass


class CapturingConsumer:
    def __init__(self) -> None:
        self.dlq: list[tuple[str, dict[str, Any], str]] = []

    async def consume_batch(self, timeout_ms: int = 500) -> list[dict[str, Any]]:
        return []

    def commit(self) -> None:
        pass

    async def send_to_dlq(self, topic: str, message: dict[str, Any], error: str) -> None:
        self.dlq.append((topic, message, error))

    def close(self) -> None:
        pass


@pytest.mark.asyncio
async def test_publisher_validates_known_event_payload_before_kafka_send() -> None:
    producer = CapturingProducer()
    publisher = EventPublisher("ride-events", producer=producer)  # type: ignore[arg-type]

    event = ServiceRequestCreatedEvent(
        payload={
            "ride_id": str(uuid4()),
            "passenger_user_id": str(uuid4()),
            "service_type": "CITY_RIDE",
            "pricing_mode": "FIXED",
        }
    )

    assert await publisher.publish(event) is True
    assert producer.sent[0]["topic"] == "ride-events"
    assert producer.sent[0]["value"]["event_type"] == "service.request.created"


@pytest.mark.asyncio
async def test_publisher_rejects_known_event_with_missing_consumer_payload_fields() -> None:
    publisher = EventPublisher("ride-events", producer=CapturingProducer())  # type: ignore[arg-type]

    with pytest.raises(EventPayloadValidationError):
        await publisher.publish(
            ServiceRequestAcceptedEvent(
                payload={
                    "ride_id": str(uuid4()),
                    "passenger_user_id": str(uuid4()),
                }
            )
        )


@pytest.mark.asyncio
async def test_subscriber_sends_invalid_known_event_payload_to_dlq() -> None:
    consumer = CapturingConsumer()
    subscriber = EventSubscriber(consumer)  # type: ignore[arg-type]
    handled: list[Any] = []

    async def handler(event: ServiceRequestAcceptedEvent) -> None:
        handled.append(event)

    subscriber.register("service.request.accepted", handler)

    await subscriber._dispatch(
        {
            "topic": "ride-events",
            "value": {
                "event_type": "service.request.accepted",
                "payload": {
                    "ride_id": str(uuid4()),
                    "passenger_user_id": str(uuid4()),
                },
            },
        }
    )

    assert handled == []
    assert consumer.dlq
    assert consumer.dlq[0][0] == "ride-events"
    assert "driver_id" in consumer.dlq[0][2]
