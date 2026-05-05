"""Kafka producer and consumer wrappers.

kafka-python is synchronous. All blocking calls are wrapped in asyncio.to_thread
so they never block the FastAPI event loop.

DLQ (Dead Letter Queue) support:
    Failed messages are forwarded to <topic>.dlq for manual inspection and replay.
"""
from __future__ import annotations

import asyncio
import json
import logging
from typing import Any

logger = logging.getLogger("platform.messaging.kafka")

try:
    from kafka import KafkaConsumer
    from kafka import KafkaProducer as _KafkaProducer

    KAFKA_AVAILABLE = True
except ImportError:
    KAFKA_AVAILABLE = False
    logger.warning(
        "kafka-python not installed. Messaging will fall back to warning logs."
    )


class KafkaProducerWrapper:
    """Async-safe Kafka producer wrapping synchronous kafka-python."""

    def __init__(
        self,
        bootstrap_servers: str,
        client_id: str = "safarpay-producer",
    ) -> None:
        self._producer = None
        if not KAFKA_AVAILABLE:
            return
        try:
            self._producer = _KafkaProducer(
                bootstrap_servers=bootstrap_servers,
                client_id=client_id,
                value_serializer=lambda v: json.dumps(v, default=str).encode("utf-8"),
                key_serializer=lambda k: k.encode("utf-8") if k else None,
                acks="all",
                retries=3,
                batch_size=16384,
                linger_ms=10,
            )
        except Exception as exc:
            logger.error("Failed to initialise Kafka producer: %s", exc)

    async def send(
        self,
        topic: str,
        value: dict[str, Any],
        key: str | None = None,
        headers: list[tuple] | None = None,
    ) -> bool:
        if not self._producer:
            logger.warning("Kafka unavailable. Dropped message to topic=%s", topic)
            return False
        try:
            future = self._producer.send(
                topic, key=key, value=value, headers=headers or []
            )
            await asyncio.to_thread(future.get, timeout=10)
            return True
        except Exception as exc:
            logger.error("Failed to send to topic=%s: %s", topic, exc)
            return False

    async def flush(self) -> None:
        if self._producer:
            await asyncio.to_thread(self._producer.flush)

    async def close(self) -> None:
        if self._producer:
            await asyncio.to_thread(self._producer.close)


class KafkaConsumerWrapper:
    """Async-safe Kafka consumer using batch polling via asyncio.to_thread."""

    def __init__(
        self,
        bootstrap_servers: str,
        group_id: str,
        topics: list[str],
        client_id: str = "safarpay-consumer",
        dlq_producer: KafkaProducerWrapper | None = None,
    ) -> None:
        self._topics = topics
        self._dlq_producer = dlq_producer
        self._consumer = None

        if not KAFKA_AVAILABLE:
            return
        try:
            self._consumer = KafkaConsumer(
                *topics,
                bootstrap_servers=bootstrap_servers,
                group_id=group_id,
                client_id=client_id,
                value_deserializer=lambda v: json.loads(v.decode("utf-8")),
                key_deserializer=lambda v: v.decode("utf-8") if v else None,
                auto_offset_reset="latest",
                enable_auto_commit=False,   # manual commit after handler success
                consumer_timeout_ms=1000,
            )
        except Exception as exc:
            logger.error("Failed to initialise Kafka consumer: %s", exc)

    def _poll_batch_sync(self, timeout_ms: int = 500) -> list[dict[str, Any]]:
        """Synchronous batch poll. Runs in thread pool."""
        if not self._consumer:
            return []
        records = self._consumer.poll(timeout_ms=timeout_ms, max_records=50)
        messages = []
        for _tp, msgs in records.items():
            for msg in msgs:
                messages.append(
                    {
                        "topic": msg.topic,
                        "partition": msg.partition,
                        "offset": msg.offset,
                        "key": msg.key,
                        "value": msg.value,
                        "headers": dict(msg.headers) if msg.headers else {},
                    }
                )
        return messages

    async def consume_batch(self, timeout_ms: int = 500) -> list[dict[str, Any]]:
        """Async wrapper for batch polling."""
        return await asyncio.to_thread(self._poll_batch_sync, timeout_ms)

    def commit(self) -> None:
        if self._consumer:
            self._consumer.commit()

    async def commit_safe(self, *, retries: int = 3, backoff_seconds: float = 0.5) -> bool:
        """Commit offsets without letting broker failures kill consumer loops."""
        if not self._consumer:
            return True
        for attempt in range(1, retries + 1):
            try:
                await asyncio.to_thread(self._consumer.commit)
                return True
            except Exception as exc:
                logger.exception(
                    "Kafka commit failed attempt=%s/%s: %s",
                    attempt,
                    retries,
                    exc,
                )
                if attempt < retries:
                    await asyncio.sleep(backoff_seconds * attempt)
        return False

    async def send_to_dlq(
        self, topic: str, message: dict[str, Any], error: str
    ) -> None:
        """Forward a poison-pill message to <topic>.dlq for later inspection."""
        if self._dlq_producer:
            dlq_topic = f"{topic}.dlq"
            await self._dlq_producer.send(dlq_topic, {**message, "_dlq_error": error})
            logger.warning("Message forwarded to DLQ: %s", dlq_topic)

    def close(self) -> None:
        if self._consumer:
            self._consumer.close()
