from __future__ import annotations

from uuid import uuid4

import pytest
from notification.domain.models import Notification, NotificationChannel, NotificationType
from notification.infrastructure.push_client import PushClient


class _Credentials:
    project_id = "safarpay-test"
    token = "oauth-token"
    valid = True

    def refresh(self, request: object) -> None:
        raise AssertionError("valid credentials should not be refreshed")


class _Response:
    status_code = 200
    text = "{}"


class _AsyncClient:
    calls: list[dict[str, object]] = []

    def __init__(self, *args: object, **kwargs: object) -> None:
        pass

    async def __aenter__(self) -> _AsyncClient:
        return self

    async def __aexit__(self, *args: object) -> None:
        return None

    async def post(
        self,
        url: str,
        *,
        json: dict[str, object],
        headers: dict[str, str],
    ) -> _Response:
        self.calls.append({"url": url, "json": json, "headers": headers})
        return _Response()


@pytest.mark.asyncio
async def test_push_client_sends_fcm_v1_with_service_account_credentials(monkeypatch) -> None:
    _AsyncClient.calls.clear()
    monkeypatch.setattr("notification.infrastructure.push_client.httpx.AsyncClient", _AsyncClient)
    notification = Notification.create(
        user_id=uuid4(),
        title="New ride request",
        message="A passenger request is available near you.",
        channel=NotificationChannel.PUSH,
        type=NotificationType.TRIP,
        metadata={"ride_id": uuid4()},
        deeplink="safarpay://driver/requests",
    )
    client = PushClient(credentials=_Credentials())

    sent = await client.send_to_token("fcm-token", notification)

    assert sent is True
    assert len(_AsyncClient.calls) == 1
    call = _AsyncClient.calls[0]
    assert call["url"] == "https://fcm.googleapis.com/v1/projects/safarpay-test/messages:send"
    assert call["headers"] == {
        "Authorization": "Bearer oauth-token",
        "Content-Type": "application/json",
    }
    payload = call["json"]
    assert payload["message"]["token"] == "fcm-token"  # type: ignore[index]
    assert payload["message"]["android"]["priority"] == "HIGH"  # type: ignore[index]
    assert payload["message"]["data"]["deeplink"] == "safarpay://driver/requests"  # type: ignore[index]


@pytest.mark.asyncio
async def test_push_client_marks_driver_ride_requests_as_urgent_android_alerts(monkeypatch) -> None:
    _AsyncClient.calls.clear()
    monkeypatch.setattr("notification.infrastructure.push_client.httpx.AsyncClient", _AsyncClient)
    ride_id = uuid4()
    notification = Notification.create(
        user_id=uuid4(),
        title="New ride request",
        message="PKR 540 from Liberty Market",
        channel=NotificationChannel.PUSH,
        type=NotificationType.TRIP,
        metadata={
            "notification_kind": "driver_ride_request",
            "ride_id": ride_id,
            "pricing_mode": "hybrid",
        },
        deeplink=f"safarpay://driver/requests/{ride_id}",
    )
    client = PushClient(credentials=_Credentials())

    sent = await client.send_to_token("fcm-token", notification)

    assert sent is True
    payload = _AsyncClient.calls[0]["json"]
    message = payload["message"]  # type: ignore[index]
    android = message["android"]
    assert "notification" not in message
    assert message["data"]["title"] == "New ride request"
    assert message["data"]["body"] == "PKR 540 from Liberty Market"
    assert android["priority"] == "HIGH"
    assert android["ttl"] == "45s"
    assert android["collapse_key"] == f"driver_ride_request:{ride_id}"
    assert "notification" not in android


@pytest.mark.asyncio
async def test_push_client_marks_communication_calls_as_urgent_call_alerts(monkeypatch) -> None:
    _AsyncClient.calls.clear()
    monkeypatch.setattr("notification.infrastructure.push_client.httpx.AsyncClient", _AsyncClient)
    ride_id = uuid4()
    call_id = uuid4()
    notification = Notification.create(
        user_id=uuid4(),
        title="Incoming ride call",
        message="Passenger is calling",
        channel=NotificationChannel.PUSH,
        type=NotificationType.SYSTEM,
        metadata={
            "notification_kind": "communication_call",
            "ride_id": ride_id,
            "call_id": call_id,
            "present_as_call": True,
        },
        deeplink=f"safarpay://communication/rides/{ride_id}",
    )
    client = PushClient(credentials=_Credentials())

    sent = await client.send_to_token("fcm-token", notification)

    assert sent is True
    payload = _AsyncClient.calls[0]["json"]
    message = payload["message"]  # type: ignore[index]
    android = message["android"]
    assert "notification" not in message
    assert message["data"]["title"] == "Incoming ride call"
    assert message["data"]["body"] == "Passenger is calling"
    assert android["priority"] == "HIGH"
    assert android["ttl"] == "30s"
    assert android["collapse_key"] == f"communication_call:{call_id}"
    assert "notification" not in android
