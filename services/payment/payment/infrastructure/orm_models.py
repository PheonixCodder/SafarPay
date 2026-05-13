from __future__ import annotations

import enum
import uuid
from datetime import datetime, timezone

from sp.infrastructure.db.base import Base, TimestampMixin
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
    UniqueConstraint,
    func,
)
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PgUUID
from sqlalchemy.orm import Mapped, mapped_column


class PassengerPaymentMethod(enum.Enum):
    CARD = "CARD"
    CASH = "CASH"
    EASYPAISA = "EASYPAISA"
    JAZZCASH = "JAZZCASH"


class DriverTopupMethod(enum.Enum):
    CARD = "CARD"
    EASYPAISA = "EASYPAISA"
    JAZZCASH = "JAZZCASH"


class CollectionMode(enum.Enum):
    PLATFORM_COLLECTED = "PLATFORM_COLLECTED"
    DRIVER_COLLECTED = "DRIVER_COLLECTED"


class WalletStatus(enum.Enum):
    ACTIVE = "ACTIVE"
    FROZEN = "FROZEN"


class LedgerEntryType(enum.Enum):
    TOPUP_PENDING = "TOPUP_PENDING"
    TOPUP_CREDIT = "TOPUP_CREDIT"
    COMMISSION_RESERVE = "COMMISSION_RESERVE"
    COMMISSION_CAPTURE = "COMMISSION_CAPTURE"
    COMMISSION_RELEASE = "COMMISSION_RELEASE"
    COMMISSION_DELTA_DEBIT = "COMMISSION_DELTA_DEBIT"
    COMMISSION_DELTA_RELEASE = "COMMISSION_DELTA_RELEASE"
    REVERSAL = "REVERSAL"
    ADJUSTMENT = "ADJUSTMENT"


class PaymentIntentStatus(enum.Enum):
    CREATED = "CREATED"
    AUTHORIZED = "AUTHORIZED"
    REQUIRES_ACTION = "REQUIRES_ACTION"
    CAPTURED = "CAPTURED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"
    REFUNDED = "REFUNDED"


class PaymentStatus(enum.Enum):
    PENDING = "PENDING"
    AUTHORIZED = "AUTHORIZED"
    PAID = "PAID"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"
    REFUNDED = "REFUNDED"
    REQUIRES_ACTION = "REQUIRES_ACTION"
    COLLECTION_UNCONFIRMED = "COLLECTION_UNCONFIRMED"


class ReservationStatus(enum.Enum):
    RESERVED = "RESERVED"
    CAPTURED = "CAPTURED"
    RELEASED = "RELEASED"
    EXPIRED = "EXPIRED"


class ProviderStatus(enum.Enum):
    INITIATED = "INITIATED"
    PENDING = "PENDING"
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"
    DISPUTED = "DISPUTED"


