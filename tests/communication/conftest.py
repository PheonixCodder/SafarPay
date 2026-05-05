from __future__ import annotations

# ruff: noqa: E402,I001

import sys
from contextlib import asynccontextmanager
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any
from uuid import UUID, uuid4

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sp.infrastructure.db.session import get_async_session
from sp.infrastructure.security.dependencies import (
    get_current_user,
    get_current_user_ws,
    get_optional_driver_id,
)
from sp.infrastructure.security.jwt import TokenPayload

ROOT = Path(__file__).resolve().parents[2]
COMMUNICATION_SRC = ROOT / "services" / "communication"
if str(COMMUNICATION_SRC) not in sys.path:
    sys.path.insert(0, str(COMMUNICATION_SRC))
loaded_communication = sys.modules.get("communication")
if loaded_communication is not None and str(COMMUNICATION_SRC) not in str(getattr(loaded_communication, "__file__", "")):
    del sys.modules["communication"]

from communication.api.router import router as communication_router
from communication.domain.models import (
    Conversation,
    ConversationParticipant,
    ConversationStatus,
    MediaUploadStatus,
    MediaType,
    Message,
    MessageMedia,
    ParticipantRole,
    VoiceCall,
)

PASSENGER_ID = UUID("11111111-1111-1111-1111-111111111111")
DRIVER_USER_ID = UUID("22222222-2222-2222-2222-222222222222")
DRIVER_ID = UUID("33333333-3333-3333-3333-333333333333")
OTHER_USER_ID = UUID("44444444-4444-4444-4444-444444444444")
OTHER_DRIVER_ID = UUID("55555555-5555-5555-5555-555555555555")
RIDE_ID = UUID("66666666-6666-6666-6666-666666666666")
CONVERSATION_ID = UUID("77777777-7777-7777-7777-777777777777")


def token(user_id: UUID = PASSENGER_ID, role: str = "passenger") -> TokenPayload:
    now = datetime.now(timezone.utc)
    return TokenPayload(
        user_id=user_id,
        email=f"{user_id}@example.test",
        role=role,
        session_id=uuid4(),
        iat=now,
        exp=now + timedelta(hours=1),
    )


def make_conversation(
    *,
    conversation_id: UUID = CONVERSATION_ID,
    passenger_user_id: UUID = PASSENGER_ID,
    driver_id: UUID = DRIVER_ID,
    driver_user_id: UUID = DRIVER_USER_ID,
    status: ConversationStatus = ConversationStatus.ACTIVE,
) -> Conversation:
    return Conversation(
        id=conversation_id,
        service_request_id=RIDE_ID,
        passenger_user_id=passenger_user_id,
        driver_id=driver_id,
        driver_user_id=driver_user_id,
        status=status,
        opened_at=datetime.now(timezone.utc),
    )


def make_participants(conversation: Conversation) -> tuple[ConversationParticipant, ConversationParticipant]:
    passenger = ConversationParticipant(
        id=UUID("88888888-8888-8888-8888-888888888888"),
        conversation_id=conversation.id,
        role=ParticipantRole.PASSENGER,
        user_id=conversation.passenger_user_id,
        driver_id=None,
    )
    driver = ConversationParticipant(
        id=UUID("99999999-9999-9999-9999-999999999999"),
        conversation_id=conversation.id,
        role=ParticipantRole.DRIVER,
        user_id=conversation.driver_user_id,
        driver_id=conversation.driver_id,
    )
    return passenger, driver


def make_message(
    conversation: Conversation,
    participant: ConversationParticipant,
    *,
    body: str = "hello",
) -> Message:
    return Message.create_text(conversation.id, participant.id, body)


def make_media(
    conversation: Conversation,
    participant: ConversationParticipant,
    *,
    media_type: MediaType = MediaType.IMAGE,
) -> MessageMedia:
    return MessageMedia.pending(
        conversation_id=conversation.id,
        uploader_participant_id=participant.id,
        media_type=media_type,
        file_key=f"conversations/{conversation.id}/{media_type.value.lower()}/{uuid4().hex}.bin",
        mime_type="image/png" if media_type == MediaType.IMAGE else "audio/ogg",
        file_name="upload.png" if media_type == MediaType.IMAGE else "voice.ogg",
        file_size_bytes=100,
        duration_seconds=3.0 if media_type == MediaType.VOICE_NOTE else None,
    )


