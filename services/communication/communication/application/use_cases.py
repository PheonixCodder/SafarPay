"""Communication use cases."""
from __future__ import annotations

import json
from typing import Any
from uuid import UUID

from sp.infrastructure.cache.manager import CacheManager

from ..domain.exceptions import (
    CallNotFoundError,
    ConversationNotFoundError,
    MediaUploadError,
    MessageNotFoundError,
    UnauthorisedConversationAccessError,
)
from ..domain.interfaces import (
    CallRepositoryProtocol,
    ConversationRepositoryProtocol,
    MediaRepositoryProtocol,
    MessageRepositoryProtocol,
    ParticipantRepositoryProtocol,
    StorageProviderProtocol,
)
from ..domain.models import (
    CallStatus,
    Conversation,
    ConversationStatus,
    MediaType,
    Message,
    MessageMedia,
    MessageType,
    VoiceCall,
)
from ..infrastructure.storage import build_media_key
from ..infrastructure.websocket_manager import CommunicationEvent, WebSocketManager
from .schemas import (
    CallResponse,
    ConversationResponse,
    IceServerResponse,
    MediaMessageResponse,
    MediaUploadUrlRequest,
    MediaUploadUrlResponse,
    MediaUrlResponse,
    MessageResponse,
    SendTextMessageRequest,
)

_CONVERSATION_LOCK_NS = "communication"
_CONVERSATION_LOCK_TTL = 30

IMAGE_MIME_TYPES = {"image/jpeg", "image/png", "image/webp", "image/heic"}
VOICE_MIME_TYPES = {"audio/mpeg", "audio/mp4", "audio/aac", "audio/ogg", "audio/webm"}
MAX_IMAGE_BYTES = 10 * 1024 * 1024
MAX_VOICE_BYTES = 25 * 1024 * 1024
MAX_VOICE_SECONDS = 300.0


def _conversation_to_resp(c: Conversation) -> ConversationResponse:
    return ConversationResponse(
        id=c.id,
        service_request_id=c.service_request_id,
        passenger_user_id=c.passenger_user_id,
        driver_id=c.driver_id,
        driver_user_id=c.driver_user_id,
        status=c.status,
        opened_at=c.opened_at,
        closed_at=c.closed_at,
    )


def _message_to_resp(m: Message) -> MessageResponse:
    return MessageResponse(
        id=m.id,
        conversation_id=m.conversation_id,
        sender_participant_id=m.sender_participant_id,
        message_type=m.message_type,
        body=m.body,
        sent_at=m.sent_at,
        reply_to_message_id=m.reply_to_message_id,
    )


def _call_to_resp(c: VoiceCall) -> CallResponse:
    return CallResponse(
        id=c.id,
        conversation_id=c.conversation_id,
        caller_participant_id=c.caller_participant_id,
        callee_participant_id=c.callee_participant_id,
        status=c.status,
        started_at=c.started_at,
        accepted_at=c.accepted_at,
        ended_at=c.ended_at,
        end_reason=c.end_reason,
    )


async def _load_conversation_or_404(
    repo: ConversationRepositoryProtocol, conversation_id: UUID
) -> Conversation:
    conversation = await repo.find_by_id(conversation_id)
    if not conversation:
        raise ConversationNotFoundError(f"Conversation {conversation_id} not found.")
    return conversation


class OpenConversationFromRideUseCase:
    def __init__(
        self,
        conversation_repo: ConversationRepositoryProtocol,
        cache: CacheManager,
        ws: WebSocketManager,
    ) -> None:
        self._conversation_repo = conversation_repo
        self._cache = cache
        self._ws = ws

    async def execute(self, ride_id: UUID, passenger_user_id: UUID, driver_id: UUID) -> ConversationResponse:
        existing = await self._conversation_repo.find_by_ride(ride_id)
        if existing:
            return _conversation_to_resp(existing)

        token = str(ride_id)
        lock_key = f"conversation:create:{ride_id}"
        if not await self._cache.set(_CONVERSATION_LOCK_NS, lock_key, token, nx=True, ttl=_CONVERSATION_LOCK_TTL):
            existing = await self._conversation_repo.find_by_ride(ride_id)
            if existing:
                return _conversation_to_resp(existing)

        try:
            driver_user_id = await self._conversation_repo.get_driver_user_id(driver_id)
            if not driver_user_id:
                raise UnauthorisedConversationAccessError("Accepted driver has no auth user.")
            conversation = Conversation.open(
                service_request_id=ride_id,
                passenger_user_id=passenger_user_id,
                driver_id=driver_id,
                driver_user_id=driver_user_id,
            )
            conversation = await self._conversation_repo.create_with_participants(conversation)
            await self._ws.broadcast_to_conversation(
                conversation.id,
                "CONVERSATION_OPENED",
                {"conversation_id": str(conversation.id), "ride_id": str(ride_id)},
            )
            return _conversation_to_resp(conversation)
        finally:
            await self._cache.delete_if_equals(_CONVERSATION_LOCK_NS, lock_key, token)


