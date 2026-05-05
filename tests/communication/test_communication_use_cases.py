from __future__ import annotations

# ruff: noqa: E402,I001

from typing import Any, cast

import pytest

from communication.application.schemas import MediaUploadUrlRequest, SendTextMessageRequest
from communication.application.use_cases import (
    CloseConversationFromRideUseCase,
    ConversationAccessUseCase,
    EndCallUseCase,
    GenerateMediaUploadUrlUseCase,
    GetIceServersUseCase,
    GetMediaUrlUseCase,
    ListConversationsUseCase,
    OpenConversationFromRideUseCase,
    RegisterMediaMessageUseCase,
    SendTextMessageUseCase,
    SignalingUseCase,
    StartCallUseCase,
)
from communication.domain.exceptions import (
    ConversationClosedError,
    InvalidCallTransitionError,
    MediaUploadError,
    UnauthorisedConversationAccessError,
)
from communication.domain.models import CallStatus, ConversationStatus, MediaType, MessageType, VoiceCall
from communication.infrastructure.websocket_manager import CommunicationEvent

from tests.communication.conftest import (
    CONVERSATION_ID,
    DRIVER_ID,
    DRIVER_USER_ID,
    PASSENGER_ID,
    RIDE_ID,
    FakeCache,
    FakeCallRepo,
    FakeConversationRepo,
    FakeMediaRepo,
    FakeMessageRepo,
    FakeParticipantRepo,
    FakeStorage,
    FakeWsManager,
    make_conversation,
    make_media,
    make_message,
    make_participants,
)


@pytest.mark.asyncio
async def test_conversation_domain_and_call_transition_guards() -> None:
    conversation = make_conversation()
    conversation.ensure_active()
    conversation.close()
    assert conversation.status == ConversationStatus.CLOSED
    with pytest.raises(ConversationClosedError):
        conversation.ensure_active()

    passenger, driver = make_participants(conversation)
    message = make_message(conversation, passenger)
    assert message.message_type == MessageType.TEXT
    assert message.sender_participant_id == passenger.id
    assert driver.driver_id == DRIVER_ID

    call = VoiceCall.start(conversation.id, passenger.id, driver.id)
    call.accept()
    assert call.status == CallStatus.ACCEPTED
    call.finish(CallStatus.ENDED, "done")
    assert call.end_reason == "done"
    with pytest.raises(InvalidCallTransitionError):
        call.finish(CallStatus.MISSED)


@pytest.mark.asyncio
async def test_open_conversation_from_ride_is_idempotent_and_resolves_driver_user() -> None:
    repo = FakeConversationRepo()
    cache = FakeCache()
    ws = FakeWsManager()
    uc = OpenConversationFromRideUseCase(repo, cast(Any, cache), ws)  # type: ignore[arg-type]

    response = await uc.execute(RIDE_ID, PASSENGER_ID, DRIVER_ID)

    assert response.service_request_id == RIDE_ID
    assert response.passenger_user_id == PASSENGER_ID
    assert response.driver_id == DRIVER_ID
    assert response.driver_user_id == DRIVER_USER_ID
    assert len(repo.created) == 1
    assert ws.broadcasts[0][1] == "CONVERSATION_OPENED"
    assert cache.deleted_if_equals[0][1] == f"conversation:create:{RIDE_ID}"

    again = await uc.execute(RIDE_ID, PASSENGER_ID, DRIVER_ID)
    assert again.id == response.id
    assert len(repo.created) == 1


@pytest.mark.asyncio
async def test_open_conversation_rejects_driver_without_auth_user() -> None:
    uc = OpenConversationFromRideUseCase(
        FakeConversationRepo(driver_user_id=None),  # type: ignore[arg-type]
        cast(Any, FakeCache()),
        FakeWsManager(),  # type: ignore[arg-type]
    )

    with pytest.raises(UnauthorisedConversationAccessError):
        await uc.execute(RIDE_ID, PASSENGER_ID, DRIVER_ID)


@pytest.mark.asyncio
async def test_close_conversation_from_ride_broadcasts_and_missing_is_noop() -> None:
    conversation = make_conversation()
    repo = FakeConversationRepo(conversation)
    ws = FakeWsManager()
    response = await CloseConversationFromRideUseCase(repo, ws).execute(RIDE_ID)  # type: ignore[arg-type]

    assert response is not None
    assert response.status == ConversationStatus.CLOSED
    assert ws.broadcasts[0][1] == "CONVERSATION_CLOSED"

    missing = await CloseConversationFromRideUseCase(FakeConversationRepo(), ws).execute(RIDE_ID)  # type: ignore[arg-type]
    assert missing is None


