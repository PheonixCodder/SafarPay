"""Ride service Pydantic schemas — API DTOs and command objects.

All schemas use Pydantic v2. Input schemas validate incoming API payloads.
Response schemas serialise domain objects for API consumers.

Service-type detail inputs use a Literal discriminator on `service_type`
so FastAPI can produce a clean OpenAPI schema and validate the union correctly.
"""
from __future__ import annotations

from datetime import datetime
from typing import Annotated, Literal
from uuid import UUID

from pydantic import BaseModel, Field, model_validator

from ..domain.models import (
    DriverGenderPreference,
    FuelType,
    PricingMode,
    ProofType,
    RideStatus,
    ServiceCategory,
    ServiceType,
    StopType,
    VehicleType,
)

# ============================================================
# Stop schemas
# ============================================================

class StopInput(BaseModel):
    sequence_order: int = Field(..., ge=1, description="1-based position in the route")
    stop_type: StopType
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    place_name: str | None = Field(None, max_length=255)
    address_line_1: str | None = Field(None, max_length=255)
    address_line_2: str | None = Field(None, max_length=255)
    city: str | None = Field(None, max_length=120)
    state: str | None = Field(None, max_length=120)
    country: str | None = Field(None, max_length=120)
    postal_code: str | None = Field(None, max_length=30)
    contact_name: str | None = Field(None, max_length=255)
    contact_phone: str | None = Field(None, max_length=30)
    instructions: str | None = None


class StopResponse(BaseModel):
    id: UUID
    service_request_id: UUID
    sequence_order: int
    stop_type: StopType
    latitude: float
    longitude: float
    place_name: str | None
    address_line_1: str | None
    address_line_2: str | None
    city: str | None
    state: str | None
    country: str | None
    postal_code: str | None
    contact_name: str | None
    contact_phone: str | None
    instructions: str | None
    arrived_at: datetime | None
    completed_at: datetime | None


# ============================================================
# Proof image schemas
# ============================================================

class UploadProofRequest(BaseModel):
    proof_type: ProofType
    file_key: str = Field(..., max_length=500, description="S3 / object-storage key returned by the upload-url endpoint")
    file_name: str | None = Field(None, max_length=255)
    mime_type: str | None = Field(None, max_length=120)
    file_size_bytes: int | None = Field(None, ge=0)
    checksum_sha256: str | None = Field(None, max_length=64)
    is_primary: bool = False
    stop_id: UUID | None = None
    # NOTE: uploaded_by_user_id / uploaded_by_driver_id are intentionally absent.
    # The server derives the uploader identity from the authenticated JWT principal
    # to prevent identity spoofing; clients must not supply these fields.


class ProofImageResponse(BaseModel):
    id: UUID
    service_request_id: UUID
    stop_id: UUID | None
    proof_type: ProofType
    file_key: str
    file_name: str | None
    mime_type: str | None
    file_size_bytes: int | None
    is_primary: bool
    uploaded_by_user_id: UUID | None
    uploaded_by_driver_id: UUID | None
    uploaded_at: datetime


# ── Presigned URL schemas ────────────────────────────────────────────────────

class ProofUploadUrlRequest(BaseModel):
    """
    Request a presigned S3 PUT URL before uploading a proof image.

    Flow:
      1.  POST /rides/{id}/proofs/upload-url  → receives presigned_url + file_key
      2.  PUT  <presigned_url>                → client uploads binary to S3
      3.  POST /rides/{id}/proofs             → client registers metadata with file_key
    """
    proof_type: ProofType
    file_name: str | None = Field(None, max_length=255, description="Original filename; used to derive the S3 key extension")
    mime_type: str = Field(
        default="image/jpeg",
        description="MIME type the client will upload with. Must match Content-Type in the PUT request.",
    )
    stop_id: UUID | None = Field(None, description="Associate the proof with a specific stop")


class ProofUploadUrlResponse(BaseModel):
    """Presigned PUT URL + the S3 key the client must use when registering the proof."""
    presigned_url: str = Field(..., description="HTTPS PUT URL valid for 15 minutes")
    file_key: str = Field(..., description="S3 object key — pass this to POST /proofs as file_key")
    expires_in_seconds: int = 900
    proof_type: ProofType
    mime_type: str


class ProofImageWithUrlResponse(ProofImageResponse):
    """ProofImageResponse enriched with a time-limited presigned GET URL for display."""
    view_url: str = Field(..., description="Presigned GET URL valid for 1 hour")


# ============================================================
# Verification code schemas
# ============================================================

class GenerateVerificationCodeRequest(BaseModel):
    stop_id: UUID | None = None
    expires_in_minutes: int = Field(default=15, ge=1, le=60)
    max_attempts: int = Field(default=5, ge=1, le=10)
    length: int = Field(default=6, ge=4, le=8)


