from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import uuid4

from fastapi import FastAPI
from fastapi.testclient import TestClient
from notification.api.router import router
from notification.application.schemas import (
    NotificationListResponse,
    NotificationResponse,
    NotificationUnreadCountResponse,
)
from notification.domain.models import DevicePlatform, DeviceToken, Notification
from notification.infrastructure.dependencies import (
    get_device_token_repo,
    get_list_notifications_uc,
    get_mark_all_read_uc,
    get_mark_read_uc,
    get_notification_repo,
    get_push_client,
    get_unread_count_uc,
)
from sp.infrastructure.security.dependencies import get_current_user
from sp.infrastructure.security.jwt import TokenPayload


class StubUseCase:
    def __init__(self, response: Any) -> None:
        self.response = response
        self.calls: list[tuple[Any, ...]] = []

    async def execute(self, *args: Any, **kwargs: Any) -> Any:
        self.calls.append((*args, kwargs))
        return self.response


def token(user_id):
    now = datetime.now(timezone.utc)
    return TokenPayload(
        user_id=user_id,
        email="passenger@test.dev",
        role="passenger",
        session_id=uuid4(),
        iat=now,
        exp=now + timedelta(minutes=15),
    )


def test_inbox_routes_are_scoped_to_current_user() -> None:
    user_id = uuid4()
    notification_id = uuid4()
    item = NotificationResponse(
        id=notification_id,
        user_id=user_id,
        type="trip",
        title="Driver assigned",
        message="Your driver is heading to pickup.",
        channel="push",
        status="queued",
        created_at=datetime.now(timezone.utc),
        is_unread=True,
    )
    app = FastAPI()
    app.include_router(router, prefix="/api/v1/notification")
    app.dependency_overrides[get_current_user] = lambda: token(user_id)
    list_uc = StubUseCase(NotificationListResponse(data=[item], total=1, unread_count=1))
    count_uc = StubUseCase(NotificationUnreadCountResponse(unread_count=1))
    mark_uc = StubUseCase(item.model_copy(update={"read_at": datetime.now(timezone.utc), "is_unread": False}))
    mark_all_uc = StubUseCase(NotificationUnreadCountResponse(unread_count=0))
    app.dependency_overrides[get_list_notifications_uc] = lambda: list_uc
    app.dependency_overrides[get_unread_count_uc] = lambda: count_uc
    app.dependency_overrides[get_mark_read_uc] = lambda: mark_uc
    app.dependency_overrides[get_mark_all_read_uc] = lambda: mark_all_uc
    client = TestClient(app)

    assert client.get("/api/v1/notification/notifications").status_code == 200
    assert client.get("/api/v1/notification/notifications/unread-count").json() == {"unread_count": 1}
    assert client.post(f"/api/v1/notification/notifications/{notification_id}/read").status_code == 200
    assert client.post("/api/v1/notification/notifications/read-all").json() == {"unread_count": 0}

    assert list_uc.calls[0][0] == user_id
    assert mark_uc.calls[0][0:2] == (user_id, notification_id)


class NotificationRepoSpy:
    def __init__(self) -> None:
        self.created: list[Notification] = []

    async def create(self, notification: Notification) -> Notification:
        self.created.append(notification)
        return notification


class DeviceTokenRepoStub:
    def __init__(self, token: DeviceToken) -> None:
        self.token = token

    async def active_tokens_for_driver(self, driver_id):
        return [self.token]


class PushClientSpy:
    def __init__(self) -> None:
        self.sent: list[tuple[str, Notification]] = []

    async def send_to_token(self, token: str, notification: Notification) -> bool:
        self.sent.append((token, notification))
        return True


def test_internal_ride_job_persists_and_pushes_to_driver_user() -> None:
    user_id = uuid4()
    driver_id = uuid4()
    ride_id = uuid4()
    token_model = DeviceToken.register(
        user_id=user_id,
        driver_id=driver_id,
        token="driver-fcm-token",
        platform=DevicePlatform.ANDROID,
    )
    notification_repo = NotificationRepoSpy()
    push_client = PushClientSpy()
    app = FastAPI()
    app.include_router(router, prefix="/api/v1/notification")
    app.dependency_overrides[get_notification_repo] = lambda: notification_repo
    app.dependency_overrides[get_device_token_repo] = lambda: DeviceTokenRepoStub(token_model)
    app.dependency_overrides[get_push_client] = lambda: push_client
    client = TestClient(app)

    response = client.post(
        f"/api/v1/notification/internal/ride-jobs/{driver_id}",
        json={"ride_id": str(ride_id), "pickup": "Liberty Market"},
    )

    assert response.status_code == 200
    assert response.json() == {"ok": True}
    assert len(notification_repo.created) == 1
    notification = notification_repo.created[0]
    assert notification.user_id == user_id
    assert notification.deeplink == f"safarpay://driver/requests/{ride_id}"
    assert notification.metadata["notification_kind"] == "driver_ride_request"
    assert notification.metadata["driver_id"] == str(driver_id)
    assert notification.metadata["ride_id"] == str(ride_id)
    assert notification.metadata["present_as_driver_alert"] is True
    assert push_client.sent == [("driver-fcm-token", notification)]
