"""payment service schema and ride payment fields.

Revision ID: 0008_payment_service
Revises: 0007_pr18_reliability_contract_fixes
Create Date: 2026-05-05 00:00:00.000000
"""
from __future__ import annotations

import uuid
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0008_payment_service"
down_revision: str | None = "0007_pr18_reliability_contract_fixes"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def _enum(name: str, values: list[str]) -> postgresql.ENUM:
    return postgresql.ENUM(*values, name=name, schema="payment", create_type=False)


def upgrade() -> None:
    op.execute("CREATE SCHEMA IF NOT EXISTS payment")
    enums = {
        "wallet_status_enum": ["ACTIVE", "FROZEN"],
        "ledger_entry_type_enum": [
            "TOPUP_PENDING", "TOPUP_CREDIT", "COMMISSION_RESERVE",
            "COMMISSION_CAPTURE", "COMMISSION_RELEASE", "COMMISSION_DELTA_DEBIT",
            "COMMISSION_DELTA_RELEASE", "REVERSAL", "ADJUSTMENT",
        ],
        "payment_intent_status_enum": ["CREATED", "AUTHORIZED", "REQUIRES_ACTION", "CAPTURED", "FAILED", "CANCELLED", "REFUNDED"],
        "passenger_payment_method_enum": ["CARD", "CASH", "EASYPAISA", "JAZZCASH"],
        "driver_topup_method_enum": ["CARD", "EASYPAISA", "JAZZCASH"],
        "collection_mode_enum": ["PLATFORM_COLLECTED", "DRIVER_COLLECTED"],
        "payment_status_enum": ["PENDING", "AUTHORIZED", "PAID", "FAILED", "CANCELLED", "REFUNDED", "REQUIRES_ACTION", "COLLECTION_UNCONFIRMED"],
        "reservation_status_enum": ["RESERVED", "CAPTURED", "RELEASED", "EXPIRED"],
        "provider_status_enum": ["INITIATED", "PENDING", "SUCCEEDED", "FAILED", "CANCELLED", "DISPUTED"],
    }
    for name, values in enums.items():
        postgresql.ENUM(*values, name=name, schema="payment").create(op.get_bind(), checkfirst=True)

    op.create_table(
        "wallets",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("driver_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("verification.drivers.id", ondelete="CASCADE"), nullable=False),
        sa.Column("available_balance", sa.Numeric(14, 2), nullable=False, server_default="0"),
        sa.Column("reserved_balance", sa.Numeric(14, 2), nullable=False, server_default="0"),
        sa.Column("current_balance", sa.Numeric(14, 2), nullable=False, server_default="0"),
        sa.Column("currency", sa.String(10), nullable=False, server_default="PKR"),
        sa.Column("status", _enum("wallet_status_enum", enums["wallet_status_enum"]), nullable=False, server_default="ACTIVE"),
        sa.Column("negative_limit", sa.Numeric(14, 2), nullable=False, server_default="0"),
        sa.Column("max_reserved_limit", sa.Numeric(14, 2), nullable=False, server_default="100000"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint("available_balance >= negative_limit * -1", name="ck_wallet_available_negative_limit"),
        sa.CheckConstraint("reserved_balance >= 0", name="ck_wallet_reserved_non_negative"),
        sa.UniqueConstraint("driver_id"),
        schema="payment",
    )
    op.create_index("ix_payment_wallets_driver_id", "wallets", ["driver_id"], schema="payment")
    op.create_index("ix_payment_wallets_status", "wallets", ["status"], schema="payment")

    op.create_table(
        "payment_methods",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("owner_user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("auth.users.id", ondelete="CASCADE")),
        sa.Column("owner_driver_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("verification.drivers.id", ondelete="CASCADE")),
        sa.Column("method_type", sa.String(30), nullable=False),
        sa.Column("provider", sa.String(40), nullable=False, server_default="SANDBOX"),
        sa.Column("provider_customer_id", sa.String(160)),
        sa.Column("provider_payment_method_id", sa.String(220), nullable=False, unique=True),
        sa.Column("brand", sa.String(40)),
        sa.Column("last4", sa.String(4)),
        sa.Column("expiry_month", sa.Integer),
        sa.Column("expiry_year", sa.Integer),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default=sa.false()),
        sa.Column("is_deleted", sa.Boolean, nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        schema="payment",
    )

    op.create_table(
        "payment_intents",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("ride_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("passenger_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("auth.users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("amount_estimated", sa.Numeric(14, 2)),
        sa.Column("amount_final", sa.Numeric(14, 2)),
        sa.Column("currency", sa.String(10), nullable=False, server_default="PKR"),
        sa.Column("status", _enum("payment_intent_status_enum", enums["payment_intent_status_enum"]), nullable=False, server_default="CREATED"),
        sa.Column("active_payment_method_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("payment.payment_methods.id", ondelete="SET NULL")),
        sa.Column("provider", sa.String(40), nullable=False, server_default="SANDBOX"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        schema="payment",
    )

    op.create_table(
        "ride_payments",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("ride_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("passenger_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("auth.users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("payment_intent_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("payment.payment_intents.id", ondelete="SET NULL")),
        sa.Column("passenger_payment_method", _enum("passenger_payment_method_enum", enums["passenger_payment_method_enum"]), nullable=False),
        sa.Column("collection_mode", _enum("collection_mode_enum", enums["collection_mode_enum"]), nullable=False),
        sa.Column("amount_estimated", sa.Numeric(14, 2)),
        sa.Column("amount_final", sa.Numeric(14, 2)),
        sa.Column("status", _enum("payment_status_enum", enums["payment_status_enum"]), nullable=False, server_default="PENDING"),
        sa.Column("currency", sa.String(10), nullable=False, server_default="PKR"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("ride_id", name="uq_ride_payments_ride"),
        schema="payment",
    )

    op.create_table(
        "commission_policies",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("rate", sa.Numeric(6, 4), nullable=False),
        sa.Column("currency", sa.String(10), nullable=False, server_default="PKR"),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default=sa.true()),
        sa.Column("effective_from", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("effective_to", sa.DateTime(timezone=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        schema="payment",
    )
    op.execute(
        "INSERT INTO payment.commission_policies (id, name, rate, currency, is_active) "
        f"VALUES ('{uuid.uuid4()}', 'Default commission', 0.15, 'PKR', true)"
    )

    op.create_table(
        "commission_reservations",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("ride_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("driver_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("verification.drivers.id", ondelete="CASCADE"), nullable=False),
        sa.Column("wallet_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("payment.wallets.id", ondelete="CASCADE"), nullable=False),
        sa.Column("commission_policy_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("payment.commission_policies.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("rate_snapshot", sa.Numeric(6, 4), nullable=False),
        sa.Column("basis_amount", sa.Numeric(14, 2), nullable=False),
        sa.Column("reserved_amount", sa.Numeric(14, 2), nullable=False),
        sa.Column("captured_amount", sa.Numeric(14, 2), nullable=False, server_default="0"),
        sa.Column("released_amount", sa.Numeric(14, 2), nullable=False, server_default="0"),
        sa.Column("currency", sa.String(10), nullable=False, server_default="PKR"),
        sa.Column("calculation_details", postgresql.JSONB, nullable=False, server_default="{}"),
        sa.Column("status", _enum("reservation_status_enum", enums["reservation_status_enum"]), nullable=False, server_default="RESERVED"),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("ride_id", "driver_id", name="uq_commission_reservation_ride_driver"),
        schema="payment",
    )

    op.create_table(
        "wallet_ledger_entries",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("wallet_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("payment.wallets.id", ondelete="CASCADE"), nullable=False),
        sa.Column("driver_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("ride_id", postgresql.UUID(as_uuid=True)),
        sa.Column("reservation_id", postgresql.UUID(as_uuid=True)),
        sa.Column("topup_id", postgresql.UUID(as_uuid=True)),
        sa.Column("provider_transaction_id", postgresql.UUID(as_uuid=True)),
        sa.Column("entry_type", _enum("ledger_entry_type_enum", enums["ledger_entry_type_enum"]), nullable=False),
        sa.Column("amount", sa.Numeric(14, 2), nullable=False),
        sa.Column("currency", sa.String(10), nullable=False, server_default="PKR"),
        sa.Column("balance_before", postgresql.JSONB, nullable=False, server_default="{}"),
        sa.Column("balance_after", postgresql.JSONB, nullable=False, server_default="{}"),
        sa.Column("source_service", sa.String(80)),
        sa.Column("actor_id", sa.String(120)),
        sa.Column("reason", sa.Text),
        sa.Column("correlation_id", sa.String(120)),
        sa.Column("idempotency_key", sa.String(180), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("idempotency_key", name="uq_wallet_ledger_idempotency"),
        schema="payment",
    )

    op.create_table(
        "topups",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("wallet_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("payment.wallets.id", ondelete="CASCADE"), nullable=False),
        sa.Column("driver_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("method", _enum("driver_topup_method_enum", enums["driver_topup_method_enum"]), nullable=False),
        sa.Column("amount", sa.Numeric(14, 2), nullable=False),
        sa.Column("currency", sa.String(10), nullable=False, server_default="PKR"),
        sa.Column("status", _enum("provider_status_enum", enums["provider_status_enum"]), nullable=False, server_default="INITIATED"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        schema="payment",
    )

    op.create_table(
        "provider_transactions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("provider", sa.String(40), nullable=False),
        sa.Column("provider_transaction_id", sa.String(220), nullable=False),
        sa.Column("payment_intent_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("payment.payment_intents.id", ondelete="SET NULL")),
        sa.Column("topup_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("payment.topups.id", ondelete="SET NULL")),
        sa.Column("status", _enum("provider_status_enum", enums["provider_status_enum"]), nullable=False),
        sa.Column("amount", sa.Numeric(14, 2)),
        sa.Column("currency", sa.String(10), nullable=False, server_default="PKR"),
        sa.Column("signature_verified", sa.Boolean, nullable=False, server_default=sa.false()),
        sa.Column("metadata_json", postgresql.JSONB, nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("provider", "provider_transaction_id", name="uq_provider_transaction"),
        schema="payment",
    )

    op.create_table(
        "driver_collection_confirmations",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("ride_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("driver_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("passenger_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("method", _enum("passenger_payment_method_enum", enums["passenger_payment_method_enum"]), nullable=False),
        sa.Column("amount_collected", sa.Numeric(14, 2), nullable=False),
        sa.Column("confirmed_by_driver_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("confirmed_by_passenger_at", sa.DateTime(timezone=True)),
        sa.Column("notes", sa.Text),
        sa.Column("is_disputed", sa.Boolean, nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("ride_id", name="uq_driver_collection_ride"),
        schema="payment",
    )

    op.create_table(
        "outbox_events",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("event_type", sa.String(160), nullable=False),
        sa.Column("aggregate_id", sa.String(120)),
        sa.Column("aggregate_type", sa.String(80)),
        sa.Column("topic", sa.String(160), nullable=False, server_default="payment-events"),
        sa.Column("payload", postgresql.JSONB, nullable=False, server_default="{}"),
        sa.Column("correlation_id", sa.String(120)),
        sa.Column("idempotency_key", sa.String(180), unique=True),
        sa.Column("processed_at", sa.DateTime(timezone=True)),
        sa.Column("error_count", sa.Integer, nullable=False, server_default="0"),
        sa.Column("last_error", sa.Text),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        schema="payment",
    )
    op.create_table(
        "inbox_messages",
        sa.Column("event_id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("event_type", sa.String(160), nullable=False),
        sa.Column("source_topic", sa.String(160), nullable=False),
        sa.Column("source_partition", sa.Integer),
        sa.Column("source_offset", sa.Integer),
        sa.Column("aggregate_id", sa.String(120)),
        sa.Column("payload", postgresql.JSONB, nullable=False, server_default="{}"),
        sa.Column("received_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("processed_at", sa.DateTime(timezone=True)),
        sa.Column("error_count", sa.Integer, nullable=False, server_default="0"),
        sa.Column("last_error", sa.Text),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        schema="payment",
    )
    op.create_table(
        "reconciliation_runs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("provider", sa.String(40), nullable=False),
        sa.Column("status", sa.String(40), nullable=False, server_default="RUNNING"),
        sa.Column("started_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        schema="payment",
    )
    op.create_table(
        "reconciliation_items",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("run_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("payment.reconciliation_runs.id", ondelete="CASCADE"), nullable=False),
        sa.Column("provider_transaction_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("payment.provider_transactions.id", ondelete="SET NULL")),
        sa.Column("mismatch_type", sa.String(80), nullable=False),
        sa.Column("details", postgresql.JSONB, nullable=False, server_default="{}"),
        sa.Column("resolved_at", sa.DateTime(timezone=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        schema="payment",
    )

    op.add_column("service_requests", sa.Column("passenger_payment_method", sa.String(30), nullable=False, server_default="CASH"), schema="service_request")
    op.add_column("service_requests", sa.Column("passenger_payment_method_id", postgresql.UUID(as_uuid=True), nullable=True), schema="service_request")
    op.add_column("service_requests", sa.Column("payment_collection_mode", sa.String(30), nullable=False, server_default="DRIVER_COLLECTED"), schema="service_request")


def downgrade() -> None:
    op.drop_column("service_requests", "payment_collection_mode", schema="service_request")
    op.drop_column("service_requests", "passenger_payment_method_id", schema="service_request")
    op.drop_column("service_requests", "passenger_payment_method", schema="service_request")
    for table in [
        "reconciliation_items", "reconciliation_runs", "inbox_messages", "outbox_events",
        "driver_collection_confirmations", "provider_transactions", "topups",
        "wallet_ledger_entries", "commission_reservations", "commission_policies",
        "ride_payments", "payment_intents", "payment_methods", "wallets",
    ]:
        op.drop_table(table, schema="payment")
    for name in [
        "provider_status_enum", "reservation_status_enum", "payment_status_enum",
        "collection_mode_enum", "driver_topup_method_enum", "passenger_payment_method_enum",
        "payment_intent_status_enum", "ledger_entry_type_enum", "wallet_status_enum",
    ]:
        postgresql.ENUM(name=name, schema="payment").drop(op.get_bind(), checkfirst=True)
    op.execute("DROP SCHEMA IF EXISTS payment")
