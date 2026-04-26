"""Ride service repository and external client protocols.

All protocols use structural typing (typing.Protocol) so concrete
implementations need not inherit from them — duck typing is enough.
This keeps the domain layer free of any framework imports.
"""
from __future__ import annotations

from datetime import datetime
from typing import Any, Protocol
from uuid import UUID

from .models import (
    DriverCandidate,
    ProofImage,
    RideStatus,
    ServiceRequest,
    Stop,
    VerificationCode,
)


# ---------------------------------------------------------------------------
# Repository protocols
# ---------------------------------------------------------------------------

class ServiceRequestRepositoryProtocol(Protocol):
    """Persistence contract for the ServiceRequest aggregate."""

    async def create_full(
        self,
        ride: ServiceRequest,
        stops: list[Stop],
        detail_data: dict[str, Any],
    ) -> ServiceRequest:
        """
        Atomically persist a new ride, its stops, and its type-specific
        detail row in a single database transaction.
        """
        ...

    async def find_by_id(
        self,
        ride_id: UUID,
        *,
        load_relations: bool = True,
    ) -> ServiceRequest | None:
        """Return a ride aggregate with all child relations eager-loaded."""
        ...

    async def find_by_passenger(
        self,
        passenger_id: UUID,
        *,
        status_filter: list[RideStatus] | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> list[ServiceRequest]:
        """Return paginated rides for a passenger, optionally filtered by status."""
        ...

    async def update_status(
        self,
        ride_id: UUID,
        status: RideStatus,
        *,
        accepted_at: datetime | None = None,
        completed_at: datetime | None = None,
        cancelled_at: datetime | None = None,
        cancellation_reason: str | None = None,
        assigned_driver_id: UUID | None = None,
        final_price: float | None = None,
    ) -> None:
        """Patch lifecycle fields without loading the full aggregate."""
        ...


class StopRepositoryProtocol(Protocol):
    """Persistence contract for ServiceStop entities."""

    async def create(self, stop: Stop) -> Stop:
        ...

    async def find_by_id(self, stop_id: UUID) -> Stop | None:
        ...

    async def find_by_ride(self, ride_id: UUID) -> list[Stop]:
        ...

    async def update_arrived_at(
        self, stop_id: UUID, arrived_at: datetime
    ) -> None:
        ...

    async def update_completed_at(
        self, stop_id: UUID, completed_at: datetime
    ) -> None:
        ...


class ProofImageRepositoryProtocol(Protocol):
    """Persistence contract for ServiceProofImage entities."""

    async def create(self, proof: ProofImage) -> ProofImage:
        ...

    async def find_by_ride(self, ride_id: UUID) -> list[ProofImage]:
        ...

    async def find_by_stop(self, stop_id: UUID) -> list[ProofImage]:
        ...


class VerificationCodeRepositoryProtocol(Protocol):
    """Persistence contract for ServiceVerificationCode entities."""

    async def create(self, code: VerificationCode) -> VerificationCode:
        ...

    async def find_active_by_ride(
        self,
        ride_id: UUID,
        stop_id: UUID | None = None,
    ) -> VerificationCode | None:
        """Return the most recent unverified code for a ride (optionally per-stop)."""
        ...

    async def update_verification(self, code: VerificationCode) -> None:
        """Persist attempt count, is_verified, verified_at, verified_by fields."""
        ...


# ---------------------------------------------------------------------------
# External client protocols
# ---------------------------------------------------------------------------

class GeospatialClientProtocol(Protocol):
    """Contract for querying nearby drivers from the geospatial service."""

    async def find_nearby_drivers(
        self,
        latitude: float,
        longitude: float,
        radius_km: float,
        *,
        category: str | None = None,
        vehicle_type: str | None = None,
        fuel_types: list[str] | None = None,
        limit: int = 20,
    ) -> list[DriverCandidate]:
        ...


class WebhookClientProtocol(Protocol):
    """Contract for sending ride job notifications downstream via webhook."""

    async def dispatch_ride_job(
        self,
        driver_id: UUID,
        ride_id: UUID,
        payload: dict[str, Any],
        *,
        idempotency_key: str,
    ) -> bool:
        """Send a ride-job webhook to the notification/dispatch service.

        Returns True if the request was accepted (2xx), False otherwise.
        Implementations are expected to retry on transient failures.
        """
        ...


class NotificationClientProtocol(Protocol):
    """Contract for sending push/SMS notifications via the notification service."""

    async def send_ride_notification(
        self,
        recipient_id: UUID,
        template: str,
        context: dict[str, Any],
    ) -> bool:
        ...
