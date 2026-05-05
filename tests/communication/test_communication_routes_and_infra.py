from __future__ import annotations

# ruff: noqa: E402,I001

import json
from datetime import datetime, timezone
from typing import Any, cast
from uuid import UUID, uuid4

import pytest
from botocore.exceptions import ClientError
from fastapi import FastAPI

from communication.api.router import _resolve_driver_id
from communication.application.use_cases import _call_to_resp, _conversation_to_resp, _message_to_resp
from communication.domain.exceptions import (
    CallNotFoundError,
    ConversationClosedError,
    ConversationNotFoundError,
    MediaUploadError,
    MessageNotFoundError,
    UnauthorisedConversationAccessError,
)
from communication.domain.models import VoiceCall
from communication.infrastructure import kafka_consumer as consumer_module
from communication.infrastructure import storage as storage_module
from communication.infrastructure.dependencies import (
    get_end_call_uc,
    get_get_conversation_uc,
    get_list_conversations_uc,
    get_list_messages_uc,
    get_media_upload_uc,
    get_media_url_uc,
    get_register_media_uc,
    get_send_text_uc,
    get_start_call_uc,
)
from communication.infrastructure.orm_models import CommunicationEventORM, CommunicationEventType
from communication.infrastructure.storage import S3StorageProvider, build_media_key
from communication.infrastructure.websocket_manager import CommunicationEvent, WebSocketManager
from sp.infrastructure.messaging.outbox import GenericOutboxWorker
from sp.infrastructure.security.dependencies import get_current_user, get_optional_driver_id

from tests.communication.conftest import (
    CONVERSATION_ID,
    DRIVER_ID,
    DRIVER_USER_ID,
    PASSENGER_ID,
    RIDE_ID,
    FakeDriverLookupSession,
    StubUseCase,
    make_conversation,
    make_media,
    make_message,
    make_participants,
    token,
)


def override(app: FastAPI, dependency: Any, value: Any) -> Any:
    app.dependency_overrides[dependency] = lambda: value
    return value


def test_all_communication_http_routes_success_and_identity_parameters(
    communication_app: FastAPI,
    communication_client: Any,
) -> None:
    conversation = make_conversation()
    passenger, driver = make_participants(conversation)
    message = make_message(conversation, passenger)
    media = make_media(conversation, passenger)
    media.message_id = message.id
    call = VoiceCall.start(conversation.id, passenger.id, driver.id)

    list_conversations = override(communication_app, get_list_conversations_uc, StubUseCase([_conversation_to_resp(conversation)]))
    get_conversation = override(communication_app, get_get_conversation_uc, StubUseCase(_conversation_to_resp(conversation)))
    list_messages = override(communication_app, get_list_messages_uc, StubUseCase([_message_to_resp(message)]))
    send_text = override(communication_app, get_send_text_uc, StubUseCase(_message_to_resp(message)))
    upload = override(
        communication_app,
        get_media_upload_uc,
        StubUseCase(
            {
                "media_id": media.id,
                "presigned_url": "https://s3.test/put",
                "file_key": media.file_key,
                "expires_in_seconds": 900,
                "media_type": media.media_type,
                "mime_type": media.mime_type,
            }
        ),
    )
    register = override(
        communication_app,
        get_register_media_uc,
        StubUseCase(
            {
                "message": _message_to_resp(message),
                "media_id": media.id,
                "file_key": media.file_key,
                "media_type": media.media_type,
                "mime_type": media.mime_type,
            }
        ),
    )
    get_url = override(
        communication_app,
        get_media_url_uc,
        StubUseCase({"message_id": message.id, "media_id": media.id, "view_url": "https://s3.test/get", "expires_in_seconds": 3600}),
    )
    start_call = override(communication_app, get_start_call_uc, StubUseCase(_call_to_resp(call)))
    end_call = override(communication_app, get_end_call_uc, StubUseCase(_call_to_resp(call)))

    assert communication_client.get("/api/v1/communication/conversations").status_code == 200
    assert communication_client.get(f"/api/v1/communication/conversations/{conversation.id}").status_code == 200
    assert communication_client.get(f"/api/v1/communication/conversations/{conversation.id}/messages").status_code == 200
    assert communication_client.post(
        f"/api/v1/communication/conversations/{conversation.id}/messages",
        json={"body": "hello"},
    ).status_code == 201
    assert communication_client.post(
        f"/api/v1/communication/conversations/{conversation.id}/media/upload-url",
        json={"media_type": "IMAGE", "mime_type": "image/png", "file_name": "photo.png"},
    ).status_code == 200
    assert communication_client.post(
        f"/api/v1/communication/conversations/{conversation.id}/messages/media",
        json={"media_id": str(media.id)},
    ).status_code == 201
    assert communication_client.get(f"/api/v1/communication/messages/{message.id}/media-url").status_code == 200
    assert communication_client.post(
        f"/api/v1/communication/conversations/{conversation.id}/calls",
        json={"initial_offer": {"sdp": "offer"}},
    ).status_code == 201
    assert communication_client.post(
        f"/api/v1/communication/calls/{call.id}/end",
        json={"status": "ENDED", "reason": "normal"},
    ).status_code == 200

    assert list_conversations.calls[0][:2] == (PASSENGER_ID, None)
    assert get_conversation.calls[0][1:3] == (PASSENGER_ID, None)
    assert list_messages.calls[0][1:3] == (PASSENGER_ID, None)
    assert send_text.calls[0][2:4] == (PASSENGER_ID, None)
    assert upload.calls[0][2:4] == (PASSENGER_ID, None)
    assert register.calls[0][2:4] == (PASSENGER_ID, None)
    assert get_url.calls[0][1:3] == (PASSENGER_ID, None)
    assert start_call.calls[0][1:3] == (PASSENGER_ID, None)
    assert end_call.calls[0][1:3] == (PASSENGER_ID, None)


