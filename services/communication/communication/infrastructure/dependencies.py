"""FastAPI dependency wiring for communication service."""
from __future__ import annotations

from typing import Annotated

from fastapi import Depends, Request
from sp.core.config import Settings, get_settings
from sp.infrastructure.cache.manager import CacheManager
from sp.infrastructure.db.session import get_async_session
from sqlalchemy.ext.asyncio import AsyncSession

from ..application.use_cases import (
    ConversationAccessUseCase,
    EndCallUseCase,
    GenerateMediaUploadUrlUseCase,
    GetConversationUseCase,
    GetIceServersUseCase,
    GetMediaUrlUseCase,
    ListConversationsUseCase,
    ListMessagesUseCase,
    RegisterMediaMessageUseCase,
    SendTextMessageUseCase,
    SignalingUseCase,
    StartCallUseCase,
)
from ..domain.interfaces import (
    CallRepositoryProtocol,
    ConversationRepositoryProtocol,
    MediaRepositoryProtocol,
    MessageRepositoryProtocol,
    ParticipantRepositoryProtocol,
    StorageProviderProtocol,
)
from .repositories import (
    CallRepository,
    ConversationRepository,
    MediaRepository,
    MessageRepository,
    ParticipantRepository,
)
from .websocket_manager import WebSocketManager

DBSession = Annotated[AsyncSession, Depends(get_async_session)]
AppSettings = Annotated[Settings, Depends(get_settings)]


def get_cache(request: Request) -> CacheManager:
    return request.app.state.cache


def get_ws_manager(request: Request) -> WebSocketManager:
    return request.app.state.ws_manager


def get_storage(request: Request) -> StorageProviderProtocol:
    return request.app.state.storage


def get_conversation_repo(session: DBSession, settings: AppSettings) -> ConversationRepositoryProtocol:
    return ConversationRepository(session, settings.COMMUNICATION_EVENTS_TOPIC)


def get_participant_repo(session: DBSession) -> ParticipantRepositoryProtocol:
    return ParticipantRepository(session)


def get_message_repo(session: DBSession, settings: AppSettings) -> MessageRepositoryProtocol:
    return MessageRepository(session, settings.COMMUNICATION_EVENTS_TOPIC)


def get_media_repo(session: DBSession, settings: AppSettings) -> MediaRepositoryProtocol:
    return MediaRepository(session, settings.COMMUNICATION_EVENTS_TOPIC)


def get_call_repo(session: DBSession, settings: AppSettings) -> CallRepositoryProtocol:
    return CallRepository(session, settings.COMMUNICATION_EVENTS_TOPIC)


def get_access_uc(
    conversation_repo: Annotated[ConversationRepositoryProtocol, Depends(get_conversation_repo)],
    participant_repo: Annotated[ParticipantRepositoryProtocol, Depends(get_participant_repo)],
) -> ConversationAccessUseCase:
    return ConversationAccessUseCase(conversation_repo, participant_repo)


def get_list_conversations_uc(
    conversation_repo: Annotated[ConversationRepositoryProtocol, Depends(get_conversation_repo)],
) -> ListConversationsUseCase:
    return ListConversationsUseCase(conversation_repo)


def get_get_conversation_uc(
    access: Annotated[ConversationAccessUseCase, Depends(get_access_uc)],
) -> GetConversationUseCase:
    return GetConversationUseCase(access)


def get_send_text_uc(
    access: Annotated[ConversationAccessUseCase, Depends(get_access_uc)],
    message_repo: Annotated[MessageRepositoryProtocol, Depends(get_message_repo)],
    request: Request,
) -> SendTextMessageUseCase:
    return SendTextMessageUseCase(access, message_repo, get_ws_manager(request))


def get_list_messages_uc(
    access: Annotated[ConversationAccessUseCase, Depends(get_access_uc)],
    message_repo: Annotated[MessageRepositoryProtocol, Depends(get_message_repo)],
) -> ListMessagesUseCase:
    return ListMessagesUseCase(access, message_repo)


def get_media_upload_uc(
    access: Annotated[ConversationAccessUseCase, Depends(get_access_uc)],
    media_repo: Annotated[MediaRepositoryProtocol, Depends(get_media_repo)],
    request: Request,
) -> GenerateMediaUploadUrlUseCase:
    return GenerateMediaUploadUrlUseCase(access, media_repo, get_storage(request))


def get_register_media_uc(
    access: Annotated[ConversationAccessUseCase, Depends(get_access_uc)],
    message_repo: Annotated[MessageRepositoryProtocol, Depends(get_message_repo)],
    media_repo: Annotated[MediaRepositoryProtocol, Depends(get_media_repo)],
    request: Request,
) -> RegisterMediaMessageUseCase:
    return RegisterMediaMessageUseCase(access, message_repo, media_repo, get_ws_manager(request))


def get_media_url_uc(
    access: Annotated[ConversationAccessUseCase, Depends(get_access_uc)],
    message_repo: Annotated[MessageRepositoryProtocol, Depends(get_message_repo)],
    media_repo: Annotated[MediaRepositoryProtocol, Depends(get_media_repo)],
    request: Request,
) -> GetMediaUrlUseCase:
    return GetMediaUrlUseCase(access, message_repo, media_repo, get_storage(request))


def get_start_call_uc(
    access: Annotated[ConversationAccessUseCase, Depends(get_access_uc)],
    participant_repo: Annotated[ParticipantRepositoryProtocol, Depends(get_participant_repo)],
    call_repo: Annotated[CallRepositoryProtocol, Depends(get_call_repo)],
    request: Request,
) -> StartCallUseCase:
    return StartCallUseCase(access, participant_repo, call_repo, get_ws_manager(request))


def get_end_call_uc(
    access: Annotated[ConversationAccessUseCase, Depends(get_access_uc)],
    call_repo: Annotated[CallRepositoryProtocol, Depends(get_call_repo)],
    request: Request,
) -> EndCallUseCase:
    return EndCallUseCase(call_repo, access, get_ws_manager(request))


def get_signaling_uc(
    access: Annotated[ConversationAccessUseCase, Depends(get_access_uc)],
    call_repo: Annotated[CallRepositoryProtocol, Depends(get_call_repo)],
    request: Request,
) -> SignalingUseCase:
    return SignalingUseCase(access, call_repo, get_ws_manager(request))


def get_ice_servers_uc(request: Request) -> GetIceServersUseCase:
    return GetIceServersUseCase(getattr(request.app.state.settings, "WEBRTC_ICE_SERVERS_JSON", None))


StorageProvider = Annotated[StorageProviderProtocol, Depends(get_storage)]