class VerifyCodeRequest(BaseModel):
    code: str = Field(..., min_length=4, max_length=10)
    # Pass exactly one verifier ID
    user_id: UUID | None = None
    driver_id: UUID | None = None

    @model_validator(mode="after")
    def require_one_verifier(self) -> VerifyCodeRequest:
        if self.user_id is None and self.driver_id is None:
            raise ValueError("Provide either user_id or driver_id as the verifier.")
        if self.user_id and self.driver_id:
            raise ValueError("Provide only one of user_id or driver_id, not both.")
        return self


class VerificationCodeResponse(BaseModel):
    id: UUID
    service_request_id: UUID
    stop_id: UUID | None
    is_verified: bool
    attempts: int
    max_attempts: int
    expires_at: datetime | None
    generated_at: datetime
    verified_at: datetime | None


# ============================================================
# Service-type detail input schemas (discriminated union)
# ============================================================

class PassengerGroupInput(BaseModel):
    passenger_count: int = Field(..., ge=1)
    luggage_count: int = Field(0, ge=0)
    full_name: str | None = Field(None, max_length=255)
    phone_number: str | None = Field(None, max_length=30)
    seat_preference: str | None = Field(None, max_length=80)
    special_needs: str | None = None


class CityRideDetailInput(BaseModel):
    service_type: Literal[ServiceType.CITY_RIDE] = ServiceType.CITY_RIDE
    passenger_count: int = Field(1, ge=1)
    is_ac: bool = False
    preferred_vehicle_type: VehicleType | None = None
    driver_gender_preference: DriverGenderPreference = DriverGenderPreference.NO_PREFERENCE
    is_shared_ride: bool = False
    max_co_passengers: int | None = None
    allowed_fuel_types: list[FuelType] = Field(default_factory=list)
    is_smoking_allowed: bool = False
    is_pet_allowed: bool = False
    requires_wheelchair_access: bool = False
    max_wait_time_minutes: int | None = Field(None, ge=0)
    requires_otp_start: bool = True
    requires_otp_end: bool = True
    estimated_price: float | None = Field(None, ge=0)
    surge_multiplier_applied: float | None = Field(None, ge=1)


class IntercityDetailInput(BaseModel):
    service_type: Literal[ServiceType.INTERCITY] = ServiceType.INTERCITY
    passenger_count: int = Field(..., ge=1)
    luggage_count: int = Field(0, ge=0)
    child_count: int = Field(0, ge=0)
    senior_count: int = Field(0, ge=0)
    allowed_fuel_types: list[FuelType] = Field(default_factory=list)
    preferred_departure_time: datetime | None = None
    departure_time_flexibility_minutes: int | None = Field(None, ge=0)
    is_round_trip: bool = False
    return_time: datetime | None = None
    trip_distance_km: float | None = Field(None, ge=0)
    estimated_duration_minutes: int | None = Field(None, ge=0)
    route_polyline: str | None = None
    vehicle_type_requested: VehicleType | None = None
    min_vehicle_capacity: int | None = None
    requires_luggage_carrier: bool = False
    estimated_price: float | None = Field(None, ge=0)
    price_per_km: float | None = Field(None, ge=0)
    toll_estimate: float | None = Field(None, ge=0)
    fuel_surcharge: float | None = Field(None, ge=0)
    total_stops: int = Field(0, ge=0)
    is_multi_city_trip: bool = False
    requires_identity_verification: bool = False
    emergency_contact_name: str | None = Field(None, max_length=255)
    emergency_contact_number: str | None = Field(None, max_length=30)
    matching_priority_score: float | None = None
    demand_zone_id: str | None = Field(None, max_length=120)
    passenger_groups: list[PassengerGroupInput] = Field(default_factory=list)


class FreightDetailInput(BaseModel):
    service_type: Literal[ServiceType.FREIGHT] = ServiceType.FREIGHT
    cargo_weight: float = Field(..., gt=0)
    cargo_type: str = Field(..., max_length=120)
    requires_loader: bool = False
    vehicle_type: VehicleType
    is_fragile: bool = False
    requires_temperature_control: bool = False
    declared_value: float | None = Field(None, ge=0)
    commodity_notes: str | None = None
    estimated_load_hours: int | None = Field(None, ge=0)


class CourierDetailInput(BaseModel):
    service_type: Literal[ServiceType.COURIER] = ServiceType.COURIER
    item_description: str
    item_weight: float | None = Field(None, gt=0)
    total_parcels: int = Field(1, ge=1)
    recipient_name: str = Field(..., max_length=255)
    recipient_phone: str = Field(..., max_length=30)
    recipient_email: str | None = Field(None, max_length=255)
    is_fragile: bool = False
    requires_signature: bool = False
    declared_value: float | None = Field(None, ge=0)
    special_handling_notes: str | None = None


class GroceryDetailInput(BaseModel):
    service_type: Literal[ServiceType.GROCERY] = ServiceType.GROCERY
    store_id: UUID
    total_items: int = Field(0, ge=0)
    special_notes: str | None = None
    contactless_delivery: bool = False
    estimated_bag_count: int | None = None


ServiceDetailInput = Annotated[
    CityRideDetailInput | IntercityDetailInput | FreightDetailInput | CourierDetailInput | GroceryDetailInput,
    Field(discriminator="service_type"),
]