def test_driver_and_passenger_route_dependencies_remain_separate(
    communication_app: FastAPI,
    communication_client: Any,
) -> None:
    conversation = make_conversation()
    communication_app.dependency_overrides[get_current_user] = lambda: token(DRIVER_USER_ID, role="driver")
    communication_app.dependency_overrides[get_optional_driver_id] = lambda: DRIVER_ID
    get_conversation = override(communication_app, get_get_conversation_uc, StubUseCase(_conversation_to_resp(conversation)))

    response = communication_client.get(f"/api/v1/communication/conversations/{conversation.id}")

    assert response.status_code == 200
    assert get_conversation.calls[0][1:3] == (DRIVER_USER_ID, DRIVER_ID)
    assert get_conversation.calls[0][1] != get_conversation.calls[0][2]


@pytest.mark.parametrize(
    ("dependency", "exc", "method", "path", "body", "status_code"),
    [
        (get_get_conversation_uc, ConversationNotFoundError("missing"), "get", f"/api/v1/communication/conversations/{CONVERSATION_ID}", None, 404),
        (get_list_messages_uc, MessageNotFoundError("missing"), "get", f"/api/v1/communication/conversations/{CONVERSATION_ID}/messages", None, 404),
        (get_send_text_uc, UnauthorisedConversationAccessError("forbidden"), "post", f"/api/v1/communication/conversations/{CONVERSATION_ID}/messages", {"body": "hi"}, 403),
        (get_send_text_uc, ConversationClosedError("closed"), "post", f"/api/v1/communication/conversations/{CONVERSATION_ID}/messages", {"body": "hi"}, 409),
        (get_media_upload_uc, MediaUploadError("bad media"), "post", f"/api/v1/communication/conversations/{CONVERSATION_ID}/media/upload-url", {"media_type": "IMAGE", "mime_type": "image/gif"}, 422),
        (get_start_call_uc, CallNotFoundError("bad call"), "post", f"/api/v1/communication/conversations/{CONVERSATION_ID}/calls", {}, 404),
    ],
)
def test_communication_route_error_mappings(
    communication_app: FastAPI,
    communication_client: Any,
    dependency: Any,
    exc: Exception,
    method: str,
    path: str,
    body: dict[str, Any] | None,
    status_code: int,
) -> None:
    override(communication_app, dependency, StubUseCase(exc=exc))

    response = getattr(communication_client, method)(path, json=body) if body is not None else getattr(communication_client, method)(path)

    assert response.status_code == status_code


def test_communication_schema_validation_errors(communication_app: FastAPI, communication_client: Any) -> None:
    override(communication_app, get_send_text_uc, StubUseCase())
    override(communication_app, get_media_upload_uc, StubUseCase())
    override(communication_app, get_end_call_uc, StubUseCase())

    assert communication_client.post(
        f"/api/v1/communication/conversations/{CONVERSATION_ID}/messages",
        json={"body": ""},
    ).status_code == 422
    assert communication_client.get("/api/v1/communication/conversations?limit=101").status_code == 422
    assert communication_client.post(
        f"/api/v1/communication/conversations/{CONVERSATION_ID}/media/upload-url",
        json={"media_type": "IMAGE", "mime_type": "image/png", "file_size_bytes": -1},
    ).status_code == 422
    assert communication_client.post(
        f"/api/v1/communication/calls/{uuid4()}/end",
        json={"status": "NOT_A_STATUS"},
    ).status_code == 422


