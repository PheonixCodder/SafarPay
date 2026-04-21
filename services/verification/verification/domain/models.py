"""Verification domain models — pure Python."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from uuid import UUID, uuid4


class DocumentType(str, Enum):
    NATIONAL_ID = "national_id"
    DRIVERS_LICENSE = "drivers_license"
    PASSPORT = "passport"
    VEHICLE_REGISTRATION = "vehicle_registration"


class DocumentStatus(str, Enum):
    PENDING = "pending"
    UNDER_REVIEW = "under_review"
    VERIFIED = "verified"
    REJECTED = "rejected"


@dataclass
class Document:
    id: UUID
    user_id: UUID
    doc_type: DocumentType
    status: DocumentStatus
    file_url: str
    submitted_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    verified_at: datetime | None = None
    rejection_reason: str | None = None

    @classmethod
    def create(cls, user_id: UUID, doc_type: DocumentType, file_url: str) -> Document:
        return cls(
            id=uuid4(),
            user_id=user_id,
            doc_type=doc_type,
            status=DocumentStatus.PENDING,
            file_url=file_url,
        )