class FakeCache:
    def __init__(self, allow_lock: bool = True) -> None:
        self.allow_lock = allow_lock
        self.values: dict[tuple[str, str], str] = {}
        self.deleted_if_equals: list[tuple[str, str, str]] = []

    async def set(self, namespace: str, key: str, value: str, *, nx: bool = False, ttl: int | None = None) -> bool:
        if not self.allow_lock:
            return False
        compound = (namespace, key)
        if nx and compound in self.values:
            return False
        self.values[compound] = value
        return True

    async def delete_if_equals(self, namespace: str, key: str, value: str) -> None:
        self.deleted_if_equals.append((namespace, key, value))
        if self.values.get((namespace, key)) == value:
            self.values.pop((namespace, key), None)


class FakeWsManager:
    def __init__(self) -> None:
        self.broadcasts: list[tuple[UUID, Any, dict[str, Any]]] = []

    async def broadcast_to_conversation(self, conversation_id: UUID, event: Any, payload: dict[str, Any]) -> int:
        self.broadcasts.append((conversation_id, event, payload))
        return 1


class FakeStorage:
    def __init__(self) -> None:
        self.puts: list[tuple[str, str, int]] = []
        self.gets: list[tuple[str, int]] = []

    async def generate_presigned_put_url(self, object_key: str, *, content_type: str, expires_in: int = 900) -> str:
        self.puts.append((object_key, content_type, expires_in))
        return f"https://s3.test/put/{object_key}"

    async def generate_presigned_get_url(self, object_key: str, *, expires_in: int = 3600) -> str:
        self.gets.append((object_key, expires_in))
        return f"https://s3.test/get/{object_key}"


class FakeConversationRepo:
    def __init__(self, conversation: Conversation | None = None, driver_user_id: UUID | None = DRIVER_USER_ID) -> None:
        self.conversation = conversation
        self.driver_user_id = driver_user_id
        self.created: list[Conversation] = []
        self.closed: list[UUID] = []
        self.find_actor_calls: list[tuple[UUID, UUID | None, ConversationStatus | None, int, int]] = []

    async def find_by_id(self, conversation_id: UUID) -> Conversation | None:
        return self.conversation if self.conversation and self.conversation.id == conversation_id else None

    async def find_by_ride(self, service_request_id: UUID) -> Conversation | None:
        return self.conversation if self.conversation and self.conversation.service_request_id == service_request_id else None

    async def find_for_actor(
        self,
        user_id: UUID,
        driver_id: UUID | None,
        status_filter: ConversationStatus | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Conversation]:
        self.find_actor_calls.append((user_id, driver_id, status_filter, limit, offset))
        if not self.conversation:
            return []
        if status_filter and self.conversation.status != status_filter:
            return []
        if user_id in {self.conversation.passenger_user_id, self.conversation.driver_user_id}:
            return [self.conversation]
        if driver_id and driver_id == self.conversation.driver_id:
            return [self.conversation]
        return []

    async def create_with_participants(self, conversation: Conversation) -> Conversation:
        self.conversation = conversation
        self.created.append(conversation)
        return conversation

    async def close_by_ride(self, service_request_id: UUID) -> Conversation | None:
        if not self.conversation or self.conversation.service_request_id != service_request_id:
            return None
        self.conversation.close()
        self.closed.append(service_request_id)
        return self.conversation

    async def get_driver_user_id(self, driver_id: UUID) -> UUID | None:
        return self.driver_user_id if driver_id == DRIVER_ID else None


class FakeParticipantRepo:
    def __init__(self, conversation: Conversation) -> None:
        self.passenger, self.driver = make_participants(conversation)
        self.find_actor_calls: list[tuple[UUID, UUID, UUID | None]] = []

    async def find_for_actor(
        self,
        conversation_id: UUID,
        user_id: UUID,
        driver_id: UUID | None,
    ) -> ConversationParticipant | None:
        self.find_actor_calls.append((conversation_id, user_id, driver_id))
        if conversation_id != self.passenger.conversation_id:
            return None
        if user_id == self.passenger.user_id and driver_id is None:
            return self.passenger
        if user_id == self.driver.user_id and driver_id == self.driver.driver_id:
            return self.driver
        return None

    async def find_other_participant(
        self,
        conversation_id: UUID,
        participant_id: UUID,
    ) -> ConversationParticipant | None:
        if conversation_id != self.passenger.conversation_id:
            return None
        if participant_id == self.passenger.id:
            return self.driver
        if participant_id == self.driver.id:
            return self.passenger
        return None


