"""Kafka consumer for the Location Service — matches platform KafkaConsumerWrapper pattern.

Uses the synchronous kafka-python wrapper (KafkaConsumerWrapper.consume_batch via
asyncio.to_thread) — same pattern as ride and bidding services.

Subscribes to: ride-events
Consumer group: location_service_group

Events handled:
  service.request.accepted  → subscribe passenger WS; mark driver ON_RIDE in Redis
  service.request.completed → unsubscribe ride WS; mark driver ONLINE in Redis
  service.request.cancelled → unsubscribe ride WS; mark driver ONLINE in Redis
"""
from __future__ import annotations

import asyncio
import logging
from contextlib import suppress
from uuid import UUID

from sp.core.config import Settings
from sp.infrastructure.messaging.inbox import message_event_id
from sp.infrastructure.messaging.kafka import KafkaConsumerWrapper

from ..domain.models import DriverStatus
from .redis_store import RedisLocationStore
from .websocket_manager import WebSocketManager

logger = logging.getLogger("location.kafka_consumer")

_TOPIC = "ride-events"
_GROUP = "location_service_group"
_POLL_INTERVAL = 0.5  # seconds


class LocationKafkaConsumer:
    """Consumes ride lifecycle events and maintains location subscriptions."""

    def __init__(
        self,
        bootstrap_servers: str,
        store: RedisLocationStore,
        ws_manager: WebSocketManager,
        settings: Settings | None = None,
    ) -> None:
        self._store = store
        self._ws_manager = ws_manager
        self._inbox_ttl = (
            settings.LOCATION_INBOX_TTL_SECONDS if settings else 604800
        )
        self._consumer = KafkaConsumerWrapper(
            bootstrap_servers=bootstrap_servers,
            group_id=_GROUP,
            topics=[_TOPIC],
            client_id="location-consumer",
        )
        self._task: asyncio.Task | None = None

    async def start(self) -> None:
        self._task = asyncio.create_task(
            self._consume_loop(), name="location_kafka_consumer"
        )
        logger.info("LocationKafkaConsumer started — listening on '%s'", _TOPIC)

    async def stop(self) -> None:
        if self._task:
            self._task.cancel()
            with suppress(asyncio.CancelledError):
                await self._task
        self._consumer.close()
        logger.info("LocationKafkaConsumer stopped")

    # ------------------------------------------------------------------
    # Main loop
    # ------------------------------------------------------------------

    async def _consume_loop(self) -> None:
        while True:
            try:
                messages = await self._consumer.consume_batch(timeout_ms=500)
                had_error = False
                for msg in messages:
                    try:
                        await self._dispatch(msg)
                    except Exception as exc:  # noqa: BLE001
                        had_error = True
                        logger.exception(
                            "Error handling Kafka message offset=%s: %s",
                            msg.get("offset"), exc,
                        )
                if messages and not had_error:
                    await self._consumer.commit_safe()
            except asyncio.CancelledError:
                raise
            except Exception as exc:  # noqa: BLE001
                logger.exception("LocationKafkaConsumer loop error: %s", exc)
                await asyncio.sleep(2)

    async def _dispatch(self, msg: dict) -> None:
        payload = msg.get("value", {})
        if not isinstance(payload, dict):
            return
        event_type: str = payload.get("event_type", "")
        data = payload.get("payload", {})
        if not isinstance(data, dict):
            logger.warning("Kafka event payload must be an object: %s", event_type)
            return
        if event_type in {
            "service.request.accepted",
            "service.request.completed",
            "service.request.cancelled",
        }:
            event_id = message_event_id(msg)
            reserved = await self._store.reserve_inbox_event(
                event_id,
                ttl=self._inbox_ttl,
            )
            if not reserved:
                logger.info("Skipping duplicate location event_id=%s", event_id)
                return

        match event_type:
            case "service.request.accepted":
                await self._on_ride_accepted(data)
            case "service.request.completed" | "service.request.cancelled":
                await self._on_ride_ended(data)
            case _:
                pass  # Not relevant to location service

    # ------------------------------------------------------------------
    # Handlers
    # ------------------------------------------------------------------

    async def _on_ride_accepted(self, data: dict) -> None:
        """Subscribe passenger to ride location feed; mark driver ON_RIDE;
        cache ride participants for authorization."""
        try:
            ride_id = UUID(data["ride_id"])
            driver_id = UUID(data["driver_id"])
            passenger_user_id = UUID(data["passenger_user_id"])
        except (KeyError, ValueError) as exc:
            logger.error("service.request.accepted: bad payload — %s", exc)
            return

        # 1. Subscribe passenger to the live location WebSocket feed
        self._ws_manager.subscribe_ride(ride_id, passenger_user_id)

        # 2. Mark driver ON_RIDE in Redis
        await self._store.set_driver_status(
            driver_id=driver_id,
            status=DriverStatus.ON_RIDE,
            ride_id=ride_id,
        )

        # 3. Cache participant IDs for secure ride-location authorization
        await self._store.set_ride_participants(
            ride_id=ride_id,
            driver_id=driver_id,
            passenger_user_id=passenger_user_id,
        )

        logger.info(
            "ride_id=%s | Accepted — driver=%s ON_RIDE, passenger=%s subscribed, "
            "participants cached",
            ride_id, driver_id, passenger_user_id,
        )

    async def _on_ride_ended(self, data: dict) -> None:
        """Clear ride subscriptions; return driver to ONLINE; remove participant cache."""
        try:
            ride_id = UUID(data["ride_id"])
        except (KeyError, ValueError) as exc:
            logger.error("ride ended event: bad payload — %s", exc)
            return

        driver_id = None
        driver_id_str = data.get("driver_id") or data.get("assigned_driver_id")
        if driver_id_str:
            try:
                driver_id = UUID(driver_id_str)
            except ValueError:
                logger.warning(
                    "ride_id=%s | ride ended event has invalid driver id: %s",
                    ride_id,
                    driver_id_str,
                )

        if driver_id is None:
            participants = await self._store.get_ride_participants(ride_id)
            if participants:
                driver_id = participants[0]

        # 1. Clear WebSocket subscriptions
        self._ws_manager.unsubscribe_all_from_ride(ride_id)

        # 2. Return driver to ONLINE
        if driver_id:
            await self._store.set_driver_status(
                driver_id=driver_id,
                status=DriverStatus.ONLINE,
                ride_id=None,
            )
        else:
            logger.warning(
                "ride_id=%s | ended without driver id; skipped driver status update",
                ride_id,
            )

        # 3. Delete participant auth cache
        await self._store.delete_ride_participants(ride_id)

        logger.info(
            "ride_id=%s | Ended — driver=%s ONLINE, subscriptions + participant cache cleared",
            ride_id, driver_id,
        )