class CloseConversationFromRideUseCase:
    def __init__(self, conversation_repo: ConversationRepositoryProtocol, ws: WebSocketManager) -> None:
        self._conversation_repo = conversation_repo
        self._ws = ws

    async def execute(self, ride_id: UUID) -> ConversationResponse | None:
        conversation = await self._conversation_repo.close_by_ride(ride_id)
        if not conversation:
            return None
        await self._ws.broadcast_to_conversation(
            conversation.id,
            "CONVERSATION_CLOSED",
            {"conversation_id": str(conversation.id), "ride_id": str(ride_id)},
        )
        return _conversation_to_resp(conversation)


class ConversationAccessUseCase:
    def __init__(
        self,
        conversation_repo: ConversationRepositoryProtocol,
        participant_repo: ParticipantRepositoryProtocol,
    ) -> None:
        self._conversation_repo = conversation_repo
        self._participant_repo = participant_repo

    async def assert_participant(self, conversation_id: UUID, user_id: UUID, driver_id: UUID | None):
        conversation = await _load_conversation_or_404(self._conversation_repo, conversation_id)
        participant = await self._participant_repo.find_for_actor(conversation_id, user_id, driver_id)
        if not participant:
            raise UnauthorisedConversationAccessError("Caller is not a participant in this conversation.")
        return conversation, participant


