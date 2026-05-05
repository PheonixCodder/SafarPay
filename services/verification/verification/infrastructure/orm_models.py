"""Verification ORM models — verification schema."""
from __future__ import annotations

import uuid
from datetime import date, datetime, timezone
from typing import Any

from sp.infrastructure.db.base import Base, TimestampMixin
from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PgUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..domain.models import DocumentType, EntityType, VehicleType, VerificationStatus


class DriverORM(Base, TimestampMixin):
    """Core driver profile linked to auth user."""
    __tablename__ = "drivers"
    __table_args__ = {"schema": "verification"}

    id: Mapped[uuid.UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    # Link to Auth User
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("auth.users.id", ondelete="CASCADE"), unique=True)

    verification_status: Mapped[VerificationStatus] = mapped_column(
        SQLEnum(VerificationStatus, name="verification_status", schema="verification"),
        default=VerificationStatus.PENDING
    )

    review_attempts: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    last_reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    stats: Mapped[DriverStatsORM] = relationship(back_populates="driver", cascade="all, delete-orphan")
    vehicles: Mapped[list[DriverVehicleORM]] = relationship(back_populates="driver")

    # Four Images with Doc Table: id_front, id_back, selfie_id, license_front, license_back


class VehicleORM(Base, TimestampMixin):
    """Vehicle details and verification status."""
    __tablename__ = "vehicles"
    __table_args__ = {"schema": "verification"}

    id: Mapped[uuid.UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    brand: Mapped[str] = mapped_column(String(50))
    model: Mapped[str] = mapped_column(String(50))
    year: Mapped[int] = mapped_column(Integer)
    color: Mapped[str] = mapped_column(String(30))
    plate_number: Mapped[str] = mapped_column(String(20), unique=True, index=True)
    max_passengers: Mapped[int] = mapped_column(Integer, default=4)
    vehicle_type: Mapped[VehicleType] = mapped_column(
        SQLEnum(VehicleType, name="vehicle_type", schema="verification"),
        default=VehicleType.ECONOMY
    )
    verification_status: Mapped[VerificationStatus] = mapped_column(
        SQLEnum(VerificationStatus, name="verification_status", schema="verification"),
        default=VerificationStatus.PENDING
    )

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    drivers: Mapped[list[DriverVehicleORM]] = relationship(back_populates="vehicle")

    # Three Images with Doc Table: registration_doc, vehicle_photo_front, vehicle_photo_back


class DocumentORM(Base, TimestampMixin):
    """Unified document storage for drivers and vehicles."""
    __tablename__ = "documents"
    __table_args__ = (
        Index("idx_doc_entity_type", "entity_id", "document_type"),
        {"schema": "verification"},
    )

    id: Mapped[uuid.UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_type: Mapped[DocumentType] = mapped_column(
        SQLEnum(DocumentType, name="document_type_enum", schema="verification")
    )
    file_key: Mapped[str] = mapped_column(String(500))  # S3 Key
    document_number: Mapped[str | None] = mapped_column(String(100))  # CNIC/License #
    expiry_date: Mapped[date | None] = mapped_column(Date)

    # Polymorphic-style link
    entity_id: Mapped[uuid.UUID] = mapped_column(PgUUID(as_uuid=True), index=True)
    entity_type: Mapped[EntityType] = mapped_column(
        SQLEnum(EntityType, name="entity_type", schema="verification")
    )
    verification_status: Mapped[VerificationStatus] = mapped_column(
        SQLEnum(VerificationStatus, name="verification_status", schema="verification"),
        default=VerificationStatus.PENDING
    )
    metadata_json: Mapped[dict[str, Any] | None] = mapped_column(JSONB)


class DriverVehicleORM(Base, TimestampMixin):
    """Junction table for drivers and their cars."""
    __tablename__ = "driver_vehicles"
    __table_args__ = (
        UniqueConstraint("driver_id", "vehicle_type", name="uq_driver_vehicle_type"),
        {"schema": "verification"}
    )

    id: Mapped[uuid.UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    driver_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("verification.drivers.id", ondelete="CASCADE"))
    vehicle_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("verification.vehicles.id", ondelete="CASCADE"))
    vehicle_type: Mapped[VehicleType] = mapped_column(
        SQLEnum(VehicleType, name="vehicle_type", schema="verification"),
        default=VehicleType.ECONOMY
    )
    is_currently_selected: Mapped[bool] = mapped_column(Boolean, default=False)
    assigned_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc))

    driver: Mapped[DriverORM] = relationship(back_populates="vehicles")
    vehicle: Mapped[VehicleORM] = relationship(back_populates="drivers")


class VerificationRejectionORM(Base, TimestampMixin):
    """History of verification failures."""
    __tablename__ = "verification_rejections"
    __table_args__ = {"schema": "verification"}

    id: Mapped[uuid.UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    driver_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("verification.drivers.id"), index=True)
    document_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("verification.documents.id"), index=True)

    rejection_reason_code: Mapped[str] = mapped_column(String(50))  # e.g., DOC_BLURRY
    admin_comment: Mapped[str | None] = mapped_column(Text)
    is_resolved: Mapped[bool] = mapped_column(Boolean, default=False)
    rejected_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc))


class DriverStatsORM(Base):
    """Performance metrics for drivers."""
    __tablename__ = "driver_stats"
    __table_args__ = {"schema": "verification"}

    driver_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("verification.drivers.id", ondelete="CASCADE"), primary_key=True
    )
    rating_avg: Mapped[float] = mapped_column(Numeric(3, 2), default=0.0)
    total_rides: Mapped[int] = mapped_column(Integer, default=0)
    acceptance_rate: Mapped[float] = mapped_column(Numeric(5, 2), default=0.0)
    cancellation_rate: Mapped[float] = mapped_column(Numeric(5, 2), default=0.0)
    driver: Mapped[DriverORM] = relationship(back_populates="stats")


class VerificationOutboxEventORM(Base, TimestampMixin):
    __tablename__ = "outbox_events"
    __table_args__ = (
        Index("ix_verification_outbox_pending", "processed_at", "created_at"),
        {"schema": "verification"},
    )

    id: Mapped[uuid.UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    event_type: Mapped[str] = mapped_column(String(160), nullable=False, index=True)
    aggregate_id: Mapped[str | None] = mapped_column(String(120), index=True)
    aggregate_type: Mapped[str | None] = mapped_column(String(80))
    topic: Mapped[str] = mapped_column(String(160), nullable=False, default="verification.events")
    payload: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    correlation_id: Mapped[str | None] = mapped_column(String(120))
    idempotency_key: Mapped[str | None] = mapped_column(String(180), unique=True)
    processed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    error_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    last_error: Mapped[str | None] = mapped_column(Text)


class VerificationInboxMessageORM(Base, TimestampMixin):
    __tablename__ = "inbox_messages"
    __table_args__ = (
        Index("ix_verification_inbox_source_offset", "source_topic", "source_partition", "source_offset", unique=True),
        Index("ix_verification_inbox_pending", "processed_at", "received_at"),
        {"schema": "verification"},
    )

    event_id: Mapped[uuid.UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True)
    event_type: Mapped[str] = mapped_column(String(160), nullable=False, index=True)
    source_topic: Mapped[str] = mapped_column(String(160), nullable=False)
    source_partition: Mapped[int | None] = mapped_column(Integer)
    source_offset: Mapped[int | None] = mapped_column(Integer)
    aggregate_id: Mapped[str | None] = mapped_column(String(120), index=True)
    payload: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    received_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    processed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    error_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    last_error: Mapped[str | None] = mapped_column(Text)
