"""Align bidding lifecycle contract.

Revision ID: 0004_bidding_lifecycle_contract
Revises: 0003_communication_service
Create Date: 2026-05-04
"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


revision = "0004_bidding_lifecycle_contract"
down_revision = "0003_communication_service"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE SCHEMA IF NOT EXISTS bidding")
    op.execute(
        """
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1
                FROM pg_type t
                JOIN pg_namespace n ON n.oid = t.typnamespace
                WHERE t.typname = 'bidding_pricing_mode_enum'
                  AND n.nspname = 'bidding'
            ) THEN
                CREATE TYPE bidding.bidding_pricing_mode_enum AS ENUM ('FIXED', 'BID_BASED', 'HYBRID');
            END IF;
        END $$;
        """
    )
    op.execute(
        """
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1
                FROM pg_type t
                JOIN pg_namespace n ON n.oid = t.typnamespace
                WHERE t.typname = 'bidding_session_status_enum'
                  AND n.nspname = 'bidding'
            ) THEN
                CREATE TYPE bidding.bidding_session_status_enum AS ENUM ('OPEN', 'CLOSED', 'EXPIRED', 'PAUSED');
            END IF;
            IF NOT EXISTS (
                SELECT 1
                FROM pg_type t
                JOIN pg_namespace n ON n.oid = t.typnamespace
                WHERE t.typname = 'bid_status_enum'
                  AND n.nspname = 'bidding'
            ) THEN
                CREATE TYPE bidding.bid_status_enum AS ENUM ('ACTIVE', 'OUTBID', 'WITHDRAWN', 'ACCEPTED', 'REJECTED', 'EXPIRED');
            END IF;
            IF NOT EXISTS (
                SELECT 1
                FROM pg_type t
                JOIN pg_namespace n ON n.oid = t.typnamespace
                WHERE t.typname = 'counter_offer_status_enum'
                  AND n.nspname = 'bidding'
            ) THEN
                CREATE TYPE bidding.counter_offer_status_enum AS ENUM ('PENDING', 'ACCEPTED', 'REJECTED', 'EXPIRED');
            END IF;
        END $$;
        """
    )
    session_status = postgresql.ENUM(
        "OPEN",
        "CLOSED",
        "EXPIRED",
        "PAUSED",
        name="bidding_session_status_enum",
        schema="bidding",
        create_type=False,
    )
    pricing_mode = postgresql.ENUM(
        "FIXED",
        "BID_BASED",
        "HYBRID",
        name="bidding_pricing_mode_enum",
        schema="bidding",
        create_type=False,
    )
    bid_status = postgresql.ENUM(
        "ACTIVE",
        "OUTBID",
        "WITHDRAWN",
        "ACCEPTED",
        "REJECTED",
        "EXPIRED",
        name="bid_status_enum",
        schema="bidding",
        create_type=False,
    )
    counter_offer_status = postgresql.ENUM(
        "PENDING",
        "ACCEPTED",
        "REJECTED",
        "EXPIRED",
        name="counter_offer_status_enum",
        schema="bidding",
        create_type=False,
    )
    op.create_table(
        "bidding_sessions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("service_request_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("status", session_status, nullable=False, server_default="OPEN"),
        sa.Column("opened_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("passenger_user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("pricing_mode", pricing_mode, nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("closed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("max_bids_allowed", sa.Integer(), nullable=True),
        sa.Column("min_driver_rating", sa.Numeric(3, 2), nullable=True),
        sa.Column("baseline_price", sa.Numeric(12, 2), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["service_request_id"], ["service_request.service_requests.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["passenger_user_id"], ["auth.users.id"], ondelete="SET NULL"),
        sa.CheckConstraint("max_bids_allowed IS NULL OR max_bids_allowed > 0", name="ck_bidding_sessions_max_bids_positive"),
        sa.UniqueConstraint("service_request_id", name="uq_bidding_sessions_service_request_id"),
        schema="bidding",
        if_not_exists=True,
    )
    op.execute(
        """
        ALTER TABLE IF EXISTS bidding.bidding_sessions
            ADD COLUMN IF NOT EXISTS passenger_user_id uuid,
            ADD COLUMN IF NOT EXISTS pricing_mode bidding.bidding_pricing_mode_enum;
        """
    )
    op.execute(
        """
        ALTER TABLE IF EXISTS bidding.bids
            ADD COLUMN IF NOT EXISTS service_request_id uuid,
            ADD COLUMN IF NOT EXISTS bidding_session_id uuid,
            ADD COLUMN IF NOT EXISTS driver_id uuid,
            ADD COLUMN IF NOT EXISTS driver_vehicle_id uuid,
            ADD COLUMN IF NOT EXISTS bid_amount numeric(12, 2),
            ADD COLUMN IF NOT EXISTS currency varchar(10) DEFAULT 'PKR',
            ADD COLUMN IF NOT EXISTS eta_minutes integer,
            ADD COLUMN IF NOT EXISTS message text,
            ADD COLUMN IF NOT EXISTS expires_at timestamp with time zone,
            ADD COLUMN IF NOT EXISTS old_status bidding.bid_status_enum;

        ALTER TABLE IF EXISTS bidding.bids
            ADD CONSTRAINT ck_bid_amount_positive CHECK (bid_amount IS NULL OR bid_amount > 0);
        """
    )
    op.execute(
        """
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1 FROM information_schema.tables
                WHERE table_schema = 'bidding' AND table_name = 'bids'
            ) THEN
                IF NOT EXISTS (
                    SELECT 1 FROM pg_constraint WHERE conname = 'fk_bids_service_request_id'
                ) THEN
                    ALTER TABLE bidding.bids
                        ADD CONSTRAINT fk_bids_service_request_id
                        FOREIGN KEY (service_request_id)
                        REFERENCES service_request.service_requests(id)
                        ON DELETE CASCADE;
                END IF;
                IF NOT EXISTS (
                    SELECT 1 FROM pg_constraint WHERE conname = 'fk_bids_bidding_session_id'
                ) THEN
                    ALTER TABLE bidding.bids
                        ADD CONSTRAINT fk_bids_bidding_session_id
                        FOREIGN KEY (bidding_session_id)
                        REFERENCES bidding.bidding_sessions(id)
                        ON DELETE CASCADE;
                END IF;
                IF NOT EXISTS (
                    SELECT 1 FROM pg_constraint WHERE conname = 'fk_bids_driver_id'
                ) THEN
                    ALTER TABLE bidding.bids
                        ADD CONSTRAINT fk_bids_driver_id
                        FOREIGN KEY (driver_id)
                        REFERENCES verification.drivers(id)
                        ON DELETE CASCADE;
                END IF;
                IF NOT EXISTS (
                    SELECT 1 FROM pg_constraint WHERE conname = 'fk_bids_driver_vehicle_id'
                ) THEN
                    ALTER TABLE bidding.bids
                        ADD CONSTRAINT fk_bids_driver_vehicle_id
                        FOREIGN KEY (driver_vehicle_id)
                        REFERENCES verification.driver_vehicles(id)
                        ON DELETE SET NULL;
                END IF;
            END IF;
        END $$;
        """
    )
    op.create_table(
        "bid_status_history",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("bid_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("old_status", bid_status, nullable=True),
        sa.Column("new_status", bid_status, nullable=False),
        sa.Column("changed_by_user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("changed_by_driver_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("reason_code", sa.String(50), nullable=True),
        sa.Column("reason_text", sa.Text(), nullable=True),
        sa.Column("changed_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["bid_id"], ["bidding.bids.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["changed_by_user_id"], ["auth.users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["changed_by_driver_id"], ["verification.drivers.id"], ondelete="SET NULL"),
        schema="bidding",
        if_not_exists=True,
    )
    op.create_table(
        "bid_counter_offers",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("bid_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("bidding_session_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("counter_price", sa.Numeric(12, 2), nullable=False),
        sa.Column("counter_eta_minutes", sa.Integer(), nullable=True),
        sa.Column("counter_by_user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("counter_by_driver_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("status", counter_offer_status, nullable=False, server_default="PENDING"),
        sa.Column("responded_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["bid_id"], ["bidding.bids.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["bidding_session_id"], ["bidding.bidding_sessions.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["counter_by_user_id"], ["auth.users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["counter_by_driver_id"], ["verification.drivers.id"], ondelete="SET NULL"),
        sa.CheckConstraint("counter_price > 0", name="ck_counter_price_positive"),
        schema="bidding",
        if_not_exists=True,
    )
    op.create_table(
        "bid_acceptances",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("service_request_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("bid_id", postgresql.UUID(as_uuid=True), nullable=False, unique=True),
        sa.Column("accepted_by_user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("final_price", sa.Numeric(12, 2), nullable=False),
        sa.Column("final_eta_minutes", sa.Integer(), nullable=True),
        sa.Column("accepted_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["service_request_id"], ["service_request.service_requests.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["bid_id"], ["bidding.bids.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["accepted_by_user_id"], ["auth.users.id"], ondelete="SET NULL"),
        schema="bidding",
        if_not_exists=True,
    )
    op.create_table(
        "bid_events",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("bid_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("event_type", sa.String(160), nullable=False),
        sa.Column("aggregate_id", sa.String(120), nullable=True),
        sa.Column("aggregate_type", sa.String(80), nullable=True),
        sa.Column("topic", sa.String(160), nullable=False, server_default="bidding-events"),
        sa.Column("payload", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("correlation_id", sa.String(120), nullable=True),
        sa.Column("idempotency_key", sa.String(180), nullable=True),
        sa.Column("processed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("error_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("last_error", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["bid_id"], ["bidding.bids.id"], ondelete="CASCADE"),
        schema="bidding",
        if_not_exists=True,
    )
    op.execute(
        """
        CREATE INDEX IF NOT EXISTS ix_bid_events_type_time
            ON bidding.bid_events (event_type, created_at);
        CREATE INDEX IF NOT EXISTS ix_bid_events_unprocessed
            ON bidding.bid_events (processed_at, error_count);
        """
    )
    op.execute(
        """
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1
                FROM information_schema.tables
                WHERE table_schema = 'bidding'
                  AND table_name = 'bidding_sessions'
            ) THEN
                IF NOT EXISTS (
                    SELECT 1
                    FROM pg_constraint
                    WHERE conname = 'fk_bidding_sessions_passenger_user_id'
                ) THEN
                    ALTER TABLE bidding.bidding_sessions
                        ADD CONSTRAINT fk_bidding_sessions_passenger_user_id
                        FOREIGN KEY (passenger_user_id)
                        REFERENCES auth.users(id)
                        ON DELETE SET NULL;
                END IF;
            END IF;
        END $$;
        """
    )
    op.execute(
        """
        CREATE INDEX IF NOT EXISTS ix_bidding_sessions_passenger_user_id
            ON bidding.bidding_sessions (passenger_user_id);
        CREATE INDEX IF NOT EXISTS ix_bidding_sessions_pricing_mode
            ON bidding.bidding_sessions (pricing_mode);
        """
    )
    op.execute(
        """
        ALTER TABLE IF EXISTS bidding.bid_counter_offers
            ADD COLUMN IF NOT EXISTS bidding_session_id uuid;
        """
    )
    op.execute(
        """
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1
                FROM information_schema.tables
                WHERE table_schema = 'bidding'
                  AND table_name = 'bid_counter_offers'
            ) THEN
                UPDATE bidding.bid_counter_offers co
                SET bidding_session_id = b.bidding_session_id
                FROM bidding.bids b
                WHERE co.bid_id = b.id
                  AND co.bidding_session_id IS NULL;
            END IF;
        END $$;
        """
    )
    op.execute(
        """
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1
                FROM information_schema.tables
                WHERE table_schema = 'bidding'
                  AND table_name = 'bid_counter_offers'
            ) THEN
                IF NOT EXISTS (
                    SELECT 1
                    FROM pg_constraint
                    WHERE conname = 'fk_bid_counter_offers_bidding_session_id'
                ) THEN
                    ALTER TABLE bidding.bid_counter_offers
                        ADD CONSTRAINT fk_bid_counter_offers_bidding_session_id
                        FOREIGN KEY (bidding_session_id)
                        REFERENCES bidding.bidding_sessions(id)
                        ON DELETE CASCADE;
                END IF;
            END IF;
        END $$;
        """
    )
    op.execute(
        """
        ALTER TABLE IF EXISTS bidding.bid_counter_offers
            ALTER COLUMN bid_id DROP NOT NULL,
            ALTER COLUMN bidding_session_id SET NOT NULL;
        """
    )
    op.execute(
        """
        CREATE INDEX IF NOT EXISTS ix_bid_counter_offers_bidding_session_id
            ON bidding.bid_counter_offers (bidding_session_id);
        """
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS bidding.ix_bid_counter_offers_bidding_session_id;")
    op.execute(
        """
        ALTER TABLE IF EXISTS bidding.bid_counter_offers
            ALTER COLUMN bid_id SET NOT NULL,
            DROP CONSTRAINT IF EXISTS fk_bid_counter_offers_bidding_session_id,
            DROP COLUMN IF EXISTS bidding_session_id;
        """
    )
    op.execute("DROP INDEX IF EXISTS bidding.ix_bidding_sessions_pricing_mode;")
    op.execute("DROP INDEX IF EXISTS bidding.ix_bidding_sessions_passenger_user_id;")
    op.execute(
        """
        ALTER TABLE IF EXISTS bidding.bidding_sessions
            DROP CONSTRAINT IF EXISTS fk_bidding_sessions_passenger_user_id,
            DROP COLUMN IF EXISTS pricing_mode,
            DROP COLUMN IF EXISTS passenger_user_id;
        """
    )
    op.execute("DROP TYPE IF EXISTS bidding.bidding_pricing_mode_enum;")
