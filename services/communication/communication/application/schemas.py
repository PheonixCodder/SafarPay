"""Pydantic schemas for communication service."""
from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field

from ..domain.models import CallStatus, ConversationStatus, MediaType, MessageType


class ConversationResponse(BaseModel):
    id: UUID
    service_request_id: UUID
    passenger_user_id: UUID
    driver_id: UUID
    driver_user_id: UUID
    status: ConversationStatus
    opened_at: datetime
    closed_at: datetime | None = None


class SendTextMessageRequest(BaseModel):
    body: str = Field(..., min_length=1, max_length=4000)
    reply_to_message_id: UUID | None = None


class MessageResponse(BaseModel):
    id: UUID
    conversation_id: UUID
    sender_participant_id: UUID
    message_type: MessageType
    body: str | None = None
    sent_at: datetime
    reply_to_message_id: UUID | None = None


class MediaUploadUrlRequest(BaseModel):
    media_type: MediaType
    file_name: str | None = Field(None, max_length=255)
    mime_type: str = Field(..., max_length=120)
    file_size_bytes: int | None = Field(None, ge=0)
    duration_seconds: float | None = Field(None, ge=0)
    checksum_sha256: str | None = Field(None, min_length=64, max_length=64)


class MediaUploadUrlResponse(BaseModel):
    media_id: UUID
    presigned_url: str
    file_key: str
    expires_in_seconds: int
    media_type: MediaType
    mime_type: str


class RegisterMediaMessageRequest(BaseModel):
    media_id: UUID
    reply_to_message_id: UUID | None = None


class MediaMessageResponse(BaseModel):
    message: MessageResponse
    media_id: UUID
    file_key: str
    media_type: MediaType
    mime_type: str


class MediaUrlResponse(BaseModel):
    message_id: UUID
    media_id: UUID
    view_url: str
    expires_in_seconds: int


class StartCallRequest(BaseModel):
    initial_offer: dict[str, Any] | None = None


class CallResponse(BaseModel):
    id: UUID
    conversation_id: UUID
    caller_participant_id: UUID
    callee_participant_id: UUID
    status: CallStatus
    started_at: datetime
    accepted_at: datetime | None = None
    ended_at: datetime | None = None
    end_reason: str | None = None


class EndCallRequest(BaseModel):
    status: CallStatus = CallStatus.ENDED
    reason: str | None = Field(None, max_length=120)


class IceServerResponse(BaseModel):
    ice_servers: list[dict[str, Any]]
