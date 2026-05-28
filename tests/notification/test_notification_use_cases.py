from __future__ import annotations

from uuid import uuid4

import pytest
from notification.application.schemas import SendNotificationRequest
from notification.application.use_cases import SendNotificationUseCase
from notification.domain.models import Notification


class FakeRepo:
    def __init__(self) -> None:
        self.created: list[Notification] = []

    async def create(self, notification: Notification) -> Notification:
        self.created.append(notification)
        return notification


class FakePublisher:
    def __init__(self) -> None:
        self.events = []

    async def publish(self, event) -> None:
        self.events.append(event)


@pytest.mark.asyncio
async def test_send_notification_persists_inbox_item_and_publishes_recipient_payload() -> None:
    repo = FakeRepo()
    publisher = FakePublisher()
    user_id = uuid4()
    use_case = SendNotificationUseCase(repo, publisher=publisher)

    response = await use_case.execute(
        SendNotificationRequest(
            recipient_id=user_id,
            title="Driver assigned",
            message="Your driver is heading to pickup.",
            type="trip",
            idempotency_key="ride:accepted:1",
        )
    )

    assert response.user_id == user_id
    assert response.type == "trip"
    assert response.is_unread is True
    assert repo.created[0].idempotency_key == "ride:accepted:1"
    assert publisher.events[0].payload["recipient_id"] == str(user_id)
