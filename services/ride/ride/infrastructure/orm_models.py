from __future__ import annotations

import enum
import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    Enum as SQLEnum,
    func,
)
from sqlalchemy.dialects.postgresql import UUID as PgUUID, ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship

from sp.infrastructure.db.base import Base, TimestampMixin


# =========================
# ENUMS
# =========================


class ServiceType(enum.Enum):
    CITY_RIDE = "CITY_RIDE"
    INTERCITY = "INTERCITY"
    FREIGHT = "FREIGHT"
    COURIER = "COURIER"
    GROCERY = "GROCERY"


class ServiceCategory(enum.Enum):
    MINI = "MINI"
    RICKSHAW = "RICKSHAW"
    RIDE_AC = "RIDE_AC"
    PREMIUM = "PREMIUM"
    BIKE = "BIKE"
    COMFORT = "COMFORT"
    SHARE = "SHARE"
    PRIVATE = "PRIVATE"


class PricingMode(enum.Enum):
    FIXED = "FIXED"
    BID_BASED = "BID_BASED"
    HYBRID = "HYBRID"


class RequestStatus(enum.Enum):
    CREATED = "CREATED"
    BIDDING = "BIDDING"
    MATCHING = "MATCHING"
    ACCEPTED = "ACCEPTED"
    ARRIVING = "ARRIVING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


class StopType(enum.Enum):
    PICKUP = "PICKUP"
    DROPOFF = "DROPOFF"
    WAYPOINT = "WAYPOINT"


class ProofType(enum.Enum):
    PICKUP = "PICKUP"
    DROPOFF = "DROPOFF"


class VehicleType(enum.Enum):
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


class DriverGenderPreference(enum.Enum):
    NO_PREFERENCE = "NO_PREFERENCE"
    MALE = "MALE"
    FEMALE = "FEMALE"
    ANY = "ANY"

class FuelType(enum.Enum):
    PETROL = "PETROL"
    DIESEL = "DIESEL"
    CNG = "CNG"
    HYBRID = "HYBRID"
    ELECTRIC = "ELECTRIC"


# =========================
# CORE TABLE
# =========================


