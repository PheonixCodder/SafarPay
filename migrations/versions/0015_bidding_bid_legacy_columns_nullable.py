"""Relax legacy bidding bid columns for ride-based bids.

Revision ID: 0015_bidding_bid_legacy_columns_nullable
Revises: 0014_location_places
Create Date: 2026-05-24
"""
from __future__ import annotations

from alembic import op


revision = "0015_bidding_bid_legacy_columns_nullable"
down_revision = "0014_location_places"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        ALTER TABLE IF EXISTS bidding.bids
            ALTER COLUMN item_id DROP NOT NULL,
            ALTER COLUMN bidder_id DROP NOT NULL,
            ALTER COLUMN amount DROP NOT NULL,
            ALTER COLUMN placed_at DROP NOT NULL,
            ALTER COLUMN created_at SET DEFAULT now(),
            ALTER COLUMN updated_at SET DEFAULT now();
        """
    )


def downgrade() -> None:
    op.execute(
        """
        UPDATE bidding.bids
        SET
            item_id = COALESCE(item_id, service_request_id::text, id::text),
            bidder_id = COALESCE(bidder_id, driver_id),
            amount = COALESCE(amount, bid_amount::double precision),
            placed_at = COALESCE(placed_at, created_at::timestamp, now()::timestamp)
        WHERE item_id IS NULL
           OR bidder_id IS NULL
           OR amount IS NULL
           OR placed_at IS NULL;

        ALTER TABLE IF EXISTS bidding.bids
            ALTER COLUMN item_id SET NOT NULL,
            ALTER COLUMN bidder_id SET NOT NULL,
            ALTER COLUMN amount SET NOT NULL,
            ALTER COLUMN placed_at SET NOT NULL,
            ALTER COLUMN created_at DROP DEFAULT,
            ALTER COLUMN updated_at DROP DEFAULT;
        """
    )
