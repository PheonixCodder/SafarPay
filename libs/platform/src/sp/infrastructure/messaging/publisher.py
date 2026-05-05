"""Event publisher — accepts typed BaseEvent objects.

EventPublisher is created at service lifespan startup with a wired KafkaProducerWrapper.
It is stored on app.state.publisher and injected via a Depends provider.
"""
from __future__ import annotations

import logging

from .events import BaseEvent, validate_event_payload
from .kafka import KafkaProducerWrapper

logger = logging.getLogger("platform.messaging.publisher")


class EventPublisher:
    """Publishes typed BaseEvent objects to a Kafka topic."""

    def __init__(
        self,
        topic: str,
        producer: KafkaProducerWrapper | None = None,
    ) -> None:
        self.topic = topic
        self._producer = producer

    def set_producer(self, producer: KafkaProducerWrapper) -> None:
        """Wire in a producer after construction (e.g. at lifespan startup)."""
        self._producer = producer

    async def publish(self, event: BaseEvent) -> bool:
        """Serialize and publish a typed event. Returns True on success."""
        return await self.publish_to_topic(self.topic, event)

    async def publish_to_topic(self, topic: str, event: BaseEvent) -> bool:
        """Serialize and publish a typed event to an explicit Kafka topic."""
        validate_event_payload(event)

        if not self._producer:
            logger.warning(
                "No Kafka producer. Event dropped: type=%s topic=%s",
                event.event_type,
                topic,
            )
            return False

        payload = event.model_dump(mode="json")
        headers = [
            ("event_type", event.event_type.encode()),
            ("event_version", str(event.version).encode()),
            ("idempotency_key", event.idempotency_key.encode()),
        ]
        if event.correlation_id:
            headers.append(("correlation_id", event.correlation_id.encode()))

        return await self._producer.send(
            topic=topic,
            value=payload,
            key=str(event.event_id),
            headers=headers,
        )

    async def close(self) -> None:
        if self._producer:
            await self._producer.close()
