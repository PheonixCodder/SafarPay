"""Communication API router."""
from __future__ import annotations

from typing import Annotated, Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, WebSocket, WebSocketDisconnect, status
from sp.core.observability.logging import get_logger
from sp.infrastructure.db.session import get_async_session
from sp.infrastructure.security.dependencies import (
    CurrentUser,
    OptionalDriverId,
    get_current_user_ws,
)
from sp.infrastructure.security.jwt import TokenPayload
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from ..application.schemas import (
    CallResponse,
    ConversationResponse,
    EndCallRequest,
    IceServerResponse,
    MediaMessageResponse,
    MediaUploadUrlRequest,
    MediaUploadUrlResponse,
    MediaUrlResponse,
    MessageResponse,
    RegisterMediaMessageRequest,
    SendTextMessageRequest,
    StartCallRequest,
)
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
from ..domain.exceptions import (
    CallNotFoundError,
    CommunicationDomainError,
    ConversationClosedError,
    ConversationNotFoundError,
    MediaUploadError,
    MessageNotFoundError,
    UnauthorisedConversationAccessError,
)
from ..domain.models import ConversationStatus
from ..infrastructure.dependencies import (
    get_access_uc,
    get_end_call_uc,
    get_get_conversation_uc,
    get_ice_servers_uc,
    get_list_conversations_uc,
    get_list_messages_uc,
    get_media_upload_uc,
    get_media_url_uc,
    get_register_media_uc,
    get_send_text_uc,
    get_signaling_uc,
    get_start_call_uc,
    get_ws_manager,
)
from ..infrastructure.websocket_manager import CommunicationEvent, WebSocketManager

router = APIRouter(prefix="/communication", tags=["communication"])
logger = get_logger("communication.api")

ConversationStatusQuery = Annotated[ConversationStatus | None, Query(alias="status")]
LimitQuery = Annotated[int, Query(ge=1, le=100)]
OffsetQuery = Annotated[int, Query(ge=0)]
BeforeMessageQuery = Annotated[UUID | None, Query()]


def _handle_domain(exc: Exception) -> HTTPException:
    if isinstance(exc, ConversationNotFoundError | MessageNotFoundError | CallNotFoundError):
        return HTTPException(status_code=404, detail=str(exc))
    if isinstance(exc, UnauthorisedConversationAccessError):
        return HTTPException(status_code=403, detail=str(exc))
    if isinstance(exc, ConversationClosedError):
        return HTTPException(status_code=409, detail=str(exc))
    if isinstance(exc, MediaUploadError):
        return HTTPException(status_code=422, detail=str(exc))
    if isinstance(exc, CommunicationDomainError):
        return HTTPException(status_code=400, detail=str(exc))
    logger.exception("Unhandled communication exception: %s", exc)
    return HTTPException(status_code=500, detail="Internal server error")


@router.get("/conversations", response_model=list[ConversationResponse])
async def list_conversations(
    current_user: CurrentUser,
    driver_id: OptionalDriverId,
    uc: Annotated[ListConversationsUseCase, Depends(get_list_conversations_uc)],
    status_filter: ConversationStatusQuery = None,
    limit: LimitQuery = 50,
    offset: OffsetQuery = 0,
) -> list[ConversationResponse]:
    return await uc.execute(current_user.user_id, driver_id, status_filter, limit, offset)


@router.get("/conversations/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(
    conversation_id: UUID,
    current_user: CurrentUser,
    driver_id: OptionalDriverId,
    uc: Annotated[GetConversationUseCase, Depends(get_get_conversation_uc)],
) -> ConversationResponse:
    try:
        return await uc.execute(conversation_id, current_user.user_id, driver_id)
    except Exception as exc:
        raise _handle_domain(exc) from None


@router.get("/conversations/{conversation_id}/messages", response_model=list[MessageResponse])
async def list_messages(
    conversation_id: UUID,
    current_user: CurrentUser,
    driver_id: OptionalDriverId,
    uc: Annotated[ListMessagesUseCase, Depends(get_list_messages_uc)],
    limit: LimitQuery = 50,
    before_message_id: BeforeMessageQuery = None,
) -> list[MessageResponse]:
    try:
        return await uc.execute(conversation_id, current_user.user_id, driver_id, limit, before_message_id)
    except Exception as exc:
        raise _handle_domain(exc) from None


