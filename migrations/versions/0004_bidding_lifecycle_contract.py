"""Align bidding lifecycle contract.

Revision ID: 0004_bidding_lifecycle_contract
Revises: 0003_communication_service
Create Date: 2026-05-04
"""
from __future__ import annotations

from alembic import op


revision = "0004_bidding_lifecycle_contract"
down_revision = "0003_communication_service"
branch_labels = None
depends_on = None


def upgrade() -> None:
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
        ALTER TABLE IF EXISTS bidding.bidding_sessions
            ADD COLUMN IF NOT EXISTS passenger_user_id uuid,
            ADD COLUMN IF NOT EXISTS pricing_mode bidding.bidding_pricing_mode_enum;
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