class ServiceRequestORM(Base, TimestampMixin):
    __tablename__ = "service_requests"

    id: Mapped[uuid.UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # PASSENGER ONLY (source of truth)
    user_id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True),
        ForeignKey("auth.users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    assigned_driver_id: Mapped[uuid.UUID | None] = mapped_column(
        PgUUID(as_uuid=True),
        ForeignKey("verification.drivers.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )


    service_type: Mapped[ServiceType] = mapped_column(
        SQLEnum(ServiceType, name="service_type_enum", schema="service_request"),
        nullable=False,
        index=True,
    )
    category: Mapped[ServiceCategory] = mapped_column(
        SQLEnum(ServiceCategory, name="service_category_enum", schema="service_request"),
        nullable=False,
    )
    pricing_mode: Mapped[PricingMode] = mapped_column(
        SQLEnum(PricingMode, name="pricing_mode_enum", schema="service_request"),
        nullable=False,
    )

    status: Mapped[RequestStatus] = mapped_column(
        SQLEnum(RequestStatus, name="request_status_enum", schema="service_request"),
        default=RequestStatus.CREATED,
        nullable=False,
        index=True,
    )

    scheduled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Pricing guardrails.
    baseline_min_price: Mapped[float | None] = mapped_column(Numeric(12, 2), nullable=True)
    baseline_max_price: Mapped[float | None] = mapped_column(Numeric(12, 2), nullable=True)
    auto_accept_driver: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    final_price: Mapped[float | None] = mapped_column(Numeric(12, 2), nullable=True)

    accepted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    cancelled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    cancellation_reason: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Customer / operational flags.
    is_scheduled: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_risky: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    stops: Mapped[list["ServiceStopORM"]] = relationship(
        back_populates="service_request",
        cascade="all, delete-orphan",
        order_by="ServiceStopORM.sequence_order",
    )

    proof_images: Mapped[list["ServiceProofImageORM"]] = relationship(
        back_populates="service_request",
        cascade="all, delete-orphan",
    )

    verification_codes: Mapped[list["ServiceVerificationCodeORM"]] = relationship(
        back_populates="service_request",
        cascade="all, delete-orphan",
    )

    city_ride: Mapped["CityRideDetailORM | None"] = relationship(back_populates="service_request", uselist=False)
    intercity: Mapped["IntercityDetailORM | None"] = relationship(back_populates="service_request", uselist=False)
    freight: Mapped["FreightDetailORM | None"] = relationship(back_populates="service_request", uselist=False)
    courier: Mapped["CourierDetailORM | None"] = relationship(back_populates="service_request", uselist=False)
    grocery: Mapped["GroceryDetailORM | None"] = relationship(back_populates="service_request", uselist=False)

    __table_args__ = (
        CheckConstraint("baseline_min_price IS NULL OR baseline_min_price >= 0", name="ck_service_requests_baseline_min_price_non_negative"),
        CheckConstraint("baseline_max_price IS NULL OR baseline_max_price >= 0", name="ck_service_requests_baseline_max_price_non_negative"),
        CheckConstraint("final_price IS NULL OR final_price >= 0", name="ck_service_requests_final_price_non_negative"),
        CheckConstraint(
            "baseline_min_price IS NULL OR baseline_max_price IS NULL OR baseline_min_price <= baseline_max_price",
            name="ck_service_requests_baseline_price_range",
        ),
        Index("ix_service_requests_user_id_status", "user_id", "status"),
        Index("ix_service_requests_service_type_status", "service_type", "status"),
        {"schema": "service_request"},
    )


# =========================
# STOPS
# =========================


class ServiceStopORM(Base, TimestampMixin):
    __tablename__ = "service_stops"

    id: Mapped[uuid.UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    service_request_id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True),
        ForeignKey("service_request.service_requests.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    sequence_order: Mapped[int] = mapped_column(Integer, nullable=False)
    stop_type: Mapped[StopType] = mapped_column(
        SQLEnum(StopType, name="stop_type_enum", schema="service_request"),
        nullable=False,
    )

    latitude: Mapped[float] = mapped_column(Numeric(10, 7), nullable=False)
    longitude: Mapped[float] = mapped_column(Numeric(10, 7), nullable=False)

    place_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    address_line_1: Mapped[str | None] = mapped_column(String(255), nullable=True)
    address_line_2: Mapped[str | None] = mapped_column(String(255), nullable=True)
    city: Mapped[str | None] = mapped_column(String(120), nullable=True)
    state: Mapped[str | None] = mapped_column(String(120), nullable=True)
    country: Mapped[str | None] = mapped_column(String(120), nullable=True)
    postal_code: Mapped[str | None] = mapped_column(String(30), nullable=True)

    contact_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    contact_phone: Mapped[str | None] = mapped_column(String(30), nullable=True)
    instructions: Mapped[str | None] = mapped_column(Text, nullable=True)

    arrived_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    service_request: Mapped["ServiceRequestORM"] = relationship(back_populates="stops")
    proof_images: Mapped[list["ServiceProofImageORM"]] = relationship(back_populates="stop")
    verification_codes: Mapped[list["ServiceVerificationCodeORM"]] = relationship(back_populates="stop")

    __table_args__ = (
        CheckConstraint("sequence_order > 0", name="ck_service_stops_sequence_order_positive"),
        CheckConstraint("latitude BETWEEN -90 AND 90", name="ck_service_stops_latitude_range"),
        CheckConstraint("longitude BETWEEN -180 AND 180", name="ck_service_stops_longitude_range"),
        Index("ix_service_stops_request_order", "service_request_id", "sequence_order", unique=True),
        Index("ix_service_stops_request_type", "service_request_id", "stop_type"),
        {"schema": "service_request"},
    )


# =========================
# SERVICE TYPE DETAIL TABLES
# =========================


class FreightDetailORM(Base, TimestampMixin):
    __tablename__ = "freight_details"
    __table_args__ = (
        CheckConstraint("cargo_weight > 0", name="ck_freight_details_cargo_weight_positive"),
        CheckConstraint("estimated_load_hours IS NULL OR estimated_load_hours >= 0", name="ck_freight_details_estimated_load_hours_non_negative"),
        {"schema": "service_request"},
    )

    service_request_id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True),
        ForeignKey("service_request.service_requests.id", ondelete="CASCADE"),
        primary_key=True,
    )

    cargo_weight: Mapped[float] = mapped_column(Numeric(12, 3), nullable=False)
    cargo_type: Mapped[str] = mapped_column(String(120), nullable=False)
    requires_loader: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    vehicle_type: Mapped[VehicleType] = mapped_column(
        SQLEnum(VehicleType, name="freight_vehicle_type_enum", schema="service_request"),
        nullable=False,
    )

    is_fragile: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    requires_temperature_control: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    declared_value: Mapped[float | None] = mapped_column(Numeric(12, 2), nullable=True)
    commodity_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    estimated_load_hours: Mapped[int | None] = mapped_column(Integer, nullable=True)

    service_request: Mapped["ServiceRequestORM"] = relationship(back_populates="freight")


class CourierDetailORM(Base, TimestampMixin):
    __tablename__ = "courier_details"
    __table_args__ = (
        CheckConstraint("item_weight IS NULL OR item_weight > 0", name="ck_courier_details_item_weight_positive"),
        CheckConstraint("total_parcels > 0", name="ck_courier_details_total_parcels_positive"),
        {"schema": "service_request"},
    )

    service_request_id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True),
        ForeignKey("service_request.service_requests.id", ondelete="CASCADE"),
        primary_key=True,
    )

    item_description: Mapped[str] = mapped_column(Text, nullable=False)
    item_weight: Mapped[float | None] = mapped_column(Numeric(12, 3), nullable=True)
    total_parcels: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    recipient_name: Mapped[str] = mapped_column(String(255), nullable=False)
    recipient_phone: Mapped[str] = mapped_column(String(30), nullable=False)
    recipient_email: Mapped[str | None] = mapped_column(String(255), nullable=True)

    is_fragile: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    requires_signature: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    declared_value: Mapped[float | None] = mapped_column(Numeric(12, 2), nullable=True)
    special_handling_notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    service_request: Mapped["ServiceRequestORM"] = relationship(back_populates="courier")


