"""Communication repository and infrastructure protocols."""
from __future__ import annotations

from typing import Any, Protocol
from uuid import UUID

from .models import (
    Conversation,
    ConversationParticipant,
    ConversationStatus,
    Message,
    MessageMedia,
    VoiceCall,
)


class ConversationRepositoryProtocol(Protocol):
    async def find_by_id(self, conversation_id: UUID) -> Conversation | None: ...
    async def find_by_ride(self, service_request_id: UUID) -> Conversation | None: ...
    async def find_for_actor(
        self,
        user_id: UUID,
        driver_id: UUID | None,
        status_filter: ConversationStatus | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Conversation]: ...
    async def create_with_participants(self, conversation: Conversation) -> Conversation: ...
    async def close_by_ride(self, service_request_id: UUID) -> Conversation | None: ...
    async def get_driver_user_id(self, driver_id: UUID) -> UUID | None: ...


class ParticipantRepositoryProtocol(Protocol):
    async def find_for_actor(
        self,
        conversation_id: UUID,
        user_id: UUID,
        driver_id: UUID | None,
    ) -> ConversationParticipant | None: ...
    async def find_other_participant(
        self,
        conversation_id: UUID,
        participant_id: UUID,
    ) -> ConversationParticipant | None: ...


class MessageRepositoryProtocol(Protocol):
    async def create(self, message: Message) -> Message: ...
    async def find_by_id(self, message_id: UUID) -> Message | None: ...
    async def list_by_conversation(
        self,
        conversation_id: UUID,
        limit: int = 50,
        before_message_id: UUID | None = None,
    ) -> list[Message]: ...


class MediaRepositoryProtocol(Protocol):
    async def create(self, media: MessageMedia) -> MessageMedia: ...
    async def find_by_id(self, media_id: UUID) -> MessageMedia | None: ...
    async def find_by_message(self, message_id: UUID) -> MessageMedia | None: ...
    async def attach_to_message(self, media_id: UUID, message_id: UUID) -> MessageMedia: ...


class CallRepositoryProtocol(Protocol):
    async def create(self, call: VoiceCall) -> VoiceCall: ...
    async def find_by_id(self, call_id: UUID) -> VoiceCall | None: ...
    async def update(self, call: VoiceCall) -> VoiceCall: ...
    async def save_signal(
        self,
        call_id: UUID,
        sender_participant_id: UUID,
        signal_type: str,
        payload: dict[str, Any],
    ) -> None: ...


class StorageProviderProtocol(Protocol):
    async def generate_presigned_put_url(
        self,
        object_key: str,
        *,
        content_type: str,
        expires_in: int = 900,
    ) -> str: ...
    async def generate_presigned_get_url(self, object_key: str, *, expires_in: int = 3600) -> str: ...
