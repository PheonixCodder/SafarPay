"""Concrete LocationEventPublisher — wraps platform EventPublisher.

Publishes typed domain events to the ``location-events`` Kafka topic.
Implements LocationEventPublisherProtocol from domain/interfaces.py.
"""
from __future__ import annotations

import logging
from uuid import UUID

from sp.infrastructure.messaging.events import (
    DriverLocationUpdatedEvent,
    DriverStatusChangedEvent,
    PassengerLocationUpdatedEvent,
)
from sp.infrastructure.messaging.publisher import EventPublisher

from ..domain.models import DriverStatus, LocationUpdate

logger = logging.getLogger("location.event_publisher")


class LocationEventPublisher:
    """Concrete Kafka event publisher for location domain events."""

    def __init__(self, publisher: EventPublisher) -> None:
        self._pub = publisher

    async def publish_driver_location_updated(
        self,
        driver_id: UUID,
        update: LocationUpdate,
    ) -> None:
        event = DriverLocationUpdatedEvent(
            payload={
                "driver_id": str(driver_id),
                "lat": update.latitude,
                "lng": update.longitude,
                "speed_kmh": update.speed_kmh,
                "heading_degrees": update.heading_degrees,
                "accuracy_meters": update.accuracy_meters,
                "ride_id": str(update.ride_id) if update.ride_id else None,
                "recorded_at": update.recorded_at.isoformat(),
            }
        )
        await self._pub.publish(event)

    async def publish_driver_status_changed(
        self,
        driver_id: UUID,
        status: DriverStatus,
        ride_id: UUID | None = None,
    ) -> None:
        event = DriverStatusChangedEvent(
            payload={
                "driver_id": str(driver_id),
                "status": status.value,
                "ride_id": str(ride_id) if ride_id else None,
            }
        )
        await self._pub.publish(event)

    async def publish_passenger_location_updated(
        self,
        user_id: UUID,
        update: LocationUpdate,
    ) -> None:
        event = PassengerLocationUpdatedEvent(
            payload={
                "user_id": str(user_id),
                "lat": update.latitude,
                "lng": update.longitude,
                "ride_id": str(update.ride_id) if update.ride_id else None,
                "recorded_at": update.recorded_at.isoformat(),
            }
        )
        await self._pub.publish(event)
