"""PR 18 reliability and contract fixes.

Revision ID: 0007_pr18_reliability_contract_fixes
Revises: 0006_standardize_bidding_communication_outbox
Create Date: 2026-05-05 00:00:00.000000
"""
from __future__ import annotations

from collections.abc import Sequence

from alembic import op

revision: str = "0007_pr18_reliability_contract_fixes"
down_revision: str | None = "0006_standardize_bidding_communication_outbox"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute(
        """
        DO $$
        DECLARE
            fk_name text;
        BEGIN
            IF to_regclass('bidding.bid_counter_offers') IS NOT NULL THEN
                SELECT conname INTO fk_name
                FROM pg_constraint
                WHERE conrelid = 'bidding.bid_counter_offers'::regclass
                  AND contype = 'f'
                  AND conkey = ARRAY[
                      (
                          SELECT attnum
                          FROM pg_attribute
                          WHERE attrelid = 'bidding.bid_counter_offers'::regclass
                            AND attname = 'bid_id'
                      )
                  ]::smallint[]
                LIMIT 1;

                IF fk_name IS NOT NULL THEN
                    EXECUTE format(
                        'ALTER TABLE bidding.bid_counter_offers DROP CONSTRAINT %I',
                        fk_name
                    );
                END IF;

                ALTER TABLE bidding.bid_counter_offers
                    ADD CONSTRAINT fk_bid_counter_offers_bid_id
                    FOREIGN KEY (bid_id)
                    REFERENCES bidding.bids(id)
                    ON DELETE SET NULL;
            END IF;
        END $$;
        """
    )
    op.execute(
        """
        ALTER TABLE IF EXISTS bidding.inbox_messages
            ALTER COLUMN source_offset TYPE bigint;
        ALTER TABLE IF EXISTS communication.inbox_messages
            ALTER COLUMN source_offset TYPE bigint;
        """
    )
    op.execute(
        """
        DO $$
        BEGIN
            IF to_regclass('auth.outbox_events') IS NOT NULL THEN
                DROP INDEX IF EXISTS auth.ix_auth_outbox_pending;
                CREATE INDEX IF NOT EXISTS ix_auth_outbox_pending
                    ON auth.outbox_events (processed_at, created_at)
                    WHERE processed_at IS NULL AND error_count < 5;
            END IF;

            IF to_regclass('communication.inbox_messages') IS NOT NULL THEN
                CREATE INDEX IF NOT EXISTS ix_communication_inbox_type
                    ON communication.inbox_messages (event_type);
                CREATE INDEX IF NOT EXISTS ix_communication_inbox_aggregate
                    ON communication.inbox_messages (aggregate_id);
            END IF;
        END $$;
        """
    )


def downgrade() -> None:
    op.execute(
        """
        DO $$
        BEGIN
            IF to_regclass('bidding.bid_counter_offers') IS NOT NULL THEN
                ALTER TABLE bidding.bid_counter_offers
                    DROP CONSTRAINT IF EXISTS fk_bid_counter_offers_bid_id;
                ALTER TABLE bidding.bid_counter_offers
                    ADD CONSTRAINT fk_bid_counter_offers_bid_id
                    FOREIGN KEY (bid_id)
                    REFERENCES bidding.bids(id)
                    ON DELETE CASCADE;
            END IF;
        END $$;
        """
    )
    op.execute(
        """
        DO $$
        BEGIN
            IF to_regnamespace('communication') IS NOT NULL THEN
                DROP INDEX IF EXISTS communication.ix_communication_inbox_type;
                DROP INDEX IF EXISTS communication.ix_communication_inbox_aggregate;
            END IF;
        END $$;
        """
    )