@router.post("/conversations/{conversation_id}/messages", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
async def send_text_message(
    conversation_id: UUID,
    body: SendTextMessageRequest,
    current_user: CurrentUser,
    driver_id: OptionalDriverId,
    uc: Annotated[SendTextMessageUseCase, Depends(get_send_text_uc)],
) -> MessageResponse:
    try:
        return await uc.execute(conversation_id, body, current_user.user_id, driver_id)
    except Exception as exc:
        raise _handle_domain(exc) from None


@router.post("/conversations/{conversation_id}/media/upload-url", response_model=MediaUploadUrlResponse)
async def generate_media_upload_url(
    conversation_id: UUID,
    body: MediaUploadUrlRequest,
    current_user: CurrentUser,
    driver_id: OptionalDriverId,
    uc: Annotated[GenerateMediaUploadUrlUseCase, Depends(get_media_upload_uc)],
) -> MediaUploadUrlResponse:
    try:
        return await uc.execute(conversation_id, body, current_user.user_id, driver_id)
    except Exception as exc:
        raise _handle_domain(exc) from None


@router.post("/conversations/{conversation_id}/messages/media", response_model=MediaMessageResponse, status_code=status.HTTP_201_CREATED)
async def register_media_message(
    conversation_id: UUID,
    body: RegisterMediaMessageRequest,
    current_user: CurrentUser,
    driver_id: OptionalDriverId,
    uc: Annotated[RegisterMediaMessageUseCase, Depends(get_register_media_uc)],
) -> MediaMessageResponse:
    try:
        return await uc.execute(
            conversation_id,
            body.media_id,
            current_user.user_id,
            driver_id,
            body.reply_to_message_id,
        )
    except Exception as exc:
        raise _handle_domain(exc) from None


@router.get("/messages/{message_id}/media-url", response_model=MediaUrlResponse)
async def get_media_url(
    message_id: UUID,
    current_user: CurrentUser,
    driver_id: OptionalDriverId,
    uc: Annotated[GetMediaUrlUseCase, Depends(get_media_url_uc)],
) -> MediaUrlResponse:
    try:
        return await uc.execute(message_id, current_user.user_id, driver_id)
    except Exception as exc:
        raise _handle_domain(exc) from None


@router.post("/conversations/{conversation_id}/calls", response_model=CallResponse, status_code=status.HTTP_201_CREATED)
async def start_call(
    conversation_id: UUID,
    body: StartCallRequest,
    current_user: CurrentUser,
    driver_id: OptionalDriverId,
    uc: Annotated[StartCallUseCase, Depends(get_start_call_uc)],
) -> CallResponse:
    try:
        return await uc.execute(conversation_id, current_user.user_id, driver_id, body.initial_offer)
    except Exception as exc:
        raise _handle_domain(exc) from None


@router.post("/calls/{call_id}/end", response_model=CallResponse)
async def end_call(
    call_id: UUID,
    body: EndCallRequest,
    current_user: CurrentUser,
    driver_id: OptionalDriverId,
    uc: Annotated[EndCallUseCase, Depends(get_end_call_uc)],
) -> CallResponse:
    try:
        return await uc.execute(call_id, current_user.user_id, driver_id, body.status, body.reason)
    except Exception as exc:
        raise _handle_domain(exc) from None


@router.get("/webrtc/ice-servers", response_model=IceServerResponse)
async def get_ice_servers(
    uc: Annotated[GetIceServersUseCase, Depends(get_ice_servers_uc)],
) -> IceServerResponse:
    return await uc.execute()


async def _resolve_driver_id(session: AsyncSession, user_id: UUID) -> UUID | None:
    result = await session.execute(
        text("SELECT id FROM verification.drivers WHERE user_id = :uid LIMIT 1"),
        {"uid": user_id},
    )
    row = result.fetchone()
    return row[0] if row else None


@router.websocket("/ws")
async def communication_websocket(
    websocket: WebSocket,
    manager: Annotated[WebSocketManager, Depends(get_ws_manager)],
    access_uc: Annotated[ConversationAccessUseCase, Depends(get_access_uc)],
    signaling_uc: Annotated[SignalingUseCase, Depends(get_signaling_uc)],
    token_payload: Annotated[TokenPayload, Depends(get_current_user_ws)],
    session: Annotated[AsyncSession, Depends(get_async_session)],
) -> None:
    user_id = token_payload.user_id
    driver_id = await _resolve_driver_id(session, user_id)
    await manager.connect(user_id, websocket)
    subscribed: set[UUID] = set()
    try:
        while True:
            data: dict[str, Any] = await websocket.receive_json()
            action = data.get("action")
            conversation_id_raw = data.get("conversation_id")
            if not conversation_id_raw:
                continue
            conversation_id = UUID(conversation_id_raw)

            if action == "subscribe":
                await access_uc.assert_participant(conversation_id, user_id, driver_id)
                subscribed.add(conversation_id)
                await manager.subscribe(conversation_id, websocket)
            elif conversation_id not in subscribed:
                await manager.send(websocket, "ERROR", {"detail": "Subscribe before sending conversation events."})
            elif action in {"typing_started", "typing_stopped"}:
                event = CommunicationEvent.TYPING_STARTED if action == "typing_started" else CommunicationEvent.TYPING_STOPPED
                await manager.broadcast_to_conversation(conversation_id, event, {"conversation_id": str(conversation_id), "user_id": str(user_id)})
            elif action in {"webrtc_offer", "webrtc_answer", "webrtc_ice_candidate"}:
                signal_type = {
                    "webrtc_offer": "OFFER",
                    "webrtc_answer": "ANSWER",
                    "webrtc_ice_candidate": "ICE_CANDIDATE",
                }[action]
                await signaling_uc.relay(
                    conversation_id=conversation_id,
                    call_id=UUID(data["call_id"]),
                    signal_type=signal_type,
                    payload=data.get("payload", {}),
                    user_id=user_id,
                    driver_id=driver_id,
                )
                await session.commit()
    except WebSocketDisconnect:
        await manager.disconnect(user_id, websocket)
    except Exception as exc:
        await session.rollback()
        await manager.send(websocket, "ERROR", {"detail": str(exc)})
        await manager.disconnect(user_id, websocket)