class WalletORM(Base, TimestampMixin):
    __tablename__ = "wallets"
    __table_args__ = (
        CheckConstraint("available_balance >= negative_limit * -1", name="ck_wallet_available_negative_limit"),
        CheckConstraint("reserved_balance >= 0", name="ck_wallet_reserved_non_negative"),
        {"schema": "payment"},
    )

    id: Mapped[uuid.UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    driver_id: Mapped[uuid.UUID] = mapped_column(PgUUID(as_uuid=True), ForeignKey("verification.drivers.id", ondelete="CASCADE"), unique=True, index=True)
    available_balance: Mapped[float] = mapped_column(Numeric(14, 2), default=0, nullable=False)
    reserved_balance: Mapped[float] = mapped_column(Numeric(14, 2), default=0, nullable=False)
    current_balance: Mapped[float] = mapped_column(Numeric(14, 2), default=0, nullable=False)
    currency: Mapped[str] = mapped_column(String(10), default="PKR", nullable=False)
    status: Mapped[WalletStatus] = mapped_column(SQLEnum(WalletStatus, name="wallet_status_enum", schema="payment"), default=WalletStatus.ACTIVE, nullable=False, index=True)
    negative_limit: Mapped[float] = mapped_column(Numeric(14, 2), default=0, nullable=False)
    max_reserved_limit: Mapped[float] = mapped_column(Numeric(14, 2), default=100000, nullable=False)


class WalletLedgerEntryORM(Base, TimestampMixin):
    __tablename__ = "wallet_ledger_entries"
    __table_args__ = (
        UniqueConstraint("idempotency_key", name="uq_wallet_ledger_idempotency"),
        Index("ix_wallet_ledger_wallet_created", "wallet_id", "created_at"),
        Index("ix_wallet_ledger_ride", "ride_id"),
        {"schema": "payment"},
    )

    id: Mapped[uuid.UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    wallet_id: Mapped[uuid.UUID] = mapped_column(PgUUID(as_uuid=True), ForeignKey("payment.wallets.id", ondelete="CASCADE"), index=True)
    driver_id: Mapped[uuid.UUID] = mapped_column(PgUUID(as_uuid=True), index=True)
    ride_id: Mapped[uuid.UUID | None] = mapped_column(PgUUID(as_uuid=True), index=True)
    reservation_id: Mapped[uuid.UUID | None] = mapped_column(PgUUID(as_uuid=True), index=True)
    topup_id: Mapped[uuid.UUID | None] = mapped_column(PgUUID(as_uuid=True), index=True)
    provider_transaction_id: Mapped[uuid.UUID | None] = mapped_column(PgUUID(as_uuid=True), index=True)
    entry_type: Mapped[LedgerEntryType] = mapped_column(SQLEnum(LedgerEntryType, name="ledger_entry_type_enum", schema="payment"), nullable=False, index=True)
    amount: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(10), default="PKR", nullable=False)
    balance_before: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    balance_after: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    source_service: Mapped[str | None] = mapped_column(String(80))
    actor_id: Mapped[str | None] = mapped_column(String(120))
    reason: Mapped[str | None] = mapped_column(Text)
    correlation_id: Mapped[str | None] = mapped_column(String(120), index=True)
    idempotency_key: Mapped[str] = mapped_column(String(180), nullable=False)


class PaymentMethodORM(Base, TimestampMixin):
    __tablename__ = "payment_methods"
    __table_args__ = (
        Index("ix_payment_methods_owner_active", "owner_user_id", "is_active"),
        {"schema": "payment"},
    )

    id: Mapped[uuid.UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    owner_user_id: Mapped[uuid.UUID | None] = mapped_column(PgUUID(as_uuid=True), ForeignKey("auth.users.id", ondelete="CASCADE"), index=True)
    owner_driver_id: Mapped[uuid.UUID | None] = mapped_column(PgUUID(as_uuid=True), ForeignKey("verification.drivers.id", ondelete="CASCADE"), index=True)
    method_type: Mapped[str] = mapped_column(String(30), nullable=False)
    provider: Mapped[str] = mapped_column(String(40), nullable=False, default="SANDBOX")
    provider_customer_id: Mapped[str | None] = mapped_column(String(160))
    provider_payment_method_id: Mapped[str] = mapped_column(String(220), nullable=False, unique=True)
    brand: Mapped[str | None] = mapped_column(String(40))
    last4: Mapped[str | None] = mapped_column(String(4))
    expiry_month: Mapped[int | None] = mapped_column(Integer)
    expiry_year: Mapped[int | None] = mapped_column(Integer)
    is_active: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)


class PaymentIntentORM(Base, TimestampMixin):
    __tablename__ = "payment_intents"
    __table_args__ = (
        Index("ix_payment_intents_ride", "ride_id"),
        {"schema": "payment"},
    )

    id: Mapped[uuid.UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ride_id: Mapped[uuid.UUID] = mapped_column(PgUUID(as_uuid=True), nullable=False, index=True)
    passenger_id: Mapped[uuid.UUID] = mapped_column(PgUUID(as_uuid=True), ForeignKey("auth.users.id", ondelete="CASCADE"), nullable=False, index=True)
    amount_estimated: Mapped[float | None] = mapped_column(Numeric(14, 2))
    amount_final: Mapped[float | None] = mapped_column(Numeric(14, 2))
    currency: Mapped[str] = mapped_column(String(10), default="PKR", nullable=False)
    status: Mapped[PaymentIntentStatus] = mapped_column(SQLEnum(PaymentIntentStatus, name="payment_intent_status_enum", schema="payment"), default=PaymentIntentStatus.CREATED, nullable=False, index=True)
    active_payment_method_id: Mapped[uuid.UUID | None] = mapped_column(PgUUID(as_uuid=True), ForeignKey("payment.payment_methods.id", ondelete="SET NULL"))
    provider: Mapped[str] = mapped_column(String(40), default="SANDBOX", nullable=False)


class RidePaymentORM(Base, TimestampMixin):
    __tablename__ = "ride_payments"
    __table_args__ = (
        UniqueConstraint("ride_id", name="uq_ride_payments_ride"),
        {"schema": "payment"},
    )

    id: Mapped[uuid.UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ride_id: Mapped[uuid.UUID] = mapped_column(PgUUID(as_uuid=True), nullable=False, index=True)
    passenger_id: Mapped[uuid.UUID] = mapped_column(PgUUID(as_uuid=True), ForeignKey("auth.users.id", ondelete="CASCADE"), nullable=False, index=True)
    payment_intent_id: Mapped[uuid.UUID | None] = mapped_column(PgUUID(as_uuid=True), ForeignKey("payment.payment_intents.id", ondelete="SET NULL"))
    passenger_payment_method: Mapped[PassengerPaymentMethod] = mapped_column(SQLEnum(PassengerPaymentMethod, name="passenger_payment_method_enum", schema="payment"), nullable=False)
    collection_mode: Mapped[CollectionMode] = mapped_column(SQLEnum(CollectionMode, name="collection_mode_enum", schema="payment"), nullable=False)
    amount_estimated: Mapped[float | None] = mapped_column(Numeric(14, 2))
    amount_final: Mapped[float | None] = mapped_column(Numeric(14, 2))
    status: Mapped[PaymentStatus] = mapped_column(SQLEnum(PaymentStatus, name="payment_status_enum", schema="payment"), default=PaymentStatus.PENDING, nullable=False, index=True)
    currency: Mapped[str] = mapped_column(String(10), default="PKR", nullable=False)


class CommissionPolicyORM(Base, TimestampMixin):
    __tablename__ = "commission_policies"
    __table_args__ = {"schema": "payment"}

    id: Mapped[uuid.UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    rate: Mapped[float] = mapped_column(Numeric(6, 4), nullable=False)
    currency: Mapped[str] = mapped_column(String(10), default="PKR", nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)
    effective_from: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    effective_to: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class CommissionReservationORM(Base, TimestampMixin):
    __tablename__ = "commission_reservations"
    __table_args__ = (
        UniqueConstraint("ride_id", "driver_id", name="uq_commission_reservation_ride_driver"),
        Index("ix_commission_reservations_expiry", "status", "expires_at"),
        {"schema": "payment"},
    )

    id: Mapped[uuid.UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ride_id: Mapped[uuid.UUID] = mapped_column(PgUUID(as_uuid=True), nullable=False, index=True)
    driver_id: Mapped[uuid.UUID] = mapped_column(PgUUID(as_uuid=True), ForeignKey("verification.drivers.id", ondelete="CASCADE"), nullable=False, index=True)
    wallet_id: Mapped[uuid.UUID] = mapped_column(PgUUID(as_uuid=True), ForeignKey("payment.wallets.id", ondelete="CASCADE"), nullable=False)
    commission_policy_id: Mapped[uuid.UUID] = mapped_column(PgUUID(as_uuid=True), ForeignKey("payment.commission_policies.id", ondelete="RESTRICT"), nullable=False)
    rate_snapshot: Mapped[float] = mapped_column(Numeric(6, 4), nullable=False)
    basis_amount: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False)
    reserved_amount: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False)
    captured_amount: Mapped[float] = mapped_column(Numeric(14, 2), default=0, nullable=False)
    released_amount: Mapped[float] = mapped_column(Numeric(14, 2), default=0, nullable=False)
    currency: Mapped[str] = mapped_column(String(10), default="PKR", nullable=False)
    calculation_details: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    status: Mapped[ReservationStatus] = mapped_column(SQLEnum(ReservationStatus, name="reservation_status_enum", schema="payment"), default=ReservationStatus.RESERVED, nullable=False, index=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class DriverCollectionConfirmationORM(Base, TimestampMixin):
    __tablename__ = "driver_collection_confirmations"
    __table_args__ = (
        UniqueConstraint("ride_id", name="uq_driver_collection_ride"),
        {"schema": "payment"},
    )

    id: Mapped[uuid.UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ride_id: Mapped[uuid.UUID] = mapped_column(PgUUID(as_uuid=True), nullable=False, index=True)
    driver_id: Mapped[uuid.UUID] = mapped_column(PgUUID(as_uuid=True), nullable=False, index=True)
    passenger_id: Mapped[uuid.UUID] = mapped_column(PgUUID(as_uuid=True), nullable=False, index=True)
    method: Mapped[PassengerPaymentMethod] = mapped_column(SQLEnum(PassengerPaymentMethod, name="passenger_payment_method_enum", schema="payment"), nullable=False)
    amount_collected: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False)
    confirmed_by_driver_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    confirmed_by_passenger_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    notes: Mapped[str | None] = mapped_column(Text)
    is_disputed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)


class TopupORM(Base, TimestampMixin):
    __tablename__ = "topups"
    __table_args__ = {"schema": "payment"}

    id: Mapped[uuid.UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    wallet_id: Mapped[uuid.UUID] = mapped_column(PgUUID(as_uuid=True), ForeignKey("payment.wallets.id", ondelete="CASCADE"), nullable=False, index=True)
    driver_id: Mapped[uuid.UUID] = mapped_column(PgUUID(as_uuid=True), nullable=False, index=True)
    method: Mapped[DriverTopupMethod] = mapped_column(SQLEnum(DriverTopupMethod, name="driver_topup_method_enum", schema="payment"), nullable=False)
    amount: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(10), default="PKR", nullable=False)
    status: Mapped[ProviderStatus] = mapped_column(SQLEnum(ProviderStatus, name="provider_status_enum", schema="payment"), default=ProviderStatus.INITIATED, nullable=False)


class ProviderTransactionORM(Base, TimestampMixin):
    __tablename__ = "provider_transactions"
    __table_args__ = (
        UniqueConstraint("provider", "provider_transaction_id", name="uq_provider_transaction"),
        {"schema": "payment"},
    )

    id: Mapped[uuid.UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    provider: Mapped[str] = mapped_column(String(40), nullable=False)
    provider_transaction_id: Mapped[str] = mapped_column(String(220), nullable=False)
    payment_intent_id: Mapped[uuid.UUID | None] = mapped_column(PgUUID(as_uuid=True), ForeignKey("payment.payment_intents.id", ondelete="SET NULL"), index=True)
    topup_id: Mapped[uuid.UUID | None] = mapped_column(PgUUID(as_uuid=True), ForeignKey("payment.topups.id", ondelete="SET NULL"), index=True)
    status: Mapped[ProviderStatus] = mapped_column(SQLEnum(ProviderStatus, name="provider_status_enum", schema="payment"), nullable=False)
    amount: Mapped[float | None] = mapped_column(Numeric(14, 2))
    currency: Mapped[str] = mapped_column(String(10), default="PKR", nullable=False)
    signature_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    metadata_json: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)


class ReconciliationRunORM(Base, TimestampMixin):
    __tablename__ = "reconciliation_runs"
    __table_args__ = {"schema": "payment"}

    id: Mapped[uuid.UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    provider: Mapped[str] = mapped_column(String(40), nullable=False)
    status: Mapped[str] = mapped_column(String(40), default="RUNNING", nullable=False)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class ReconciliationItemORM(Base, TimestampMixin):
    __tablename__ = "reconciliation_items"
    __table_args__ = {"schema": "payment"}

    id: Mapped[uuid.UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    run_id: Mapped[uuid.UUID] = mapped_column(PgUUID(as_uuid=True), ForeignKey("payment.reconciliation_runs.id", ondelete="CASCADE"), nullable=False, index=True)
    provider_transaction_id: Mapped[uuid.UUID | None] = mapped_column(PgUUID(as_uuid=True), ForeignKey("payment.provider_transactions.id", ondelete="SET NULL"))
    mismatch_type: Mapped[str] = mapped_column(String(80), nullable=False)
    details: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class PaymentOutboxEventORM(Base, TimestampMixin):
    __tablename__ = "outbox_events"
    __table_args__ = (
        Index("ix_payment_outbox_pending", "processed_at", "created_at"),
        {"schema": "payment"},
    )

    id: Mapped[uuid.UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    event_type: Mapped[str] = mapped_column(String(160), nullable=False, index=True)
    aggregate_id: Mapped[str | None] = mapped_column(String(120), index=True)
    aggregate_type: Mapped[str | None] = mapped_column(String(80))
    topic: Mapped[str] = mapped_column(String(160), nullable=False, default="payment-events")
    payload: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    correlation_id: Mapped[str | None] = mapped_column(String(120))
    idempotency_key: Mapped[str | None] = mapped_column(String(180), unique=True)
    processed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    error_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    last_error: Mapped[str | None] = mapped_column(Text)


class PaymentInboxMessageORM(Base, TimestampMixin):
    __tablename__ = "inbox_messages"
    __table_args__ = (
        Index("ix_payment_inbox_source_offset", "source_topic", "source_partition", "source_offset", unique=True),
        Index("ix_payment_inbox_pending", "processed_at", "received_at"),
        {"schema": "payment"},
    )

    event_id: Mapped[uuid.UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True)
    event_type: Mapped[str] = mapped_column(String(160), nullable=False, index=True)
    source_topic: Mapped[str] = mapped_column(String(160), nullable=False)
    source_partition: Mapped[int | None] = mapped_column(Integer)
    source_offset: Mapped[int | None] = mapped_column(Integer)
    aggregate_id: Mapped[str | None] = mapped_column(String(120), index=True)
    payload: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    received_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    processed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    error_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    last_error: Mapped[str | None] = mapped_column(Text)
