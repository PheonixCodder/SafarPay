from __future__ import annotations

from typing import Any
from uuid import uuid4

import pytest
from sqlalchemy import BigInteger, Integer, String
from sqlalchemy.dialects import postgresql
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PgUUID
from sqlalchemy.orm import Mapped, mapped_column
from sp.infrastructure.db.base import Base
from sp.infrastructure.messaging.events import (
    EventPayloadValidationError,
    ServiceRequestAcceptedEvent,
    ServiceRequestCreatedEvent,
)
from sp.infrastructure.messaging.inbox import reserve_inbox_message
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


class FakeInboxResult:
    def scalar_one_or_none(self):
        return None


class FakeInboxSession:
    def __init__(self) -> None:
        self.statements: list[Any] = []

    async def execute(self, statement):
        self.statements.append(statement)
        return FakeInboxResult()


class FakeInboxModel(Base):
    __tablename__ = "fake_inbox_messages_for_contract_test"

    event_id: Mapped[Any] = mapped_column(PgUUID(as_uuid=True), primary_key=True)
    event_type: Mapped[str] = mapped_column(String(160), nullable=False)
    source_topic: Mapped[str | None] = mapped_column(String(160))
    source_partition: Mapped[int | None] = mapped_column(Integer)
    source_offset: Mapped[int | None] = mapped_column(BigInteger)
    aggregate_id: Mapped[str | None] = mapped_column(String(120))
    payload: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    error_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)


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


@pytest.mark.asyncio
async def test_subscriber_can_pass_raw_broker_message_to_handler() -> None:
    consumer = CapturingConsumer()
    subscriber = EventSubscriber(consumer)  # type: ignore[arg-type]
    observed: list[dict[str, Any]] = []

    async def handler(event: ServiceRequestAcceptedEvent, raw_msg: dict[str, Any]) -> None:
        observed.append(raw_msg)

    subscriber.register("service.request.accepted", handler)
    raw_msg = {
        "topic": "ride-events",
        "partition": 3,
        "offset": 42,
        "value": {
            "event_type": "service.request.accepted",
            "payload": {
                "ride_id": str(uuid4()),
                "passenger_user_id": str(uuid4()),
                "driver_id": str(uuid4()),
            },
        },
    }

    await subscriber._dispatch(raw_msg)

    assert observed == [raw_msg]


@pytest.mark.asyncio
async def test_inbox_reservation_ignores_duplicate_event_or_source_offset() -> None:
    session = FakeInboxSession()

    reserved = await reserve_inbox_message(
        session,  # type: ignore[arg-type]
        FakeInboxModel,
        {
            "topic": "ride-events",
            "partition": 0,
            "offset": 1,
            "value": {
                "event_type": "service.request.created",
                "payload": {"ride_id": "ride-1"},
            },
        },
    )

    compiled = str(session.statements[0].compile(dialect=postgresql.dialect()))
    assert reserved is False
    assert "ON CONFLICT DO NOTHING" in compiled