# ============================================================
# Core ride schemas
# ============================================================

class CreateRideRequest(BaseModel):
    service_type: ServiceType
    category: ServiceCategory
    pricing_mode: PricingMode = PricingMode.FIXED
    stops: list[StopInput] = Field(..., min_length=2)
    detail: ServiceDetailInput
    baseline_min_price: float | None = Field(None, ge=0)
    baseline_max_price: float | None = Field(None, ge=0)
    scheduled_at: datetime | None = None
    auto_accept_driver: bool = True

    @model_validator(mode="after")
    def validate_stop_types(self) -> CreateRideRequest:
        types = {s.stop_type for s in self.stops}
        if StopType.PICKUP not in types:
            raise ValueError("At least one PICKUP stop is required.")
        if StopType.DROPOFF not in types:
            raise ValueError("At least one DROPOFF stop is required.")
        orders = [s.sequence_order for s in self.stops]
        if len(orders) != len(set(orders)):
            raise ValueError("Stop sequence_order values must be unique.")
        return self

    @model_validator(mode="after")
    def validate_detail_matches_service_type(self) -> CreateRideRequest:
        expected = self.service_type.value
        actual = self.detail.service_type.value
        if expected != actual:
            raise ValueError(
                f"detail.service_type '{actual}' does not match service_type '{expected}'."
            )
        return self

    @model_validator(mode="after")
    def validate_price_range(self) -> CreateRideRequest:
        lo, hi = self.baseline_min_price, self.baseline_max_price
        if lo is not None and hi is not None and lo > hi:
            raise ValueError("baseline_min_price must not exceed baseline_max_price.")
        return self


class UpdateRideRequest(BaseModel):
    """PATCH — only explicitly provided fields are updated."""
    baseline_min_price: float | None = Field(None, ge=0)
    baseline_max_price: float | None = Field(None, ge=0)
    final_price: float | None = Field(None, ge=0)
    scheduled_at: datetime | None = None
    is_risky: bool | None = None


class CancelRideRequest(BaseModel):
    reason: str | None = Field(None, max_length=500)


class AcceptRideRequest(BaseModel):
    """No driver_id — the acting driver is derived from the authenticated JWT principal."""


class VerifyAndStartRequest(BaseModel):
    """Optional OTP code submitted at ride start.

    No driver_id — the acting driver is derived from the authenticated JWT principal.
    """
    verification_code: str | None = Field(None, min_length=4, max_length=10)


class VerifyAndCompleteRequest(BaseModel):
    """Optional OTP code submitted at ride completion.

    No driver_id — the acting driver is derived from the authenticated JWT principal.
    """
    verification_code: str | None = Field(None, min_length=4, max_length=10)
    final_price: float | None = Field(None, ge=0)


class AddStopRequest(BaseModel):
    sequence_order: int = Field(..., ge=1)
    stop_type: StopType
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    place_name: str | None = Field(None, max_length=255)
    address_line_1: str | None = Field(None, max_length=255)
    city: str | None = Field(None, max_length=120)
    country: str | None = Field(None, max_length=120)
    contact_name: str | None = Field(None, max_length=255)
    contact_phone: str | None = Field(None, max_length=30)
    instructions: str | None = None


# ============================================================
# Response schemas
# ============================================================

class RideResponse(BaseModel):
    id: UUID
    passenger_id: UUID
    assigned_driver_id: UUID | None
    service_type: ServiceType
    category: ServiceCategory
    pricing_mode: PricingMode
    status: RideStatus
    baseline_min_price: float | None
    baseline_max_price: float | None
    final_price: float | None
    scheduled_at: datetime | None
    is_scheduled: bool
    is_risky: bool
    auto_accept_driver: bool
    accepted_at: datetime | None
    completed_at: datetime | None
    cancelled_at: datetime | None
    cancellation_reason: str | None
    created_at: datetime
    stops: list[StopResponse]
    proof_images: list[ProofImageResponse]
    verification_codes: list[VerificationCodeResponse]
    # Derived convenience fields
    pickup_stop: StopResponse | None
    dropoff_stop: StopResponse | None


class RideSummaryResponse(BaseModel):
    """Lightweight list-view response."""
    id: UUID
    passenger_id: UUID
    assigned_driver_id: UUID | None
    service_type: ServiceType
    category: ServiceCategory
    status: RideStatus
    created_at: datetime
    scheduled_at: datetime | None
    pickup_stop: StopResponse | None
    dropoff_stop: StopResponse | None


class DriverCandidateResponse(BaseModel):
    driver_id: UUID
    distance_km: float
    vehicle_type: str
    rating: float | None
    priority_score: float
    estimated_arrival_minutes: float | None


class NearbyDriversResponse(BaseModel):
    ride_id: UUID | None
    candidates: list[DriverCandidateResponse]
    count: int


class PaginatedRidesResponse(BaseModel):
    rides: list[RideSummaryResponse]
    total: int
    limit: int
    offset: int
