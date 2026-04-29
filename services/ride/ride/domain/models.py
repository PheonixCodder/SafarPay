"""Ride service domain models — pure Python, zero framework imports.

These dataclasses are the canonical in-memory representation of ride
aggregates. They are deliberately decoupled from SQLAlchemy, FastAPI,
Kafka, and Redis. All business rules and lifecycle transitions live here.

ORM field mapping (ServiceRequestORM):
    passenger_id  → ORM.user_id         (FK → auth.users.id, NOT NULL)
    assigned_driver_id → ORM.assigned_driver_id  (FK → verification.drivers.id, nullable)
"""
from __future__ import annotations

import secrets
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from uuid import UUID, uuid4

# ---------------------------------------------------------------------------
# Domain enums  (mirror ORM enum values — no ORM import)
# ---------------------------------------------------------------------------

class RideStatus(str, Enum):
    CREATED = "CREATED"
    MATCHING = "MATCHING"
    ACCEPTED = "ACCEPTED"
    ARRIVING = "ARRIVING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


class ServiceType(str, Enum):
    CITY_RIDE = "CITY_RIDE"
    INTERCITY = "INTERCITY"
    FREIGHT = "FREIGHT"
    COURIER = "COURIER"
    GROCERY = "GROCERY"


class ServiceCategory(str, Enum):
    MINI = "MINI"
    RICKSHAW = "RICKSHAW"
    RIDE_AC = "RIDE_AC"
    PREMIUM = "PREMIUM"
    BIKE = "BIKE"
    COMFORT = "COMFORT"
    SHARE = "SHARE"
    PRIVATE = "PRIVATE"


class PricingMode(str, Enum):
    FIXED = "FIXED"
    BID_BASED = "BID_BASED"
    HYBRID = "HYBRID"


class StopType(str, Enum):
    PICKUP = "PICKUP"
    DROPOFF = "DROPOFF"
    WAYPOINT = "WAYPOINT"


class ProofType(str, Enum):
    PICKUP = "PICKUP"
    DROPOFF = "DROPOFF"


class VehicleType(str, Enum):
    SEDAN = "SEDAN"
    HATCHBACK = "HATCHBACK"
    SUV = "SUV"
    VAN = "VAN"
    BIKE = "BIKE"
    RICKSHAW = "RICKSHAW"
    TRUCK = "TRUCK"
    PICKUP = "PICKUP"
    MINI_TRUCK = "MINI_TRUCK"
    COASTER = "COASTER"
    BUS = "BUS"
    OTHER = "OTHER"


class DriverGenderPreference(str, Enum):
    NO_PREFERENCE = "NO_PREFERENCE"
    MALE = "MALE"
    FEMALE = "FEMALE"
    ANY = "ANY"


class FuelType(str, Enum):
    PETROL = "PETROL"
    DIESEL = "DIESEL"
    CNG = "CNG"
    HYBRID = "HYBRID"
    ELECTRIC = "ELECTRIC"


# ---------------------------------------------------------------------------
# Valid lifecycle transitions
# ---------------------------------------------------------------------------

VALID_TRANSITIONS: dict[RideStatus, frozenset[RideStatus]] = {
    RideStatus.CREATED:     frozenset({RideStatus.MATCHING,     RideStatus.CANCELLED}),
    RideStatus.MATCHING:    frozenset({RideStatus.ACCEPTED,     RideStatus.CANCELLED}),
    RideStatus.ACCEPTED:    frozenset({RideStatus.ARRIVING,     RideStatus.CANCELLED}),
    RideStatus.ARRIVING:    frozenset({RideStatus.IN_PROGRESS,  RideStatus.CANCELLED}),
    RideStatus.IN_PROGRESS: frozenset({RideStatus.COMPLETED,    RideStatus.CANCELLED}),
    RideStatus.COMPLETED:   frozenset(),
    RideStatus.CANCELLED:   frozenset(),
}


# ---------------------------------------------------------------------------
# Stop entity
# ---------------------------------------------------------------------------

@dataclass
class Stop:
    """An ordered route point on a service request."""

    id: UUID
    service_request_id: UUID
    sequence_order: int
    stop_type: StopType
    latitude: float
    longitude: float

    place_name: str | None = None
    address_line_1: str | None = None
    address_line_2: str | None = None
    city: str | None = None
    state: str | None = None
    country: str | None = None
    postal_code: str | None = None

    contact_name: str | None = None
    contact_phone: str | None = None
    instructions: str | None = None

    arrived_at: datetime | None = None
    completed_at: datetime | None = None

    def mark_arrived(self) -> None:
        """Record driver arrival at this stop."""
        from .exceptions import StopAlreadyCompletedError
        if self.completed_at is not None:
            raise StopAlreadyCompletedError(
                f"Stop {self.id} is already completed — cannot mark arrived."
            )
        self.arrived_at = datetime.now(timezone.utc)

    def mark_completed(self) -> None:
        """Record stop completion after driver has arrived."""
        from .exceptions import StopAlreadyCompletedError, StopNotArrivedError
        if self.arrived_at is None:
            raise StopNotArrivedError(
                f"Stop {self.id} must be arrived at before completing."
            )
        if self.completed_at is not None:
            raise StopAlreadyCompletedError(f"Stop {self.id} is already completed.")
        self.completed_at = datetime.now(timezone.utc)

    @classmethod
    def create(
        cls,
        service_request_id: UUID,
        sequence_order: int,
        stop_type: StopType,
        latitude: float,
        longitude: float,
        **kwargs: object,
    ) -> Stop:
        return cls(
            id=uuid4(),
            service_request_id=service_request_id,
            sequence_order=sequence_order,
            stop_type=stop_type,
            latitude=latitude,
            longitude=longitude,
            **kwargs,  # type: ignore[arg-type]
        )


