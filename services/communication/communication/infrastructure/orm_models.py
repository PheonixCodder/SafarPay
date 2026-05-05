"""Communication ORM models."""
from __future__ import annotations

import enum
import uuid
from datetime import datetime

from sp.infrastructure.db.base import Base, TimestampMixin
from sqlalchemy import (
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
from sqlalchemy.orm import Mapped, mapped_column, relationship


class ConversationStatus(enum.Enum):
    ACTIVE = "ACTIVE"
    CLOSED = "CLOSED"


class ParticipantRole(enum.Enum):
    PASSENGER = "PASSENGER"
    DRIVER = "DRIVER"


class MessageType(enum.Enum):
    TEXT = "TEXT"
    IMAGE = "IMAGE"
    VOICE_NOTE = "VOICE_NOTE"
    SYSTEM = "SYSTEM"


class MessageStatus(enum.Enum):
    SENT = "SENT"
    DELIVERED = "DELIVERED"
    READ = "READ"
    DELETED = "DELETED"


class MediaType(enum.Enum):
    IMAGE = "IMAGE"
    VOICE_NOTE = "VOICE_NOTE"


class MediaUploadStatus(enum.Enum):
    PENDING = "PENDING"
    UPLOADED = "UPLOADED"


class CallStatus(enum.Enum):
    RINGING = "RINGING"
    ACCEPTED = "ACCEPTED"
    ENDED = "ENDED"
    MISSED = "MISSED"
    REJECTED = "REJECTED"
    FAILED = "FAILED"


class SignalType(enum.Enum):
    OFFER = "OFFER"
    ANSWER = "ANSWER"
    ICE_CANDIDATE = "ICE_CANDIDATE"
    CALL_CONTROL = "CALL_CONTROL"


class CommunicationEventType(enum.Enum):
    CONVERSATION_OPENED = "CONVERSATION_OPENED"
    CONVERSATION_CLOSED = "CONVERSATION_CLOSED"
    MESSAGE_SENT = "MESSAGE_SENT"
    MEDIA_MESSAGE_SENT = "MEDIA_MESSAGE_SENT"
    CALL_STARTED = "CALL_STARTED"
    CALL_UPDATED = "CALL_UPDATED"


class ConversationORM(Base, TimestampMixin):
    __tablename__ = "conversations"
    __table_args__ = (
        UniqueConstraint("service_request_id", name="uq_conversation_service_request"),
        Index("ix_conversations_passenger_status", "passenger_user_id", "status"),
        Index("ix_conversations_driver_status", "driver_id", "status"),
        {"schema": "communication"},
    )

    id: Mapped[uuid.UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    service_request_id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True),
        ForeignKey("service_request.service_requests.id", ondelete="CASCADE"),
        nullable=False,
    )
    passenger_user_id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True),
        ForeignKey("auth.users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    driver_id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True),
        ForeignKey("verification.drivers.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    driver_user_id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True),
        ForeignKey("auth.users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    status: Mapped[ConversationStatus] = mapped_column(
        SQLEnum(ConversationStatus, name="conversation_status_enum", schema="communication"),
        default=ConversationStatus.ACTIVE,
        nullable=False,
        index=True,
    )
    opened_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    closed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    participants: Mapped[list[ConversationParticipantORM]] = relationship(
        back_populates="conversation", cascade="all, delete-orphan"
    )
    messages: Mapped[list[MessageORM]] = relationship(back_populates="conversation")


class ConversationParticipantORM(Base, TimestampMixin):
    __tablename__ = "conversation_participants"
    __table_args__ = (
        UniqueConstraint("conversation_id", "role", name="uq_conversation_role"),
        Index("ix_conversation_participants_user", "user_id"),
        Index("ix_conversation_participants_driver", "driver_id"),
        {"schema": "communication"},
    )

    id: Mapped[uuid.UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    conversation_id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True),
        ForeignKey("communication.conversations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    role: Mapped[ParticipantRole] = mapped_column(
        SQLEnum(ParticipantRole, name="participant_role_enum", schema="communication"),
        nullable=False,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True),
        ForeignKey("auth.users.id", ondelete="CASCADE"),
        nullable=False,
    )
    driver_id: Mapped[uuid.UUID | None] = mapped_column(
        PgUUID(as_uuid=True),
        ForeignKey("verification.drivers.id", ondelete="CASCADE"),
        nullable=True,
    )
    joined_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    conversation: Mapped[ConversationORM] = relationship(back_populates="participants")


class MessageORM(Base):
    __tablename__ = "messages"
    __table_args__ = (
        Index("ix_messages_conversation_sent", "conversation_id", "sent_at"),
        {"schema": "communication"},
    )

    id: Mapped[uuid.UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    conversation_id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True),
        ForeignKey("communication.conversations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    sender_participant_id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True),
        ForeignKey("communication.conversation_participants.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    message_type: Mapped[MessageType] = mapped_column(
        SQLEnum(MessageType, name="message_type_enum", schema="communication"),
        nullable=False,
    )
    status: Mapped[MessageStatus] = mapped_column(
        SQLEnum(MessageStatus, name="message_status_enum", schema="communication"),
        default=MessageStatus.SENT,
        nullable=False,
    )
    body: Mapped[str | None] = mapped_column(Text, nullable=True)
    reply_to_message_id: Mapped[uuid.UUID | None] = mapped_column(
        PgUUID(as_uuid=True),
        ForeignKey("communication.messages.id", ondelete="SET NULL"),
        nullable=True,
    )
    sent_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    delivered_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    read_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    conversation: Mapped[ConversationORM] = relationship(back_populates="messages")
    media: Mapped[MessageMediaORM | None] = relationship(back_populates="message", uselist=False)


class MessageMediaORM(Base, TimestampMixin):
    __tablename__ = "message_media"
    __table_args__ = (
        Index("ix_message_media_conversation", "conversation_id"),
        CheckConstraint("file_size_bytes IS NULL OR file_size_bytes >= 0", name="ck_message_media_file_size_non_negative"),
        CheckConstraint("duration_seconds IS NULL OR duration_seconds >= 0", name="ck_message_media_duration_non_negative"),
        {"schema": "communication"},
    )

    id: Mapped[uuid.UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    message_id: Mapped[uuid.UUID | None] = mapped_column(
        PgUUID(as_uuid=True),
        ForeignKey("communication.messages.id", ondelete="CASCADE"),
        nullable=True,
        unique=True,
    )
    conversation_id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True),
        ForeignKey("communication.conversations.id", ondelete="CASCADE"),
        nullable=False,
    )
    uploader_participant_id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True),
        ForeignKey("communication.conversation_participants.id", ondelete="CASCADE"),
        nullable=False,
    )
    media_type: Mapped[MediaType] = mapped_column(
        SQLEnum(MediaType, name="media_type_enum", schema="communication"),
        nullable=False,
    )
    file_key: Mapped[str] = mapped_column(String(500), nullable=False, unique=True)
    file_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    mime_type: Mapped[str] = mapped_column(String(120), nullable=False)
    file_size_bytes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    duration_seconds: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True)
    checksum_sha256: Mapped[str | None] = mapped_column(String(64), nullable=True)
    upload_status: Mapped[MediaUploadStatus] = mapped_column(
        SQLEnum(MediaUploadStatus, name="media_upload_status_enum", schema="communication"),
        default=MediaUploadStatus.PENDING,
        nullable=False,
    )

    message: Mapped[MessageORM | None] = relationship(back_populates="media")


