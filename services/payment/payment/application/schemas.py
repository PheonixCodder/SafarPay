from __future__ import annotations

from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field

from ..domain.models import (
    DriverTopupMethod,
    PassengerPaymentMethod,
    PaymentIntentStatus,
    PaymentStatus,
    ReservationStatus,
    WalletStatus,
)


class WalletResponse(BaseModel):
    id: UUID
    driver_id: UUID
    available_balance: float
    reserved_balance: float
    current_balance: float
    currency: str
    status: WalletStatus
    negative_limit: float
    max_reserved_limit: float


class LedgerEntryResponse(BaseModel):
    id: UUID
    wallet_id: UUID
    driver_id: UUID
    ride_id: UUID | None
    entry_type: str
    amount: float
    currency: str
    created_at: datetime
    reason: str | None


class CreateTopupRequest(BaseModel):
    method: DriverTopupMethod
    amount: float = Field(..., gt=0)
    provider_payload: dict = Field(default_factory=dict)


class TopupResponse(BaseModel):
    id: UUID
    wallet_id: UUID
    driver_id: UUID
    method: DriverTopupMethod
    amount: float
    currency: str
    status: str


class SetupIntentResponse(BaseModel):
    setup_intent_id: str
    provider: str
    client_secret: str | None = None


class CreateSandboxCardRequest(BaseModel):
    provider_payment_method_id: str
    brand: str | None = "visa"
    last4: str | None = Field(default="4242", min_length=4, max_length=4)
    expiry_month: int | None = Field(default=12, ge=1, le=12)
    expiry_year: int | None = Field(default=2030, ge=2024)
    set_active: bool = True


class PaymentMethodResponse(BaseModel):
    id: UUID
    method_type: str
    provider: str
    brand: str | None
    last4: str | None
    expiry_month: int | None
    expiry_year: int | None
    is_active: bool


class CreateRidePaymentRequest(BaseModel):
    passenger_id: UUID
    passenger_payment_method: PassengerPaymentMethod
    passenger_payment_method_id: UUID | None = None
    amount_estimated: float | None = Field(None, ge=0)
    currency: str = "PKR"
    correlation_id: str | None = None


class RidePaymentResponse(BaseModel):
    id: UUID
    ride_id: UUID
    passenger_id: UUID
    payment_intent_id: UUID | None
    passenger_payment_method: PassengerPaymentMethod
    collection_mode: str
    amount_estimated: float | None
    amount_final: float | None
    status: PaymentStatus
    currency: str


class ReserveCommissionRequest(BaseModel):
    driver_id: UUID
    passenger_id: UUID | None = None
    basis_amount: float = Field(..., ge=0)
    currency: str = "PKR"
    correlation_id: str | None = None


class ReservationResponse(BaseModel):
    id: UUID
    ride_id: UUID
    driver_id: UUID
    wallet_id: UUID
    basis_amount: float
    reserved_amount: float
    captured_amount: float
    released_amount: float
    currency: str
    status: ReservationStatus
    expires_at: datetime


class CaptureCommissionRequest(BaseModel):
    driver_id: UUID
    final_amount: float = Field(..., ge=0)
    currency: str = "PKR"
    correlation_id: str | None = None


class ReleaseCommissionRequest(BaseModel):
    driver_id: UUID | None = None
    reason: str | None = None
    correlation_id: str | None = None


class EligibilityRequest(BaseModel):
    basis_amount: float = Field(..., ge=0)
    currency: str = "PKR"


class EligibilityResponse(BaseModel):
    eligible: bool
    reason: str | None = None
    wallet_id: UUID | None = None
    required_commission: float
    available_balance: float | None = None
    reserved_balance: float | None = None


class CapturePaymentIntentRequest(BaseModel):
    amount_final: float = Field(..., ge=0)
    correlation_id: str | None = None


class CompleteRidePaymentRequest(BaseModel):
    driver_id: UUID
    final_amount: float = Field(..., ge=0)
    currency: str = "PKR"
    correlation_id: str | None = None


class PaymentIntentResponse(BaseModel):
    id: UUID
    ride_id: UUID
    passenger_id: UUID
    amount_estimated: float | None
    amount_final: float | None
    currency: str
    status: PaymentIntentStatus
    active_payment_method_id: UUID | None
    provider: str


class CollectionConfirmationRequest(BaseModel):
    driver_id: UUID
    passenger_id: UUID
    method: PassengerPaymentMethod
    amount_collected: float = Field(..., ge=0)
    notes: str | None = None


class CollectionConfirmationResponse(BaseModel):
    id: UUID
    ride_id: UUID
    driver_id: UUID
    passenger_id: UUID
    method: PassengerPaymentMethod
    amount_collected: float
    confirmed_by_driver_at: datetime
    confirmed_by_passenger_at: datetime | None
    is_disputed: bool


DriverEarningsPeriod = Literal["today", "week", "month"]


class DriverEarningsSummary(BaseModel):
    net_earnings: float
    gross_fares: float
    commission_total: float
    available_balance: float
    reserved_balance: float
    completed_trips: int
    active_minutes: int
    rating_avg: float | None
    cash_collected: float
    platform_collected: float


class DriverEarningsBreakdownItem(BaseModel):
    label: str
    date: str
    gross_fares: float
    commission_total: float
    net_earnings: float
    completed_trips: int


class DriverEarningsTrip(BaseModel):
    ride_id: UUID
    completed_at: datetime
    pickup_label: str
    dropoff_label: str
    service_type: str
    final_fare: float
    commission: float
    net_earning: float
    collection_mode: str


class DriverEarningsResponse(BaseModel):
    period: DriverEarningsPeriod
    currency: str
    summary: DriverEarningsSummary
    daily_breakdown: list[DriverEarningsBreakdownItem]
    recent_trips: list[DriverEarningsTrip]
    withdraw_available: bool = False
    withdraw_unavailable_reason: str | None = None
