"""Communication domain models - pure Python, no framework imports."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from uuid import UUID, uuid4

from .exceptions import ConversationClosedError, InvalidCallTransitionError


class ConversationStatus(str, Enum):
    ACTIVE = "ACTIVE"
    CLOSED = "CLOSED"


class ParticipantRole(str, Enum):
    PASSENGER = "PASSENGER"
    DRIVER = "DRIVER"


class MessageType(str, Enum):
    TEXT = "TEXT"
    IMAGE = "IMAGE"
    VOICE_NOTE = "VOICE_NOTE"
    SYSTEM = "SYSTEM"


class MessageStatus(str, Enum):
    SENT = "SENT"
    DELIVERED = "DELIVERED"
    READ = "READ"
    DELETED = "DELETED"


class MediaType(str, Enum):
    IMAGE = "IMAGE"
    VOICE_NOTE = "VOICE_NOTE"


class MediaUploadStatus(str, Enum):
    PENDING = "PENDING"
    UPLOADED = "UPLOADED"


class CallStatus(str, Enum):
    RINGING = "RINGING"
    ACCEPTED = "ACCEPTED"
    ENDED = "ENDED"
    MISSED = "MISSED"
    REJECTED = "REJECTED"
    FAILED = "FAILED"


class SignalType(str, Enum):
    OFFER = "OFFER"
    ANSWER = "ANSWER"
    ICE_CANDIDATE = "ICE_CANDIDATE"
    CALL_CONTROL = "CALL_CONTROL"


@dataclass
class Conversation:
    id: UUID
    service_request_id: UUID
    passenger_user_id: UUID
    driver_id: UUID
    driver_user_id: UUID
    status: ConversationStatus = ConversationStatus.ACTIVE
    opened_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    closed_at: datetime | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    @classmethod
    def open(
        cls,
        service_request_id: UUID,
        passenger_user_id: UUID,
        driver_id: UUID,
        driver_user_id: UUID,
    ) -> Conversation:
        return cls(
            id=uuid4(),
            service_request_id=service_request_id,
            passenger_user_id=passenger_user_id,
            driver_id=driver_id,
            driver_user_id=driver_user_id,
        )

    def close(self) -> None:
        if self.status == ConversationStatus.CLOSED:
            return
        self.status = ConversationStatus.CLOSED
        self.closed_at = datetime.now(timezone.utc)

    def ensure_active(self) -> None:
        if self.status != ConversationStatus.ACTIVE:
            raise ConversationClosedError("Conversation is closed.")


@dataclass
class ConversationParticipant:
    id: UUID
    conversation_id: UUID
    role: ParticipantRole
    user_id: UUID
    driver_id: UUID | None = None
    joined_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @classmethod
    def passenger(cls, conversation_id: UUID, user_id: UUID) -> ConversationParticipant:
        return cls(id=uuid4(), conversation_id=conversation_id, role=ParticipantRole.PASSENGER, user_id=user_id)

    @classmethod
    def driver(cls, conversation_id: UUID, user_id: UUID, driver_id: UUID) -> ConversationParticipant:
        return cls(id=uuid4(), conversation_id=conversation_id, role=ParticipantRole.DRIVER, user_id=user_id, driver_id=driver_id)


@dataclass
class Message:
    id: UUID
    conversation_id: UUID
    sender_participant_id: UUID
    message_type: MessageType
    status: MessageStatus = MessageStatus.SENT
    body: str | None = None
    reply_to_message_id: UUID | None = None
    sent_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    delivered_at: datetime | None = None
    read_at: datetime | None = None
    deleted_at: datetime | None = None

    @classmethod
    def create_text(
        cls,
        conversation_id: UUID,
        sender_participant_id: UUID,
        body: str,
        reply_to_message_id: UUID | None = None,
    ) -> Message:
        return cls(
            id=uuid4(),
            conversation_id=conversation_id,
            sender_participant_id=sender_participant_id,
            message_type=MessageType.TEXT,
            body=body,
            reply_to_message_id=reply_to_message_id,
        )

    @classmethod
    def create_media(
        cls,
        conversation_id: UUID,
        sender_participant_id: UUID,
        message_type: MessageType,
        reply_to_message_id: UUID | None = None,
    ) -> Message:
        return cls(
            id=uuid4(),
            conversation_id=conversation_id,
            sender_participant_id=sender_participant_id,
            message_type=message_type,
            reply_to_message_id=reply_to_message_id,
        )


@dataclass
class MessageMedia:
    id: UUID
    message_id: UUID | None
    conversation_id: UUID
    uploader_participant_id: UUID
    media_type: MediaType
    file_key: str
    mime_type: str
    file_name: str | None = None
    file_size_bytes: int | None = None
    duration_seconds: float | None = None
    checksum_sha256: str | None = None
    upload_status: MediaUploadStatus = MediaUploadStatus.PENDING
    created_at: datetime | None = None

    @classmethod
    def pending(
        cls,
        conversation_id: UUID,
        uploader_participant_id: UUID,
        media_type: MediaType,
        file_key: str,
        mime_type: str,
        file_name: str | None = None,
        file_size_bytes: int | None = None,
        duration_seconds: float | None = None,
        checksum_sha256: str | None = None,
    ) -> MessageMedia:
        return cls(
            id=uuid4(),
            message_id=None,
            conversation_id=conversation_id,
            uploader_participant_id=uploader_participant_id,
            media_type=media_type,
            file_key=file_key,
            mime_type=mime_type,
            file_name=file_name,
            file_size_bytes=file_size_bytes,
            duration_seconds=duration_seconds,
            checksum_sha256=checksum_sha256,
        )


@dataclass
class VoiceCall:
    id: UUID
    conversation_id: UUID
    caller_participant_id: UUID
    callee_participant_id: UUID
    status: CallStatus = CallStatus.RINGING
    started_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    accepted_at: datetime | None = None
    ended_at: datetime | None = None
    end_reason: str | None = None

    @classmethod
    def start(
        cls,
        conversation_id: UUID,
        caller_participant_id: UUID,
        callee_participant_id: UUID,
    ) -> VoiceCall:
        return cls(
            id=uuid4(),
            conversation_id=conversation_id,
            caller_participant_id=caller_participant_id,
            callee_participant_id=callee_participant_id,
        )

    def accept(self) -> None:
        if self.status != CallStatus.RINGING:
            raise InvalidCallTransitionError(f"Cannot accept call in {self.status.value} state.")
        self.status = CallStatus.ACCEPTED
        self.accepted_at = datetime.now(timezone.utc)

    def finish(self, status: CallStatus, reason: str | None = None) -> None:
        if self.status in {CallStatus.ENDED, CallStatus.MISSED, CallStatus.REJECTED, CallStatus.FAILED}:
            raise InvalidCallTransitionError(f"Call already terminal: {self.status.value}.")
        if status not in {CallStatus.ENDED, CallStatus.MISSED, CallStatus.REJECTED, CallStatus.FAILED}:
            raise InvalidCallTransitionError("Call can only finish into a terminal state.")
        self.status = status
        self.ended_at = datetime.now(timezone.utc)
        self.end_reason = reason
