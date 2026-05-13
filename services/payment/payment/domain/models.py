from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from uuid import UUID, uuid4


class PassengerPaymentMethod(str, Enum):
    CARD = "CARD"
    CASH = "CASH"
    EASYPAISA = "EASYPAISA"
    JAZZCASH = "JAZZCASH"


class DriverTopupMethod(str, Enum):
    CARD = "CARD"
    EASYPAISA = "EASYPAISA"
    JAZZCASH = "JAZZCASH"


class CollectionMode(str, Enum):
    PLATFORM_COLLECTED = "PLATFORM_COLLECTED"
    DRIVER_COLLECTED = "DRIVER_COLLECTED"


class WalletStatus(str, Enum):
    ACTIVE = "ACTIVE"
    FROZEN = "FROZEN"


class LedgerEntryType(str, Enum):
    TOPUP_PENDING = "TOPUP_PENDING"
    TOPUP_CREDIT = "TOPUP_CREDIT"
    COMMISSION_RESERVE = "COMMISSION_RESERVE"
    COMMISSION_CAPTURE = "COMMISSION_CAPTURE"
    COMMISSION_RELEASE = "COMMISSION_RELEASE"
    COMMISSION_DELTA_DEBIT = "COMMISSION_DELTA_DEBIT"
    COMMISSION_DELTA_RELEASE = "COMMISSION_DELTA_RELEASE"
    REVERSAL = "REVERSAL"
    ADJUSTMENT = "ADJUSTMENT"


class PaymentIntentStatus(str, Enum):
    CREATED = "CREATED"
    AUTHORIZED = "AUTHORIZED"
    REQUIRES_ACTION = "REQUIRES_ACTION"
    CAPTURED = "CAPTURED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"
    REFUNDED = "REFUNDED"


class PaymentStatus(str, Enum):
    PENDING = "PENDING"
    AUTHORIZED = "AUTHORIZED"
    PAID = "PAID"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"
    REFUNDED = "REFUNDED"
    REQUIRES_ACTION = "REQUIRES_ACTION"
    COLLECTION_UNCONFIRMED = "COLLECTION_UNCONFIRMED"


class ReservationStatus(str, Enum):
    RESERVED = "RESERVED"
    CAPTURED = "CAPTURED"
    RELEASED = "RELEASED"
    EXPIRED = "EXPIRED"


class ProviderStatus(str, Enum):
    INITIATED = "INITIATED"
    PENDING = "PENDING"
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"
    DISPUTED = "DISPUTED"


class Provider(str, Enum):
    SANDBOX = "SANDBOX"
    CARD = "CARD"
    EASYPAISA = "EASYPAISA"
    JAZZCASH = "JAZZCASH"


@dataclass
class CommissionQuote:
    basis_amount: float
    commission_amount: float
    rate_snapshot: float
    currency: str = "PKR"


@dataclass
class Wallet:
    id: UUID
    driver_id: UUID
    available_balance: float = 0.0
    reserved_balance: float = 0.0
    current_balance: float = 0.0
    currency: str = "PKR"
    status: WalletStatus = WalletStatus.ACTIVE
    negative_limit: float = 0.0
    max_reserved_limit: float = 100000.0

    @classmethod
    def create(cls, driver_id: UUID, *, currency: str = "PKR") -> Wallet:
        return cls(id=uuid4(), driver_id=driver_id, currency=currency)


@dataclass
class CommissionReservation:
    id: UUID
    ride_id: UUID
    driver_id: UUID
    wallet_id: UUID
    commission_policy_id: UUID
    rate_snapshot: float
    basis_amount: float
    reserved_amount: float
    captured_amount: float = 0.0
    released_amount: float = 0.0
    currency: str = "PKR"
    status: ReservationStatus = ReservationStatus.RESERVED
    expires_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc) + timedelta(hours=2))