def test_ice_servers_route_uses_settings(communication_app: FastAPI, communication_client: Any) -> None:
    communication_app.state.settings.WEBRTC_ICE_SERVERS_JSON = '{"urls":["turn:example.test"]}'

    response = communication_client.get("/api/v1/communication/webrtc/ice-servers")

    assert response.status_code == 200
    assert response.json() == {"ice_servers": [{"urls": ["turn:example.test"]}]}


class FakeSocket:
    def __init__(self, fail: bool = False) -> None:
        self.accepted = False
        self.fail = fail
        self.sent: list[str] = []

    async def accept(self) -> None:
        self.accepted = True

    async def send_text(self, message: str) -> None:
        if self.fail:
            raise RuntimeError("closed")
        self.sent.append(message)


@pytest.mark.asyncio
async def test_websocket_manager_connect_subscribe_broadcast_and_cleanup() -> None:
    manager = WebSocketManager()
    good = FakeSocket()
    stale = FakeSocket(fail=True)

    await manager.connect(PASSENGER_ID, cast(Any, good))
    await manager.connect(PASSENGER_ID, cast(Any, stale))
    await manager.subscribe(CONVERSATION_ID, cast(Any, good))
    await manager.subscribe(CONVERSATION_ID, cast(Any, stale))

    assert good.accepted is True
    subscribed = json.loads(good.sent[0])
    assert subscribed["event"] == CommunicationEvent.SUBSCRIBED

    delivered = await manager.broadcast_to_conversation(CONVERSATION_ID, CommunicationEvent.MESSAGE_SENT, {"body": "hi"})
    assert delivered == 1
    assert json.loads(good.sent[-1])["data"] == {"body": "hi"}

    await manager.disconnect(PASSENGER_ID, cast(Any, good))
    assert await manager.broadcast_to_conversation(CONVERSATION_ID, CommunicationEvent.MESSAGE_SENT, {}) == 0


@pytest.mark.asyncio
async def test_resolve_driver_id_returns_verification_driver_profile_only() -> None:
    assert await _resolve_driver_id(cast(Any, FakeDriverLookupSession(DRIVER_ID)), DRIVER_USER_ID) == DRIVER_ID
    assert await _resolve_driver_id(cast(Any, FakeDriverLookupSession(None)), PASSENGER_ID) is None


def test_build_media_key_uses_safe_extension_and_media_path() -> None:
    assert build_media_key(CONVERSATION_ID, "IMAGE", "photo.PNG").endswith(".png")
    assert build_media_key(CONVERSATION_ID, "VOICE_NOTE", "voice.ogg").endswith(".ogg")
    assert build_media_key(CONVERSATION_ID, "IMAGE", "bad.exe").endswith(".bin")
    assert f"conversations/{CONVERSATION_ID}/image/" in build_media_key(CONVERSATION_ID, "IMAGE", None)