class CityRideDetailORM(Base, TimestampMixin):
    __tablename__ = "city_ride_details"
    __table_args__ = (
        CheckConstraint("passenger_count > 0", name="ck_city_ride_details_passenger_count_positive"),
        CheckConstraint("max_wait_time_minutes IS NULL OR max_wait_time_minutes >= 0", name="ck_city_ride_details_max_wait_non_negative"),
        {"schema": "service_request"},
    )

    service_request_id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True),
        ForeignKey("service_request.service_requests.id", ondelete="CASCADE"),
        primary_key=True,
    )

    passenger_count: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    is_ac: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    preferred_vehicle_type: Mapped[VehicleType | None] = mapped_column(
        SQLEnum(VehicleType, name="city_ride_vehicle_type_enum", schema="service_request"),
        nullable=True,
    )
    driver_gender_preference: Mapped[DriverGenderPreference] = mapped_column(
        SQLEnum(DriverGenderPreference, name="driver_gender_preference_enum", schema="service_request"),
        default=DriverGenderPreference.NO_PREFERENCE,
        nullable=False,
    )

    is_shared_ride: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    max_co_passengers: Mapped[int | None] = mapped_column(Integer, nullable=True)
    allowed_fuel_types: Mapped[list[FuelType]] = mapped_column(
        ARRAY(SQLEnum(FuelType, name="fuel_type_enum", schema="service_request", create_type=True)),
        nullable=True,
    )
    is_smoking_allowed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_pet_allowed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    requires_wheelchair_access: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    max_wait_time_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    requires_otp_start: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    requires_otp_end: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    estimated_price: Mapped[float | None] = mapped_column(Numeric(12, 2), nullable=True)
    surge_multiplier_applied: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)

    service_request: Mapped["ServiceRequestORM"] = relationship(back_populates="city_ride")


