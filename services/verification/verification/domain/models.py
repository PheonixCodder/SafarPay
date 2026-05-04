"""Verification domain models."""
from __future__ import annotations

import uuid
from datetime import datetime, date, timezone
from dataclasses import dataclass, field
from enum import Enum


class VerificationStatus(str, Enum):
    PENDING = "pending"
    UNDER_REVIEW = "under_review"
    VERIFIED = "verified"
    REJECTED = "rejected"
    SUSPENDED = "suspended"


class VehicleType(str, Enum):
    MOTO = "moto"
    ECONOMY = "economy"
    COMFORT = "comfort"
    FREIGHT = "freight"


class EntityType(str, Enum):
    DRIVER = "driver"
    VEHICLE = "vehicle"


class DocumentType(str, Enum):
    ID_FRONT = "id_front"
    ID_BACK = "id_back"
    SELFIE_ID = "selfie_id"
    LICENSE_FRONT = "license_front"
    LICENSE_BACK = "license_back"
    REGISTRATION_DOC_FRONT = "registration_doc_front"
    REGISTRATION_DOC_BACK = "registration_doc_back"
    VEHICLE_PHOTO_FRONT = "vehicle_photo_front"
    VEHICLE_PHOTO_BACK = "vehicle_photo_back"


@dataclass
class Driver:
    id: uuid.UUID
    user_id: uuid.UUID
    verification_status: VerificationStatus = VerificationStatus.PENDING
    review_attempts: int = 0
    last_reviewed_at: datetime | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


@dataclass
class Vehicle:
    id: uuid.UUID
    brand: str
    model: str
    year: int
    color: str
    plate_number: str
    max_passengers: int = 4
    vehicle_type: VehicleType = VehicleType.ECONOMY
    verification_status: VerificationStatus = VerificationStatus.PENDING
    is_active: bool = True
    created_at: datetime | None = None
    updated_at: datetime | None = None


@dataclass
class Document:
    id: uuid.UUID
    document_type: DocumentType
    file_key: str
    entity_id: uuid.UUID
    entity_type: EntityType
    document_number: str | None = None
    expiry_date: date | None = None
    verification_status: VerificationStatus = VerificationStatus.PENDING
    metadata_json: dict | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


@dataclass
class DriverVehicle:
    id: uuid.UUID
    driver_id: uuid.UUID
    vehicle_id: uuid.UUID
    vehicle_type: VehicleType = VehicleType.ECONOMY
    is_currently_selected: bool = False
    assigned_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    created_at: datetime | None = None
    updated_at: datetime | None = None


@dataclass
class VerificationRejection:
    id: uuid.UUID
    driver_id: uuid.UUID
    rejection_reason_code: str
    document_id: uuid.UUID | None = None
    admin_comment: str | None = None
    is_resolved: bool = False
    rejected_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    created_at: datetime | None = None
    updated_at: datetime | None = None


@dataclass
class DriverStats:
    driver_id: uuid.UUID
    rating_avg: float = 0.0
    total_rides: int = 0
    acceptance_rate: float = 0.0
    cancellation_rate: float = 0.0
    online_minutes_today: int = 0