class FakeMessageRepo:
    def __init__(self, messages: list[Message] | None = None) -> None:
        self.messages = messages or []
        self.created: list[Message] = []

    async def create(self, message: Message) -> Message:
        self.created.append(message)
        self.messages.append(message)
        return message

    async def find_by_id(self, message_id: UUID) -> Message | None:
        return next((message for message in self.messages if message.id == message_id), None)

    async def list_by_conversation(
        self,
        conversation_id: UUID,
        limit: int = 50,
        before_message_id: UUID | None = None,
    ) -> list[Message]:
        messages = [message for message in self.messages if message.conversation_id == conversation_id]
        if before_message_id:
            before = await self.find_by_id(before_message_id)
            if before:
                messages = [message for message in messages if message.sent_at < before.sent_at]
        return messages[:limit]


class FakeMediaRepo:
    def __init__(self, media: list[MessageMedia] | None = None) -> None:
        self.media = media or []
        self.created: list[MessageMedia] = []
        self.attached: list[tuple[UUID, UUID]] = []

    async def create(self, media: MessageMedia) -> MessageMedia:
        self.created.append(media)
        self.media.append(media)
        return media

    async def find_by_id(self, media_id: UUID) -> MessageMedia | None:
        return next((media for media in self.media if media.id == media_id), None)

    async def find_by_message(self, message_id: UUID) -> MessageMedia | None:
        return next((media for media in self.media if media.message_id == message_id), None)

    async def attach_to_message(self, media_id: UUID, message_id: UUID) -> MessageMedia:
        media = await self.find_by_id(media_id)
        if media is None:
            raise ValueError("missing media")
        media.message_id = message_id
        media.upload_status = MediaUploadStatus.UPLOADED
        self.attached.append((media_id, message_id))
        return media


class FakeCallRepo:
    def __init__(self, calls: list[VoiceCall] | None = None) -> None:
        self.calls = calls or []
        self.created: list[VoiceCall] = []
        self.updated: list[VoiceCall] = []
        self.signals: list[tuple[UUID, UUID, str, dict[str, Any]]] = []

    async def create(self, call: VoiceCall) -> VoiceCall:
        self.created.append(call)
        self.calls.append(call)
        return call

    async def find_by_id(self, call_id: UUID) -> VoiceCall | None:
        return next((call for call in self.calls if call.id == call_id), None)

    async def update(self, call: VoiceCall) -> VoiceCall:
        self.updated.append(call)
        return call

    async def save_signal(
        self,
        call_id: UUID,
        sender_participant_id: UUID,
        signal_type: str,
        payload: dict[str, Any],
    ) -> None:
        self.signals.append((call_id, sender_participant_id, signal_type, payload))


class FakeDriverLookupSession:
    def __init__(self, driver_id: UUID | None = DRIVER_ID) -> None:
        self.driver_id = driver_id
        self.commits = 0
        self.rollbacks = 0

    async def execute(self, statement: Any, params: dict[str, Any]) -> Any:
        driver_id = self.driver_id if params.get("uid") == DRIVER_USER_ID else None

        class Result:
            def fetchone(self_inner: Any) -> tuple[UUID] | None:
                return (driver_id,) if driver_id else None

        return Result()

    async def commit(self) -> None:
        self.commits += 1

    async def rollback(self) -> None:
        self.rollbacks += 1


class StubUseCase:
    def __init__(self, response: Any = None, exc: Exception | None = None) -> None:
        self.response = response
        self.exc = exc
        self.calls: list[tuple[Any, ...]] = []

    async def execute(self, *args: Any, **kwargs: Any) -> Any:
        self.calls.append((*args, kwargs))
        if self.exc:
            raise self.exc
        return self.response


@asynccontextmanager
async def noop_lifespan(app: FastAPI):
    yield


@pytest.fixture
def communication_app() -> FastAPI:
    app = FastAPI(lifespan=noop_lifespan)
    app.include_router(communication_router, prefix="/api/v1")
    app.state.settings = type("Settings", (), {"WEBRTC_ICE_SERVERS_JSON": None})()
    app.dependency_overrides[get_current_user] = lambda: token(PASSENGER_ID)
    app.dependency_overrides[get_current_user_ws] = lambda: token(PASSENGER_ID)
    app.dependency_overrides[get_optional_driver_id] = lambda: None
    app.dependency_overrides[get_async_session] = lambda: FakeDriverLookupSession()
    return app


@pytest.fixture
def communication_client(communication_app: FastAPI) -> TestClient:
    return TestClient(communication_app)