class VoiceCallORM(Base, TimestampMixin):
    __tablename__ = "voice_calls"
    __table_args__ = (
        Index("ix_voice_calls_conversation_started", "conversation_id", "started_at"),
        {"schema": "communication"},
    )

    id: Mapped[uuid.UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    conversation_id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True),
        ForeignKey("communication.conversations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    caller_participant_id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True),
        ForeignKey("communication.conversation_participants.id", ondelete="CASCADE"),
        nullable=False,
    )
    callee_participant_id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True),
        ForeignKey("communication.conversation_participants.id", ondelete="CASCADE"),
        nullable=False,
    )
    status: Mapped[CallStatus] = mapped_column(
        SQLEnum(CallStatus, name="call_status_enum", schema="communication"),
        default=CallStatus.RINGING,
        nullable=False,
        index=True,
    )
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    accepted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    ended_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    end_reason: Mapped[str | None] = mapped_column(String(120), nullable=True)


class CallSignalingEventORM(Base):
    __tablename__ = "call_signaling_events"
    __table_args__ = (
        Index("ix_call_signaling_call_created", "call_id", "created_at"),
        {"schema": "communication"},
    )

    id: Mapped[uuid.UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    call_id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True),
        ForeignKey("communication.voice_calls.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    sender_participant_id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True),
        ForeignKey("communication.conversation_participants.id", ondelete="CASCADE"),
        nullable=False,
    )
    signal_type: Mapped[SignalType] = mapped_column(
        SQLEnum(SignalType, name="signal_type_enum", schema="communication"),
        nullable=False,
    )
    payload: Mapped[dict] = mapped_column(JSONB, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class CommunicationEventORM(Base):
    __tablename__ = "communication_events"
    __table_args__ = (
        Index("ix_communication_events_pending", "processed_at", "created_at"),
        {"schema": "communication"},
    )

    id: Mapped[uuid.UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    event_type: Mapped[CommunicationEventType] = mapped_column(
        SQLEnum(CommunicationEventType, name="communication_event_type_enum", schema="communication"),
        nullable=False,
    )
    aggregate_id: Mapped[uuid.UUID] = mapped_column(PgUUID(as_uuid=True), nullable=False, index=True)
    payload: Mapped[dict] = mapped_column(JSONB, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    processed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    error_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