@pytest.mark.asyncio
async def test_s3_storage_provider_uses_bucket_key_content_type_and_maps_client_errors(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[tuple[str, dict[str, Any], int]] = []

    class Settings:
        S3_COMMUNICATION_BUCKET = "communication-bucket"
        AWS_REGION = "us-east-1"

    class FakeS3:
        def generate_presigned_url(self, operation: str, Params: dict[str, Any], ExpiresIn: int) -> str:
            calls.append((operation, Params, ExpiresIn))
            return f"https://s3.test/{operation}/{Params['Key']}"

    monkeypatch.setattr(storage_module, "get_settings", lambda: Settings())
    monkeypatch.setattr(storage_module.boto3, "client", lambda *args, **kwargs: FakeS3())
    provider = S3StorageProvider()

    assert await provider.generate_presigned_put_url("k.png", content_type="image/png") == "https://s3.test/put_object/k.png"
    assert await provider.generate_presigned_get_url("k.png") == "https://s3.test/get_object/k.png"
    assert calls[0] == ("put_object", {"Bucket": "communication-bucket", "Key": "k.png", "ContentType": "image/png"}, 900)
    assert calls[1] == ("get_object", {"Bucket": "communication-bucket", "Key": "k.png"}, 3600)

    class BrokenS3:
        def generate_presigned_url(self, operation: str, Params: dict[str, Any], ExpiresIn: int) -> str:
            raise ClientError({"Error": {"Code": "500", "Message": "boom"}}, operation)

    monkeypatch.setattr(storage_module.boto3, "client", lambda *args, **kwargs: BrokenS3())
    broken = S3StorageProvider()
    with pytest.raises(RuntimeError):
        await broken.generate_presigned_put_url("k.png", content_type="image/png")


@pytest.mark.asyncio
async def test_kafka_consumer_opens_and_closes_conversations_from_ride_events(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[tuple[str, UUID, UUID | None, UUID | None]] = []

    class FakeKafka:
        def __init__(self, *args: Any, **kwargs: Any) -> None:
            pass

        def close(self) -> None:
            pass

    class FakeOpen:
        def __init__(self, repo: Any, cache: Any, ws: Any) -> None:
            pass

        async def execute(self, ride_id: UUID, passenger_user_id: UUID, driver_id: UUID) -> None:
            calls.append(("open", ride_id, passenger_user_id, driver_id))

    class FakeClose:
        def __init__(self, repo: Any, ws: Any) -> None:
            pass

        async def execute(self, ride_id: UUID) -> None:
            calls.append(("close", ride_id, None, None))

    class Session:
        async def __aenter__(self) -> Any:
            return self

        async def __aexit__(self, exc_type: Any, exc: Any, tb: Any) -> bool:
            return False

        async def commit(self) -> None:
            calls.append(("commit", UUID(int=0), None, None))

        async def rollback(self) -> None:
            calls.append(("rollback", UUID(int=0), None, None))

    monkeypatch.setattr(consumer_module, "KafkaConsumerWrapper", FakeKafka)
    monkeypatch.setattr(consumer_module, "ConversationRepository", lambda session: object())
    monkeypatch.setattr(consumer_module, "OpenConversationFromRideUseCase", FakeOpen)
    monkeypatch.setattr(consumer_module, "CloseConversationFromRideUseCase", FakeClose)

    consumer = consumer_module.CommunicationKafkaConsumer("localhost:9092", cast(Any, lambda: Session()), cast(Any, object()), cast(Any, object()))
    await consumer._process_message(
        {
            "value": {
                "event_type": "service.request.accepted",
                "payload": {"ride_id": str(RIDE_ID), "passenger_user_id": str(PASSENGER_ID), "driver_id": str(DRIVER_ID)},
            }
        }
    )
    await consumer._process_message({"value": {"event_type": "service.request.completed", "payload": {"ride_id": str(RIDE_ID)}}})
    await consumer._process_message({"value": {"event_type": "service.request.accepted", "payload": {"ride_id": "bad"}}})

    assert calls[0] == ("open", RIDE_ID, PASSENGER_ID, DRIVER_ID)
    assert calls[2] == ("close", RIDE_ID, None, None)


@pytest.mark.asyncio
async def test_outbox_worker_publishes_pending_events_and_tracks_failures() -> None:
    now = datetime.now(timezone.utc)

    class Event:
        def __init__(self, event_type: CommunicationEventType, aggregate_id: UUID, error_count: int = 0) -> None:
            self.id = uuid4()
            self.event_type = event_type.value
            self.aggregate_id = aggregate_id
            self.payload = {"aggregate_id": str(aggregate_id)}
            self.topic = "communication-events"
            self.correlation_id = None
            self.idempotency_key = None
            self.created_at = now
            self.processed_at: datetime | None = None
            self.error_count = error_count
            self.last_error: str | None = None

    pending = Event(CommunicationEventType.MESSAGE_SENT, uuid4())
    failing = Event(CommunicationEventType.CALL_STARTED, uuid4())

    class Scalars:
        def all(self) -> list[Event]:
            return [pending, failing]

    class Result:
        def scalars(self) -> Scalars:
            return Scalars()

    class Session:
        def __init__(self) -> None:
            self.commits = 0

        async def __aenter__(self) -> Any:
            return self

        async def __aexit__(self, exc_type: Any, exc: Any, tb: Any) -> bool:
            return False

        async def execute(self, stmt: Any) -> Result:
            return Result()

        async def commit(self) -> None:
            self.commits += 1

    session = Session()

    class Publisher:
        def __init__(self) -> None:
            self.published: list[str] = []

        async def publish_to_topic(self, topic: str, event: Any) -> bool:
            assert topic == "communication-events"
            self.published.append(event.event_type)
            if event.event_type.endswith("call.started"):
                raise RuntimeError("publish failed")
            return True

    publisher = Publisher()
    worker = GenericOutboxWorker(
        cast(Any, lambda: session),
        cast(Any, publisher),
        CommunicationEventORM,
        default_topic="communication-events",
        batch_size=10,
    )

    await worker.flush_once()

    assert publisher.published == ["communication.message.sent", "communication.call.started"]
    assert session.commits == 1
