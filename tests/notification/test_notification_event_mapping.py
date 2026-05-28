from __future__ import annotations

from uuid import uuid4

from notification.application.use_cases import _requests_from_event
from sp.infrastructure.messaging.events import BaseEvent


def test_communication_message_event_maps_to_communication_deeplink() -> None:
    recipient_id = uuid4()
    ride_id = uuid4()
    event = BaseEvent(
        event_type="communication.message_sent",
        payload={"recipient_id": str(recipient_id), "ride_id": str(ride_id)},
    )

    requests = _requests_from_event(event)

    assert len(requests) == 1
    assert requests[0]["user_id"] == recipient_id
    assert requests[0]["deeplink"] == f"safarpay://communication/rides/{ride_id}"


def test_communication_call_event_accepts_legacy_underscore_name() -> None:
    recipient_id = uuid4()
    ride_id = uuid4()
    event = BaseEvent(
        event_type="communication.call_started",
        payload={"recipient_id": str(recipient_id), "ride_id": str(ride_id)},
    )

    requests = _requests_from_event(event)

    assert len(requests) == 1
    assert requests[0]["title"] == "Incoming ride call"
    assert requests[0]["user_id"] == recipient_id