# ---------------------------------------------------------------------------
# Proof image metadata entity
# ---------------------------------------------------------------------------

@dataclass
class ProofImage:
    """
    Metadata for an uploaded proof-of-service image.

    Actual binary is stored in S3/object storage.  Only the key and
    metadata are persisted here.

    ORM fields:
        uploaded_by_user_id   — nullable FK → auth.users (passenger upload)
        uploaded_by_driver_id — nullable FK → verification.drivers (driver upload)
    Either may be set depending on who uploads; both may be null for
    system-generated proofs.
    """

    id: UUID
    service_request_id: UUID
    proof_type: ProofType
    file_key: str

    stop_id: UUID | None = None
    file_name: str | None = None
    mime_type: str | None = None
    file_size_bytes: int | None = None
    checksum_sha256: str | None = None
    is_primary: bool = False

    # Uploader identity — at most one should be set per record
    uploaded_by_user_id: UUID | None = None    # passenger
    uploaded_by_driver_id: UUID | None = None  # driver

    uploaded_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @classmethod
    def create(
        cls,
        service_request_id: UUID,
        proof_type: ProofType,
        file_key: str,
        uploaded_by_user_id: UUID | None = None,
        uploaded_by_driver_id: UUID | None = None,
        **kwargs: object,
    ) -> ProofImage:
        return cls(
            id=uuid4(),
            service_request_id=service_request_id,
            proof_type=proof_type,
            file_key=file_key,
            uploaded_by_user_id=uploaded_by_user_id,
            uploaded_by_driver_id=uploaded_by_driver_id,
            **kwargs,  # type: ignore[arg-type]
        )


# ---------------------------------------------------------------------------
# Verification code entity
# ---------------------------------------------------------------------------

@dataclass
class VerificationCode:
    """
    OTP code used for ride handoff verification at start or completion.

    ORM fields:
        verified_by_user_id   — UUID (bare, no FK) — passenger verifier
        verified_by_driver_id — UUID (bare, no FK) — driver verifier
    The code can be verified from either side depending on the flow.
    """

    id: UUID
    service_request_id: UUID
    code: str

    stop_id: UUID | None = None
    is_verified: bool = False
    attempts: int = 0
    max_attempts: int = 5
    expires_at: datetime | None = None
    generated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    verified_at: datetime | None = None

    # Either user or driver will verify — track both separately
    verified_by_user_id: UUID | None = None
    verified_by_driver_id: UUID | None = None

    @classmethod
    def generate(
        cls,
        service_request_id: UUID,
        stop_id: UUID | None = None,
        expires_at: datetime | None = None,
        length: int = 6,
        max_attempts: int = 5,
    ) -> VerificationCode:
        """Generate a cryptographically random zero-padded numeric code."""
        code = str(secrets.randbelow(10**length)).zfill(length)
        return cls(
            id=uuid4(),
            service_request_id=service_request_id,
            stop_id=stop_id,
            code=code,
            expires_at=expires_at,
            max_attempts=max_attempts,
        )

    def verify(
        self,
        submitted_code: str,
        *,
        user_id: UUID | None = None,
        driver_id: UUID | None = None,
    ) -> None:
        """
        Validate the submitted code.

        Pass exactly one of user_id or driver_id to record who verified.
        Raises domain exceptions for all failure modes.
        """
        from .exceptions import (
            RideDomainError,
            VerificationCodeAlreadyVerifiedError,
            VerificationCodeExhaustedError,
            VerificationCodeExpiredError,
            VerificationCodeInvalidError,
        )

        if not (bool(user_id) ^ bool(driver_id)):
            raise RideDomainError("Exactly one of user_id or driver_id must be provided to verify the code.")

        if self.is_verified:
            raise VerificationCodeAlreadyVerifiedError(
                f"Code {self.id} has already been verified."
            )
        if self.expires_at and datetime.now(timezone.utc) > self.expires_at:
            raise VerificationCodeExpiredError(
                f"Verification code {self.id} expired at {self.expires_at}."
            )
        if self.attempts >= self.max_attempts:
            raise VerificationCodeExhaustedError(
                f"Max attempts ({self.max_attempts}) exceeded for code {self.id}."
            )

        self.attempts += 1

        if not secrets.compare_digest(self.code, submitted_code):
            remaining = self.max_attempts - self.attempts
            raise VerificationCodeInvalidError(
                f"Invalid code. {remaining} attempt(s) remaining."
            )

        self.is_verified = True
        self.verified_at = datetime.now(timezone.utc)
        self.verified_by_user_id = user_id
        self.verified_by_driver_id = driver_id