class IntercityDetailORM(Base, TimestampMixin):
    __tablename__ = "intercity_details"
    __table_args__ = (
        CheckConstraint("passenger_count > 0", name="ck_intercity_details_passenger_count_positive"),
        CheckConstraint("luggage_count >= 0", name="ck_intercity_details_luggage_count_non_negative"),
        CheckConstraint("trip_distance_km IS NULL OR trip_distance_km >= 0", name="ck_intercity_details_distance_non_negative"),
        CheckConstraint("estimated_duration_minutes IS NULL OR estimated_duration_minutes >= 0", name="ck_intercity_details_duration_non_negative"),
        CheckConstraint("departure_time_flexibility_minutes IS NULL OR departure_time_flexibility_minutes >= 0", name="ck_intercity_details_departure_flex_non_negative"),
        {"schema": "service_request"},
    )

    service_request_id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True),
        ForeignKey("service_request.service_requests.id", ondelete="CASCADE"),
        primary_key=True,
    )

    passenger_count: Mapped[int] = mapped_column(Integer, nullable=False)
    luggage_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    child_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    senior_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    allowed_fuel_types: Mapped[list[FuelType]] = mapped_column(
        ARRAY(SQLEnum(FuelType, name="fuel_type_enum", schema="service_request", create_type=False)),
        nullable=True,
    )
    preferred_departure_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    departure_time_flexibility_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    is_round_trip: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    return_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    trip_distance_km: Mapped[float | None] = mapped_column(Numeric(12, 3), nullable=True)
    estimated_duration_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    route_polyline: Mapped[str | None] = mapped_column(Text, nullable=True)

    vehicle_type_requested: Mapped[VehicleType | None] = mapped_column(
        SQLEnum(VehicleType, name="intercity_vehicle_type_enum", schema="service_request"),
        nullable=True,
    )
    min_vehicle_capacity: Mapped[int | None] = mapped_column(Integer, nullable=True)
    requires_luggage_carrier: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    estimated_price: Mapped[float | None] = mapped_column(Numeric(12, 2), nullable=True)
    price_per_km: Mapped[float | None] = mapped_column(Numeric(12, 2), nullable=True)
    toll_estimate: Mapped[float | None] = mapped_column(Numeric(12, 2), nullable=True)
    fuel_surcharge: Mapped[float | None] = mapped_column(Numeric(12, 2), nullable=True)

    # Note: total_stops is an operational cache; source of truth is ServiceStopORM count.
    total_stops: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_multi_city_trip: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    requires_identity_verification: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    emergency_contact_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    emergency_contact_number: Mapped[str | None] = mapped_column(String(30), nullable=True)

    matching_priority_score: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)
    demand_zone_id: Mapped[str | None] = mapped_column(String(120), nullable=True)

    service_request: Mapped["ServiceRequestORM"] = relationship(back_populates="intercity")
    passenger_groups: Mapped[list["IntercityPassengerGroupORM"]] = relationship(
        back_populates="intercity_detail",
        cascade="all, delete-orphan",
    )


