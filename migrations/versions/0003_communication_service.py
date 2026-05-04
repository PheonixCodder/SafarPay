"""communication service

Revision ID: 0003_communication_service
Revises: 0002_geospatial_zones
Create Date: 2026-05-03 00:00:00.000000
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0003_communication_service"
down_revision: Union[str, None] = "0002_geospatial_zones"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("CREATE SCHEMA IF NOT EXISTS communication")

    conversation_status = sa.Enum("ACTIVE", "CLOSED", name="conversation_status_enum", schema="communication")
    participant_role = sa.Enum("PASSENGER", "DRIVER", name="participant_role_enum", schema="communication")
    message_type = sa.Enum("TEXT", "IMAGE", "VOICE_NOTE", "SYSTEM", name="message_type_enum", schema="communication")
    message_status = sa.Enum("SENT", "DELIVERED", "READ", "DELETED", name="message_status_enum", schema="communication")
    media_type = sa.Enum("IMAGE", "VOICE_NOTE", name="media_type_enum", schema="communication")
    media_upload_status = sa.Enum("PENDING", "UPLOADED", name="media_upload_status_enum", schema="communication")
    call_status = sa.Enum("RINGING", "ACCEPTED", "ENDED", "MISSED", "REJECTED", "FAILED", name="call_status_enum", schema="communication")
    signal_type = sa.Enum("OFFER", "ANSWER", "ICE_CANDIDATE", "CALL_CONTROL", name="signal_type_enum", schema="communication")
    communication_event_type = sa.Enum(
        "CONVERSATION_OPENED",
        "CONVERSATION_CLOSED",
        "MESSAGE_SENT",
        "MEDIA_MESSAGE_SENT",
        "CALL_STARTED",
        "CALL_UPDATED",
        name="communication_event_type_enum",
        schema="communication",
    )

    for enum in [
        conversation_status,
        participant_role,
        message_type,
        message_status,
        media_type,
        media_upload_status,
        call_status,
        signal_type,
        communication_event_type,
    ]:
        enum.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "conversations",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("service_request_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("passenger_user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("driver_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("driver_user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("status", conversation_status, nullable=False),
        sa.Column("opened_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("closed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["service_request_id"], ["service_request.service_requests.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["passenger_user_id"], ["auth.users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["driver_id"], ["verification.drivers.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["driver_user_id"], ["auth.users.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("service_request_id", name="uq_conversation_service_request"),
        schema="communication",
    )
    op.create_index("ix_conversations_passenger_status", "conversations", ["passenger_user_id", "status"], schema="communication")
    op.create_index("ix_conversations_driver_status", "conversations", ["driver_id", "status"], schema="communication")

    op.create_table(
        "conversation_participants",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("conversation_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("role", participant_role, nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("driver_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("joined_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["conversation_id"], ["communication.conversations.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["auth.users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["driver_id"], ["verification.drivers.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("conversation_id", "role", name="uq_conversation_role"),
        schema="communication",
    )
    op.create_index("ix_conversation_participants_user", "conversation_participants", ["user_id"], schema="communication")
    op.create_index("ix_conversation_participants_driver", "conversation_participants", ["driver_id"], schema="communication")

    op.create_table(
        "messages",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("conversation_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("sender_participant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("message_type", message_type, nullable=False),
        sa.Column("status", message_status, nullable=False),
        sa.Column("body", sa.Text(), nullable=True),
        sa.Column("reply_to_message_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("sent_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("delivered_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("read_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["conversation_id"], ["communication.conversations.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["sender_participant_id"], ["communication.conversation_participants.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["reply_to_message_id"], ["communication.messages.id"], ondelete="SET NULL"),
        schema="communication",
    )
    op.create_index("ix_messages_conversation_sent", "messages", ["conversation_id", "sent_at"], schema="communication")

    op.create_table(
        "message_media",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("message_id", postgresql.UUID(as_uuid=True), nullable=True, unique=True),
        sa.Column("conversation_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("uploader_participant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("media_type", media_type, nullable=False),
        sa.Column("file_key", sa.String(500), nullable=False, unique=True),
        sa.Column("file_name", sa.String(255), nullable=True),
        sa.Column("mime_type", sa.String(120), nullable=False),
        sa.Column("file_size_bytes", sa.Integer(), nullable=True),
        sa.Column("duration_seconds", sa.Numeric(10, 2), nullable=True),
        sa.Column("checksum_sha256", sa.String(64), nullable=True),
        sa.Column("upload_status", media_upload_status, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["message_id"], ["communication.messages.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["conversation_id"], ["communication.conversations.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["uploader_participant_id"], ["communication.conversation_participants.id"], ondelete="CASCADE"),
        sa.CheckConstraint("file_size_bytes IS NULL OR file_size_bytes >= 0", name="ck_message_media_file_size_non_negative"),
        sa.CheckConstraint("duration_seconds IS NULL OR duration_seconds >= 0", name="ck_message_media_duration_non_negative"),
        schema="communication",
    )
    op.create_index("ix_message_media_conversation", "message_media", ["conversation_id"], schema="communication")

    op.create_table(
        "voice_calls",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("conversation_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("caller_participant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("callee_participant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("status", call_status, nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("accepted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("ended_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("end_reason", sa.String(120), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["conversation_id"], ["communication.conversations.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["caller_participant_id"], ["communication.conversation_participants.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["callee_participant_id"], ["communication.conversation_participants.id"], ondelete="CASCADE"),
        schema="communication",
    )
    op.create_index("ix_voice_calls_conversation_started", "voice_calls", ["conversation_id", "started_at"], schema="communication")

    op.create_table(
        "call_signaling_events",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("call_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("sender_participant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("signal_type", signal_type, nullable=False),
        sa.Column("payload", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["call_id"], ["communication.voice_calls.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["sender_participant_id"], ["communication.conversation_participants.id"], ondelete="CASCADE"),
        schema="communication",
    )
    op.create_index("ix_call_signaling_call_created", "call_signaling_events", ["call_id", "created_at"], schema="communication")

    op.create_table(
        "communication_events",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("event_type", communication_event_type, nullable=False),
        sa.Column("aggregate_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("payload", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("processed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("error_count", sa.Integer(), nullable=False, server_default="0"),
        schema="communication",
    )
    op.create_index("ix_communication_events_pending", "communication_events", ["processed_at", "created_at"], schema="communication")


def downgrade() -> None:
    op.drop_table("communication_events", schema="communication")
    op.drop_table("call_signaling_events", schema="communication")
    op.drop_table("voice_calls", schema="communication")
    op.drop_table("message_media", schema="communication")
    op.drop_table("messages", schema="communication")
    op.drop_table("conversation_participants", schema="communication")
    op.drop_table("conversations", schema="communication")

    for name in [
        "communication_event_type_enum",
        "signal_type_enum",
        "call_status_enum",
        "media_upload_status_enum",
        "media_type_enum",
        "message_status_enum",
        "message_type_enum",
        "participant_role_enum",
        "conversation_status_enum",
    ]:
        op.execute(f"DROP TYPE IF EXISTS communication.{name}")