# ---------------------------------------------------------------------------
# Driver matching result
# ---------------------------------------------------------------------------

@dataclass
class DriverCandidate:
    """A driver candidate returned from the geospatial / matching service."""

    driver_id: UUID
    distance_km: float
    vehicle_type: str
    rating: float | None = None
    priority_score: float = 0.0
    estimated_arrival_minutes: float | None = None


# ---------------------------------------------------------------------------
# ServiceRequest aggregate root
# ---------------------------------------------------------------------------

@dataclass
class ServiceRequest:
    """
    The aggregate root for a ride/service request lifecycle.

    Field mapping to ORM:
        passenger_id      → ServiceRequestORM.user_id           (NOT NULL, FK auth.users)
        assigned_driver_id → ServiceRequestORM.assigned_driver_id (nullable, FK verification.drivers)
    """

    id: UUID
    passenger_id: UUID           # maps to ORM.user_id
    service_type: ServiceType
    category: ServiceCategory
    pricing_mode: PricingMode
    status: RideStatus

    stops: list[Stop] = field(default_factory=list)
    proof_images: list[ProofImage] = field(default_factory=list)
    verification_codes: list[VerificationCode] = field(default_factory=list)

    assigned_driver_id: UUID | None = None   # maps to ORM.assigned_driver_id
    baseline_min_price: float | None = None
    baseline_max_price: float | None = None
    final_price: float | None = None

    scheduled_at: datetime | None = None
    is_scheduled: bool = False
    is_risky: bool = False
    auto_accept_driver: bool = True
    requires_otp_start: bool = False
    requires_otp_end: bool = False

    accepted_at: datetime | None = None
    completed_at: datetime | None = None
    cancelled_at: datetime | None = None
    cancellation_reason: str | None = None

    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    # ------------------------------------------------------------------
    # Lifecycle transitions
    # ------------------------------------------------------------------

    def transition_to(self, new_status: RideStatus) -> None:
        """Enforce the state machine. Raises InvalidStateTransitionError."""
        from .exceptions import InvalidStateTransitionError
        allowed = VALID_TRANSITIONS.get(self.status, frozenset())
        if new_status not in allowed:
            raise InvalidStateTransitionError(
                f"Ride {self.id}: cannot transition from "
                f"{self.status.value} → {new_status.value}. "
                f"Allowed: {[s.value for s in allowed] or 'none'}"
            )
        self.status = new_status

    def begin_matching(self) -> None:
        self.transition_to(RideStatus.MATCHING)

    def accept(self, driver_id: UUID) -> None:
        self.transition_to(RideStatus.ACCEPTED)
        self.assigned_driver_id = driver_id
        self.accepted_at = datetime.now(timezone.utc)

    def driver_arriving(self) -> None:
        self.transition_to(RideStatus.ARRIVING)

    def start(self) -> None:
        self.transition_to(RideStatus.IN_PROGRESS)

    def complete(self) -> None:
        self.transition_to(RideStatus.COMPLETED)
        self.completed_at = datetime.now(timezone.utc)

    def cancel(self, reason: str | None = None) -> None:
        self.transition_to(RideStatus.CANCELLED)
        self.cancelled_at = datetime.now(timezone.utc)
        self.cancellation_reason = reason

    # ------------------------------------------------------------------
    # Derived properties
    # ------------------------------------------------------------------

    @property
    def pickup_stop(self) -> Stop | None:
        return next(
            (s for s in self.stops if s.stop_type == StopType.PICKUP), None
        )

    @property
    def dropoff_stop(self) -> Stop | None:
        dropoffs = [s for s in self.stops if s.stop_type == StopType.DROPOFF]
        return max(dropoffs, key=lambda s: s.sequence_order) if dropoffs else None

    @property
    def is_active(self) -> bool:
        return self.status not in {RideStatus.COMPLETED, RideStatus.CANCELLED}

    # ------------------------------------------------------------------
    # Factory
    # ------------------------------------------------------------------

    @classmethod
    def create(
        cls,
        passenger_id: UUID,
        service_type: ServiceType,
        category: ServiceCategory,
        pricing_mode: PricingMode,
        baseline_min_price: float | None = None,
        baseline_max_price: float | None = None,
        scheduled_at: datetime | None = None,
        auto_accept_driver: bool = True,
    ) -> ServiceRequest:
        return cls(
            id=uuid4(),
            passenger_id=passenger_id,
            service_type=service_type,
            category=category,
            pricing_mode=pricing_mode,
            status=RideStatus.CREATED,
            baseline_min_price=baseline_min_price,
            baseline_max_price=baseline_max_price,
            scheduled_at=scheduled_at,
            is_scheduled=scheduled_at is not None,
            auto_accept_driver=auto_accept_driver,
        )