@pytest.mark.asyncio
async def test_access_and_list_conversations_keep_passenger_and_driver_identities_separate() -> None:
    conversation = make_conversation()
    conversation_repo = FakeConversationRepo(conversation)
    participant_repo = FakeParticipantRepo(conversation)
    access = ConversationAccessUseCase(conversation_repo, participant_repo)  # type: ignore[arg-type]

    _, passenger = await access.assert_participant(CONVERSATION_ID, PASSENGER_ID, None)
    _, driver = await access.assert_participant(CONVERSATION_ID, DRIVER_USER_ID, DRIVER_ID)

    assert passenger.user_id == PASSENGER_ID
    assert passenger.driver_id is None
    assert driver.user_id == DRIVER_USER_ID
    assert driver.driver_id == DRIVER_ID

    with pytest.raises(UnauthorisedConversationAccessError):
        await access.assert_participant(CONVERSATION_ID, DRIVER_USER_ID, None)
    with pytest.raises(UnauthorisedConversationAccessError):
        await access.assert_participant(CONVERSATION_ID, PASSENGER_ID, DRIVER_ID)

    responses = await ListConversationsUseCase(conversation_repo).execute(  # type: ignore[arg-type]
        DRIVER_USER_ID,
        DRIVER_ID,
        ConversationStatus.ACTIVE,
        10,
        2,
    )
    assert responses[0].driver_user_id == DRIVER_USER_ID
    assert conversation_repo.find_actor_calls[0] == (DRIVER_USER_ID, DRIVER_ID, ConversationStatus.ACTIVE, 10, 2)


@pytest.mark.asyncio
async def test_text_message_creation_requires_active_participant_and_broadcasts() -> None:
    conversation = make_conversation()
    access = ConversationAccessUseCase(FakeConversationRepo(conversation), FakeParticipantRepo(conversation))  # type: ignore[arg-type]
    message_repo = FakeMessageRepo()
    ws = FakeWsManager()
    uc = SendTextMessageUseCase(access, message_repo, ws)  # type: ignore[arg-type]

    response = await uc.execute(CONVERSATION_ID, SendTextMessageRequest(body="hello"), PASSENGER_ID, None)

    assert response.body == "hello"
    assert message_repo.created[0].sender_participant_id == make_participants(conversation)[0].id
    assert ws.broadcasts[0][1] == CommunicationEvent.MESSAGE_SENT

    conversation.close()
    with pytest.raises(ConversationClosedError):
        await uc.execute(CONVERSATION_ID, SendTextMessageRequest(body="closed"), PASSENGER_ID, None)


@pytest.mark.asyncio
async def test_media_upload_validation_and_registration_for_image_and_voice_note() -> None:
    conversation = make_conversation()
    participant_repo = FakeParticipantRepo(conversation)
    access = ConversationAccessUseCase(FakeConversationRepo(conversation), participant_repo)  # type: ignore[arg-type]
    media_repo = FakeMediaRepo()
    storage = FakeStorage()
    upload_uc = GenerateMediaUploadUrlUseCase(access, media_repo, storage)  # type: ignore[arg-type]

    image = await upload_uc.execute(
        CONVERSATION_ID,
        MediaUploadUrlRequest(
            media_type=MediaType.IMAGE,
            file_name="photo.png",
            mime_type="image/png",
            file_size_bytes=100,
            duration_seconds=None,
            checksum_sha256=None,
        ),
        PASSENGER_ID,
        None,
    )
    voice = await upload_uc.execute(
        CONVERSATION_ID,
        MediaUploadUrlRequest(
            media_type=MediaType.VOICE_NOTE,
            file_name=None,
            mime_type="audio/ogg",
            file_size_bytes=None,
            duration_seconds=20,
            checksum_sha256=None,
        ),
        DRIVER_USER_ID,
        DRIVER_ID,
    )

    assert image.media_type == MediaType.IMAGE
    assert voice.media_type == MediaType.VOICE_NOTE
    assert storage.puts[0][1] == "image/png"
    assert storage.puts[1][1] == "audio/ogg"

    for request in [
        MediaUploadUrlRequest(
            media_type=MediaType.IMAGE,
            file_name=None,
            mime_type="image/gif",
            file_size_bytes=None,
            duration_seconds=None,
            checksum_sha256=None,
        ),
        MediaUploadUrlRequest(
            media_type=MediaType.IMAGE,
            file_name=None,
            mime_type="image/png",
            file_size_bytes=11 * 1024 * 1024,
            duration_seconds=None,
            checksum_sha256=None,
        ),
        MediaUploadUrlRequest(
            media_type=MediaType.VOICE_NOTE,
            file_name=None,
            mime_type="audio/wav",
            file_size_bytes=None,
            duration_seconds=None,
            checksum_sha256=None,
        ),
        MediaUploadUrlRequest(
            media_type=MediaType.VOICE_NOTE,
            file_name=None,
            mime_type="audio/ogg",
            file_size_bytes=None,
            duration_seconds=301,
            checksum_sha256=None,
        ),
    ]:
        with pytest.raises(MediaUploadError):
            await upload_uc.execute(CONVERSATION_ID, request, PASSENGER_ID, None)

    message_repo = FakeMessageRepo()
    ws = FakeWsManager()
    register_uc = RegisterMediaMessageUseCase(access, message_repo, media_repo, ws)  # type: ignore[arg-type]
    registered = await register_uc.execute(CONVERSATION_ID, image.media_id, PASSENGER_ID, None)

    assert registered.message.message_type == MessageType.IMAGE
    assert media_repo.attached[0][0] == image.media_id
    assert ws.broadcasts[0][1] == CommunicationEvent.MEDIA_MESSAGE_SENT

    with pytest.raises(MediaUploadError):
        await register_uc.execute(CONVERSATION_ID, voice.media_id, PASSENGER_ID, None)