class IntercityPassengerGroupORM(Base, TimestampMixin):
    __tablename__ = "intercity_passenger_groups"
    __table_args__ = (
        CheckConstraint("passenger_count > 0", name="ck_intercity_passenger_groups_passenger_count_positive"),
        CheckConstraint("luggage_count >= 0", name="ck_intercity_passenger_groups_luggage_count_non_negative"),
        Index("ix_intercity_passenger_groups_request", "intercity_service_request_id"),
        {"schema": "service_request"},
    )

    id: Mapped[uuid.UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    intercity_service_request_id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True),
        ForeignKey("service_request.intercity_details.service_request_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    passenger_count: Mapped[int] = mapped_column(Integer, nullable=False)
    luggage_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    full_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    phone_number: Mapped[str | None] = mapped_column(String(30), nullable=True)
    seat_preference: Mapped[str | None] = mapped_column(String(80), nullable=True)
    special_needs: Mapped[str | None] = mapped_column(Text, nullable=True)

    intercity_detail: Mapped["IntercityDetailORM"] = relationship(back_populates="passenger_groups")


class GroceryDetailORM(Base, TimestampMixin):
    __tablename__ = "grocery_details"
    __table_args__ = (
        CheckConstraint("total_items >= 0", name="ck_grocery_details_total_items_non_negative"),
        {"schema": "service_request"},
    )

    service_request_id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True),
        ForeignKey("service_request.service_requests.id", ondelete="CASCADE"),
        primary_key=True,
    )

    store_id: Mapped[uuid.UUID] = mapped_column(PgUUID(as_uuid=True), nullable=False, index=True)
    total_items: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    special_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    contactless_delivery: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    estimated_bag_count: Mapped[int | None] = mapped_column(Integer, nullable=True)

    service_request: Mapped["ServiceRequestORM"] = relationship(back_populates="grocery")


# =========================
# PROOF / VERIFICATION / SECURITY
# =========================


class ServiceProofImageORM(Base, TimestampMixin):
    __tablename__ = "service_proof_images"
    __table_args__ = (
        Index("ix_service_proof_images_request_stop_type", "service_request_id", "stop_id", "proof_type"),
        CheckConstraint(
            "(uploaded_by_user_id IS NOT NULL) OR (uploaded_by_driver_id IS NOT NULL)",
            name="ck_service_proof_images_uploader_exists"
        ),
        {"schema": "service_request"},
    )

    id: Mapped[uuid.UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    service_request_id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True),
        ForeignKey("service_request.service_requests.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    stop_id: Mapped[uuid.UUID | None] = mapped_column(
        PgUUID(as_uuid=True),
        ForeignKey("service_request.service_stops.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )

    proof_type: Mapped[ProofType] = mapped_column(
        SQLEnum(ProofType, name="proof_type_enum", schema="service_request"),
        nullable=False,
    )

    file_key: Mapped[str] = mapped_column(String(500), nullable=False)
    file_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    mime_type: Mapped[str | None] = mapped_column(String(120), nullable=True)
    file_size_bytes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    checksum_sha256: Mapped[str | None] = mapped_column(String(64), nullable=True)
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    uploaded_by_user_id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True),
        ForeignKey("auth.users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    uploaded_by_driver_id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True),
        ForeignKey("verification.drivers.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    uploaded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    service_request: Mapped["ServiceRequestORM"] = relationship(back_populates="proof_images")
    stop: Mapped["ServiceStopORM | None"] = relationship(back_populates="proof_images")


class ServiceVerificationCodeORM(Base, TimestampMixin):
    __tablename__ = "service_verification_codes"
    __table_args__ = (
        Index("ix_service_verification_codes_request_stop", "service_request_id", "stop_id"),
        Index("ix_service_verification_codes_request_verified", "service_request_id", "is_verified"),
        {"schema": "service_request"},
    )

    id: Mapped[uuid.UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    service_request_id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True),
        ForeignKey("service_request.service_requests.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    stop_id: Mapped[uuid.UUID | None] = mapped_column(
        PgUUID(as_uuid=True),
        ForeignKey("service_request.service_stops.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )

    code: Mapped[str] = mapped_column(String(10), nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    attempts: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    max_attempts: Mapped[int] = mapped_column(Integer, default=5, nullable=False)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    generated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    verified_by_user_id: Mapped[uuid.UUID | None] = mapped_column(
        PgUUID(as_uuid=True),
        ForeignKey("auth.users.id", ondelete="SET NULL"),
        nullable=True
    )
    verified_by_driver_id: Mapped[uuid.UUID | None] = mapped_column(
        PgUUID(as_uuid=True),
        ForeignKey("verification.drivers.id", ondelete="SET NULL"),
        nullable=True
    )

    service_request: Mapped["ServiceRequestORM"] = relationship(back_populates="verification_codes")
    stop: Mapped["ServiceStopORM | None"] = relationship(back_populates="verification_codes")
