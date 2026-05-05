"""Event subscriber with retry logic and DLQ forwarding.

Start the consume loop as an asyncio background task during lifespan:
    asyncio.create_task(subscriber.start())
"""
from __future__ import annotations

import asyncio
import logging
from collections.abc import Callable

from .events import EVENT_REGISTRY, BaseEvent, validate_event_payload
from .kafka import KafkaConsumerWrapper

logger = logging.getLogger("platform.messaging.subscriber")


class EventSubscriber:
    """Consumes typed events with per-type handler routing and DLQ fallback."""

    def __init__(
        self,
        consumer: KafkaConsumerWrapper,
        max_retries: int = 3,
    ) -> None:
        self._consumer = consumer
        self._max_retries = max_retries
        self._handlers: dict[str, Callable] = {}
        self._running = False

    def register(self, event_type: str, handler: Callable) -> None:
        """Register an async handler for a specific event type."""
        self._handlers[event_type] = handler
        logger.info("Registered handler for event_type=%s", event_type)

    async def start(self) -> None:
        """Blocking consume loop. Run via asyncio.create_task(subscriber.start())."""
        self._running = True
        logger.info("EventSubscriber started")
        while self._running:
            try:
                messages = await self._consumer.consume_batch(timeout_ms=500)
                for msg in messages:
                    await self._dispatch(msg)
                if messages:
                    self._consumer.commit()
            except asyncio.CancelledError:
                break
            except Exception as exc:
                logger.error("Consumer loop error: %s", exc)
                await asyncio.sleep(1)

    async def stop(self) -> None:
        self._running = False
        self._consumer.close()

    async def _dispatch(self, raw_msg: dict) -> None:
        value = raw_msg.get("value", {})
        event_type = value.get("event_type")
        handler = self._handlers.get(event_type)

        if not handler:
            return  # No handler registered — intentionally ignored

        # Deserialise to typed event
        event_class = EVENT_REGISTRY.get(event_type, BaseEvent)
        try:
            event = event_class.model_validate(value)
            validate_event_payload(event)
        except Exception as exc:
            logger.error("Deserialisation failed for %s: %s", event_type, exc)
            await self._consumer.send_to_dlq(raw_msg["topic"], value, str(exc))
            return

        # Retry loop with exponential back-off
        for attempt in range(1, self._max_retries + 1):
            try:
                await handler(event)
                return
            except Exception as exc:
                logger.warning(
                    "Handler failed for %s (attempt %d/%d): %s",
                    event_type,
                    attempt,
                    self._max_retries,
                    exc,
                )
                if attempt < self._max_retries:
                    await asyncio.sleep(2**attempt)

        logger.error("Max retries exhausted for %s. Sending to DLQ.", event_type)
        await self._consumer.send_to_dlq(
            raw_msg["topic"], value, "max_retries_exceeded"
        )