@pytest.mark.asyncio
async def test_get_media_url_requires_participant_and_existing_media() -> None:
    conversation = make_conversation()
    passenger, _ = make_participants(conversation)
    message = make_message(conversation, passenger)
    media = make_media(conversation, passenger)
    media.message_id = message.id
    access = ConversationAccessUseCase(FakeConversationRepo(conversation), FakeParticipantRepo(conversation))  # type: ignore[arg-type]
    storage = FakeStorage()
    uc = GetMediaUrlUseCase(access, FakeMessageRepo([message]), FakeMediaRepo([media]), storage)  # type: ignore[arg-type]

    response = await uc.execute(message.id, PASSENGER_ID, None)

    assert response.media_id == media.id
    assert response.view_url.endswith(media.file_key)
    assert storage.gets[0] == (media.file_key, 3600)


@pytest.mark.asyncio
async def test_call_lifecycle_and_signaling_broadcasts() -> None:
    conversation = make_conversation()
    participant_repo = FakeParticipantRepo(conversation)
    access = ConversationAccessUseCase(FakeConversationRepo(conversation), participant_repo)  # type: ignore[arg-type]
    call_repo = FakeCallRepo()
    ws = FakeWsManager()

    call_response = await StartCallUseCase(access, participant_repo, call_repo, ws).execute(  # type: ignore[arg-type]
        CONVERSATION_ID,
        PASSENGER_ID,
        None,
        {"sdp": "offer"},
    )
    call = call_repo.calls[0]

    assert call_response.status == CallStatus.RINGING
    assert call_repo.signals[0][2] == "OFFER"
    assert ws.broadcasts[0][1] == CommunicationEvent.CALL_RINGING

    await SignalingUseCase(access, call_repo, ws).relay(  # type: ignore[arg-type]
        CONVERSATION_ID,
        call.id,
        "ANSWER",
        {"sdp": "answer"},
        DRIVER_USER_ID,
        DRIVER_ID,
    )
    assert call.status == CallStatus.ACCEPTED
    assert call_repo.signals[-1][2] == "ANSWER"
    assert ws.broadcasts[-1][1] == CommunicationEvent.WEBRTC_ANSWER

    ended = await EndCallUseCase(call_repo, access, ws).execute(  # type: ignore[arg-type]
        call.id,
        PASSENGER_ID,
        None,
        CallStatus.ENDED,
        "normal",
    )
    assert ended.status == CallStatus.ENDED
    assert ws.broadcasts[-1][1] == CommunicationEvent.CALL_ENDED


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        (None, [{"urls": ["stun:stun.l.google.com:19302"]}]),
        ('{"urls":["turn:example.test"]}', [{"urls": ["turn:example.test"]}]),
        ('[{"urls":["stun:a"]},{"urls":["turn:b"]}]', [{"urls": ["stun:a"]}, {"urls": ["turn:b"]}]),
        ("not json", [{"urls": ["stun:stun.l.google.com:19302"]}]),
    ],
)
async def test_ice_server_parsing(raw: str | None, expected: list[dict[str, Any]]) -> None:
    assert (await GetIceServersUseCase(raw).execute()).ice_servers == expected