class ListConversationsUseCase:
    def __init__(self, conversation_repo: ConversationRepositoryProtocol) -> None:
        self._conversation_repo = conversation_repo

    async def execute(
        self,
        user_id: UUID,
        driver_id: UUID | None,
        status_filter: ConversationStatus | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[ConversationResponse]:
        conversations = await self._conversation_repo.find_for_actor(user_id, driver_id, status_filter, limit, offset)
        return [_conversation_to_resp(c) for c in conversations]


class GetConversationUseCase:
    def __init__(self, access: ConversationAccessUseCase) -> None:
        self._access = access

    async def execute(self, conversation_id: UUID, user_id: UUID, driver_id: UUID | None) -> ConversationResponse:
        conversation, _ = await self._access.assert_participant(conversation_id, user_id, driver_id)
        return _conversation_to_resp(conversation)


class SendTextMessageUseCase:
    def __init__(
        self,
        access: ConversationAccessUseCase,
        message_repo: MessageRepositoryProtocol,
        ws: WebSocketManager,
    ) -> None:
        self._access = access
        self._message_repo = message_repo
        self._ws = ws

    async def execute(
        self,
        conversation_id: UUID,
        cmd: SendTextMessageRequest,
        user_id: UUID,
        driver_id: UUID | None,
    ) -> MessageResponse:
        conversation, participant = await self._access.assert_participant(conversation_id, user_id, driver_id)
        conversation.ensure_active()
        message = Message.create_text(conversation.id, participant.id, cmd.body, cmd.reply_to_message_id)
        message = await self._message_repo.create(message)
        payload = _message_to_resp(message).model_dump(mode="json")
        await self._ws.broadcast_to_conversation(conversation.id, CommunicationEvent.MESSAGE_SENT, payload)
        return _message_to_resp(message)


class ListMessagesUseCase:
    def __init__(
        self,
        access: ConversationAccessUseCase,
        message_repo: MessageRepositoryProtocol,
    ) -> None:
        self._access = access
        self._message_repo = message_repo

    async def execute(
        self,
        conversation_id: UUID,
        user_id: UUID,
        driver_id: UUID | None,
        limit: int = 50,
        before_message_id: UUID | None = None,
    ) -> list[MessageResponse]:
        await self._access.assert_participant(conversation_id, user_id, driver_id)
        messages = await self._message_repo.list_by_conversation(conversation_id, limit, before_message_id)
        return [_message_to_resp(m) for m in messages]


class GenerateMediaUploadUrlUseCase:
    def __init__(
        self,
        access: ConversationAccessUseCase,
        media_repo: MediaRepositoryProtocol,
        storage: StorageProviderProtocol,
    ) -> None:
        self._access = access
        self._media_repo = media_repo
        self._storage = storage

    def _validate(self, cmd: MediaUploadUrlRequest) -> None:
        if cmd.media_type == MediaType.IMAGE:
            if cmd.mime_type not in IMAGE_MIME_TYPES:
                raise MediaUploadError("Unsupported image MIME type.")
            if cmd.file_size_bytes and cmd.file_size_bytes > MAX_IMAGE_BYTES:
                raise MediaUploadError("Image exceeds maximum upload size.")
        else:
            if cmd.mime_type not in VOICE_MIME_TYPES:
                raise MediaUploadError("Unsupported voice-note MIME type.")
            if cmd.file_size_bytes and cmd.file_size_bytes > MAX_VOICE_BYTES:
                raise MediaUploadError("Voice note exceeds maximum upload size.")
            if cmd.duration_seconds and cmd.duration_seconds > MAX_VOICE_SECONDS:
                raise MediaUploadError("Voice note exceeds maximum duration.")

    async def execute(
        self,
        conversation_id: UUID,
        cmd: MediaUploadUrlRequest,
        user_id: UUID,
        driver_id: UUID | None,
    ) -> MediaUploadUrlResponse:
        self._validate(cmd)
        conversation, participant = await self._access.assert_participant(conversation_id, user_id, driver_id)
        conversation.ensure_active()
        file_key = build_media_key(conversation_id, cmd.media_type.value, cmd.file_name)
        media = MessageMedia.pending(
            conversation_id=conversation.id,
            uploader_participant_id=participant.id,
            media_type=cmd.media_type,
            file_key=file_key,
            mime_type=cmd.mime_type,
            file_name=cmd.file_name,
            file_size_bytes=cmd.file_size_bytes,
            duration_seconds=cmd.duration_seconds,
            checksum_sha256=cmd.checksum_sha256,
        )
        media = await self._media_repo.create(media)
        url = await self._storage.generate_presigned_put_url(file_key, content_type=cmd.mime_type)
        return MediaUploadUrlResponse(
            media_id=media.id,
            presigned_url=url,
            file_key=file_key,
            expires_in_seconds=900,
            media_type=cmd.media_type,
            mime_type=cmd.mime_type,
        )


class RegisterMediaMessageUseCase:
    def __init__(
        self,
        access: ConversationAccessUseCase,
        message_repo: MessageRepositoryProtocol,
        media_repo: MediaRepositoryProtocol,
        ws: WebSocketManager,
    ) -> None:
        self._access = access
        self._message_repo = message_repo
        self._media_repo = media_repo
        self._ws = ws

    async def execute(
        self,
        conversation_id: UUID,
        media_id: UUID,
        user_id: UUID,
        driver_id: UUID | None,
        reply_to_message_id: UUID | None = None,
    ) -> MediaMessageResponse:
        conversation, participant = await self._access.assert_participant(conversation_id, user_id, driver_id)
        conversation.ensure_active()
        media = await self._media_repo.find_by_id(media_id)
        if not media or media.conversation_id != conversation.id or media.uploader_participant_id != participant.id:
            raise MediaUploadError("Media upload record not found for this participant.")
        message_type = MessageType.IMAGE if media.media_type == MediaType.IMAGE else MessageType.VOICE_NOTE
        message = Message.create_media(conversation.id, participant.id, message_type, reply_to_message_id)
        message = await self._message_repo.create(message)
        media = await self._media_repo.attach_to_message(media.id, message.id)
        payload = {"message": _message_to_resp(message).model_dump(mode="json"), "media_id": str(media.id)}
        await self._ws.broadcast_to_conversation(conversation.id, CommunicationEvent.MEDIA_MESSAGE_SENT, payload)
        return MediaMessageResponse(
            message=_message_to_resp(message),
            media_id=media.id,
            file_key=media.file_key,
            media_type=media.media_type,
            mime_type=media.mime_type,
        )


class GetMediaUrlUseCase:
    def __init__(
        self,
        access: ConversationAccessUseCase,
        message_repo: MessageRepositoryProtocol,
        media_repo: MediaRepositoryProtocol,
        storage: StorageProviderProtocol,
    ) -> None:
        self._access = access
        self._message_repo = message_repo
        self._media_repo = media_repo
        self._storage = storage

    async def execute(
        self,
        message_id: UUID,
        user_id: UUID,
        driver_id: UUID | None,
    ) -> MediaUrlResponse:
        message = await self._message_repo.find_by_id(message_id)
        if not message:
            raise MessageNotFoundError(f"Message {message_id} not found.")
        await self._access.assert_participant(message.conversation_id, user_id, driver_id)
        media = await self._media_repo.find_by_message(message_id)
        if not media:
            raise MediaUploadError("Message has no media.")
        url = await self._storage.generate_presigned_get_url(media.file_key)
        return MediaUrlResponse(message_id=message_id, media_id=media.id, view_url=url, expires_in_seconds=3600)


class StartCallUseCase:
    def __init__(
        self,
        access: ConversationAccessUseCase,
        participant_repo: ParticipantRepositoryProtocol,
        call_repo: CallRepositoryProtocol,
        ws: WebSocketManager,
    ) -> None:
        self._access = access
        self._participant_repo = participant_repo
        self._call_repo = call_repo
        self._ws = ws

    async def execute(
        self,
        conversation_id: UUID,
        user_id: UUID,
        driver_id: UUID | None,
        initial_offer: dict[str, Any] | None = None,
    ) -> CallResponse:
        conversation, participant = await self._access.assert_participant(conversation_id, user_id, driver_id)
        conversation.ensure_active()
        callee = await self._participant_repo.find_other_participant(conversation_id, participant.id)
        if not callee:
            raise UnauthorisedConversationAccessError("No callee participant found.")
        call = VoiceCall.start(conversation.id, participant.id, callee.id)
        call = await self._call_repo.create(call)
        payload = _call_to_resp(call).model_dump(mode="json")
        if initial_offer:
            await self._call_repo.save_signal(call.id, participant.id, "OFFER", initial_offer)
            payload["initial_offer"] = initial_offer
        await self._ws.broadcast_to_conversation(conversation.id, CommunicationEvent.CALL_RINGING, payload)
        return _call_to_resp(call)


class EndCallUseCase:
    def __init__(
        self,
        call_repo: CallRepositoryProtocol,
        access: ConversationAccessUseCase,
        ws: WebSocketManager,
    ) -> None:
        self._call_repo = call_repo
        self._access = access
        self._ws = ws

    async def execute(
        self,
        call_id: UUID,
        user_id: UUID,
        driver_id: UUID | None,
        status: CallStatus,
        reason: str | None = None,
    ) -> CallResponse:
        call = await self._call_repo.find_by_id(call_id)
        if not call:
            raise CallNotFoundError(f"Call {call_id} not found.")
        await self._access.assert_participant(call.conversation_id, user_id, driver_id)
        call.finish(status, reason)
        call = await self._call_repo.update(call)
        await self._ws.broadcast_to_conversation(
            call.conversation_id,
            CommunicationEvent.CALL_ENDED,
            _call_to_resp(call).model_dump(mode="json"),
        )
        return _call_to_resp(call)


class SignalingUseCase:
    def __init__(
        self,
        access: ConversationAccessUseCase,
        call_repo: CallRepositoryProtocol,
        ws: WebSocketManager,
    ) -> None:
        self._access = access
        self._call_repo = call_repo
        self._ws = ws

    async def relay(
        self,
        conversation_id: UUID,
        call_id: UUID,
        signal_type: str,
        payload: dict[str, Any],
        user_id: UUID,
        driver_id: UUID | None,
    ) -> None:
        _, participant = await self._access.assert_participant(conversation_id, user_id, driver_id)
        call = await self._call_repo.find_by_id(call_id)
        if not call or call.conversation_id != conversation_id:
            raise CallNotFoundError(f"Call {call_id} not found.")
        if signal_type == "ANSWER" and call.status == CallStatus.RINGING:
            call.accept()
            await self._call_repo.update(call)
            await self._ws.broadcast_to_conversation(
                conversation_id,
                CommunicationEvent.CALL_ACCEPTED,
                _call_to_resp(call).model_dump(mode="json"),
            )
        await self._call_repo.save_signal(call_id, participant.id, signal_type, payload)
        event = {
            "OFFER": CommunicationEvent.WEBRTC_OFFER,
            "ANSWER": CommunicationEvent.WEBRTC_ANSWER,
            "ICE_CANDIDATE": CommunicationEvent.WEBRTC_ICE_CANDIDATE,
        }.get(signal_type, signal_type)
        await self._ws.broadcast_to_conversation(
            conversation_id,
            event,
            {"call_id": str(call_id), "sender_participant_id": str(participant.id), "payload": payload},
        )


class GetIceServersUseCase:
    def __init__(self, ice_servers_json: str | None) -> None:
        self._ice_servers_json = ice_servers_json

    async def execute(self) -> IceServerResponse:
        if not self._ice_servers_json:
            return IceServerResponse(ice_servers=[{"urls": ["stun:stun.l.google.com:19302"]}])
        try:
            parsed = json.loads(self._ice_servers_json)
        except json.JSONDecodeError:
            parsed = [{"urls": ["stun:stun.l.google.com:19302"]}]
        if isinstance(parsed, dict):
            parsed = [parsed]
        return IceServerResponse(ice_servers=parsed)
