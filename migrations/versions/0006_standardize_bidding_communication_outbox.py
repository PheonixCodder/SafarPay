"""Standardize bidding and communication outbox contracts.

Revision ID: 0006_standardize_bidding_communication_outbox
Revises: 0005_outbox_inbox_contracts
Create Date: 2026-05-05
"""
from __future__ import annotations

from alembic import op

revision = "0006_standardize_bidding_communication_outbox"
down_revision = "0005_outbox_inbox_contracts"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        CREATE OR REPLACE FUNCTION public.safarpay_try_jsonb(raw text)
        RETURNS jsonb
        LANGUAGE plpgsql
        AS $$
        BEGIN
            IF raw IS NULL OR btrim(raw) = '' THEN
                RETURN '{}'::jsonb;
            END IF;
            RETURN raw::jsonb;
        EXCEPTION WHEN others THEN
            RETURN '{}'::jsonb;
        END;
        $$;
        """
    )
    op.execute(
        """
        ALTER TABLE IF EXISTS bidding.bid_events
            ADD COLUMN IF NOT EXISTS aggregate_id varchar(120),
            ADD COLUMN IF NOT EXISTS aggregate_type varchar(80),
            ADD COLUMN IF NOT EXISTS topic varchar(160) NOT NULL DEFAULT 'bidding-events',
            ADD COLUMN IF NOT EXISTS correlation_id varchar(120),
            ADD COLUMN IF NOT EXISTS idempotency_key varchar(180),
            ADD COLUMN IF NOT EXISTS updated_at timestamptz NOT NULL DEFAULT now(),
            ADD COLUMN IF NOT EXISTS last_error text;

        ALTER TABLE IF EXISTS bidding.bid_events
            ALTER COLUMN event_type TYPE varchar(160) USING event_type::text,
            ALTER COLUMN payload TYPE jsonb USING public.safarpay_try_jsonb(payload);

        UPDATE bidding.bid_events
        SET event_type = CASE event_type
            WHEN 'BID_PLACED' THEN 'bid.placed'
            WHEN 'BID_UPDATED' THEN 'bid.updated'
            WHEN 'BID_WITHDRAWN' THEN 'bid.withdrawn'
            WHEN 'BID_ACCEPTED' THEN 'bid.accepted'
            WHEN 'BID_REJECTED' THEN 'bid.rejected'
            WHEN 'AUTO_ACCEPT_REQUESTED' THEN 'bid.auto_accept_requested'
            WHEN 'COUNTER_OFFER_CREATED' THEN 'bid.counter_offer.created'
            WHEN 'COUNTER_OFFER_RESPONDED' THEN 'bid.counter_offer.responded'
            ELSE event_type
        END
        WHERE event_type IS NOT NULL;

        UPDATE bidding.bid_events
        SET aggregate_id = COALESCE(aggregate_id, bid_id::text),
            aggregate_type = COALESCE(aggregate_type, 'bid'),
            topic = COALESCE(topic, 'bidding-events'),
            payload = COALESCE(payload, '{}'::jsonb);

        ALTER TABLE IF EXISTS bidding.bid_events
            ALTER COLUMN payload SET NOT NULL,
            ALTER COLUMN payload SET DEFAULT '{}'::jsonb,
            ALTER COLUMN event_type SET NOT NULL,
            ALTER COLUMN topic SET NOT NULL,
            ALTER COLUMN error_count SET DEFAULT 0;

        CREATE UNIQUE INDEX IF NOT EXISTS ix_bid_events_idempotency_key
            ON bidding.bid_events (idempotency_key)
            WHERE idempotency_key IS NOT NULL;
        CREATE INDEX IF NOT EXISTS ix_bid_events_aggregate
            ON bidding.bid_events (aggregate_id);
        CREATE INDEX IF NOT EXISTS ix_bid_events_pending_standard
            ON bidding.bid_events (processed_at, error_count, created_at);
        """
    )
    op.execute(
        """
        ALTER TABLE IF EXISTS communication.communication_events
            ADD COLUMN IF NOT EXISTS aggregate_type varchar(80),
            ADD COLUMN IF NOT EXISTS topic varchar(160) NOT NULL DEFAULT 'communication-events',
            ADD COLUMN IF NOT EXISTS correlation_id varchar(120),
            ADD COLUMN IF NOT EXISTS idempotency_key varchar(180),
            ADD COLUMN IF NOT EXISTS updated_at timestamptz NOT NULL DEFAULT now(),
            ADD COLUMN IF NOT EXISTS last_error text;

        ALTER TABLE IF EXISTS communication.communication_events
            ALTER COLUMN event_type TYPE varchar(160) USING event_type::text;

        UPDATE communication.communication_events
        SET event_type = CASE event_type
            WHEN 'CONVERSATION_OPENED' THEN 'communication.conversation.opened'
            WHEN 'CONVERSATION_CLOSED' THEN 'communication.conversation.closed'
            WHEN 'MESSAGE_SENT' THEN 'communication.message.sent'
            WHEN 'MEDIA_MESSAGE_SENT' THEN 'communication.media_message.sent'
            WHEN 'CALL_STARTED' THEN 'communication.call.started'
            WHEN 'CALL_UPDATED' THEN 'communication.call.updated'
            WHEN 'communication.conversation_opened' THEN 'communication.conversation.opened'
            WHEN 'communication.conversation_closed' THEN 'communication.conversation.closed'
            WHEN 'communication.message_sent' THEN 'communication.message.sent'
            WHEN 'communication.media_message_sent' THEN 'communication.media_message.sent'
            WHEN 'communication.call_started' THEN 'communication.call.started'
            WHEN 'communication.call_updated' THEN 'communication.call.updated'
            ELSE event_type
        END
        WHERE event_type IS NOT NULL;

        UPDATE communication.communication_events
        SET aggregate_type = COALESCE(aggregate_type, 'communication'),
            topic = COALESCE(topic, 'communication-events'),
            payload = COALESCE(payload, '{}'::jsonb);

        ALTER TABLE IF EXISTS communication.communication_events
            ALTER COLUMN event_type SET NOT NULL,
            ALTER COLUMN topic SET NOT NULL,
            ALTER COLUMN payload SET NOT NULL,
            ALTER COLUMN error_count SET DEFAULT 0;

        CREATE UNIQUE INDEX IF NOT EXISTS ix_communication_events_idempotency_key
            ON communication.communication_events (idempotency_key)
            WHERE idempotency_key IS NOT NULL;
        CREATE INDEX IF NOT EXISTS ix_communication_events_type
            ON communication.communication_events (event_type);
        CREATE INDEX IF NOT EXISTS ix_communication_events_pending_standard
            ON communication.communication_events (processed_at, error_count, created_at);
        """
    )
    op.execute("DROP FUNCTION IF EXISTS public.safarpay_try_jsonb(text);")


def downgrade() -> None:
    op.execute(
        """
        DO $$
        BEGIN
            IF to_regclass('bidding.bid_events') IS NOT NULL THEN
                UPDATE bidding.bid_events
                SET event_type = CASE event_type
                    WHEN 'bid.placed' THEN 'BID_PLACED'
                    WHEN 'bid.updated' THEN 'BID_UPDATED'
                    WHEN 'bid.withdrawn' THEN 'BID_WITHDRAWN'
                    WHEN 'bid.accepted' THEN 'BID_ACCEPTED'
                    WHEN 'bid.rejected' THEN 'BID_REJECTED'
                    WHEN 'bid.auto_accept_requested' THEN 'AUTO_ACCEPT_REQUESTED'
                    WHEN 'bid.counter_offer.created' THEN 'COUNTER_OFFER_CREATED'
                    WHEN 'bid.counter_offer.responded' THEN 'COUNTER_OFFER_RESPONDED'
                    ELSE event_type
                END
                WHERE event_type IS NOT NULL;

                ALTER TABLE bidding.bid_events
                    ALTER COLUMN payload DROP DEFAULT,
                    ALTER COLUMN payload TYPE text USING payload::text;
            END IF;
        END $$;

        DROP INDEX IF EXISTS bidding.ix_bid_events_pending_standard;
        DROP INDEX IF EXISTS bidding.ix_bid_events_aggregate;
        DROP INDEX IF EXISTS bidding.ix_bid_events_idempotency_key;
        ALTER TABLE IF EXISTS bidding.bid_events
            DROP COLUMN IF EXISTS last_error,
            DROP COLUMN IF EXISTS updated_at,
            DROP COLUMN IF EXISTS idempotency_key,
            DROP COLUMN IF EXISTS correlation_id,
            DROP COLUMN IF EXISTS topic,
            DROP COLUMN IF EXISTS aggregate_type,
            DROP COLUMN IF EXISTS aggregate_id;
        """
    )
    op.execute(
        """
        DO $$
        BEGIN
            IF to_regclass('communication.communication_events') IS NOT NULL THEN
                UPDATE communication.communication_events
                SET event_type = CASE event_type
                    WHEN 'communication.conversation.opened' THEN 'CONVERSATION_OPENED'
                    WHEN 'communication.conversation.closed' THEN 'CONVERSATION_CLOSED'
                    WHEN 'communication.message.sent' THEN 'MESSAGE_SENT'
                    WHEN 'communication.media_message.sent' THEN 'MEDIA_MESSAGE_SENT'
                    WHEN 'communication.call.started' THEN 'CALL_STARTED'
                    WHEN 'communication.call.updated' THEN 'CALL_UPDATED'
                    ELSE event_type
                END
                WHERE event_type IS NOT NULL;
            END IF;
        END $$;

        DROP INDEX IF EXISTS communication.ix_communication_events_pending_standard;
        DROP INDEX IF EXISTS communication.ix_communication_events_type;
        DROP INDEX IF EXISTS communication.ix_communication_events_idempotency_key;
        ALTER TABLE IF EXISTS communication.communication_events
            DROP COLUMN IF EXISTS last_error,
            DROP COLUMN IF EXISTS updated_at,
            DROP COLUMN IF EXISTS idempotency_key,
            DROP COLUMN IF EXISTS correlation_id,
            DROP COLUMN IF EXISTS topic,
            DROP COLUMN IF EXISTS aggregate_type;
        """
    )
