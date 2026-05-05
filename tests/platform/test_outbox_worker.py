from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, cast
from uuid import uuid4

import pytest
from ride.infrastructure.orm_models import RideOutboxEventORM
from sp.infrastructure.messaging.outbox import GenericOutboxWorker


@pytest.mark.asyncio
async def test_generic_outbox_worker_publishes_with_row_metadata_and_skip_locked() -> None:
    row_id = uuid4()
    row = type(
        "Row",
        (),
        {
            "id": row_id,
            "event_type": "service.request.accepted",
            "payload": {
                "ride_id": str(uuid4()),
                "passenger_user_id": str(uuid4()),
                "driver_id": str(uuid4()),
            },
            "topic": "ride-events",
            "correlation_id": "corr-1",
            "idempotency_key": "idem-1",
            "created_at": datetime.now(timezone.utc),
        },
    )()

    class Scalars:
        def all(self) -> list[Any]:
            return [row]

    class Result:
        def scalars(self) -> Scalars:
            return Scalars()

    class Session:
        def __init__(self) -> None:
            self.statements: list[Any] = []
            self.commits = 0

        async def __aenter__(self) -> Session:
            return self

        async def __aexit__(self, exc_type: Any, exc: Any, tb: Any) -> bool:
            return False

        async def execute(self, stmt: Any) -> Result:
            self.statements.append(stmt)
            return Result()

        async def commit(self) -> None:
            self.commits += 1

    session = Session()

    class Publisher:
        def __init__(self) -> None:
            self.calls: list[tuple[str, Any]] = []

        async def publish_to_topic(self, topic: str, event: Any) -> bool:
            self.calls.append((topic, event))
            return True

    publisher = Publisher()
    worker = GenericOutboxWorker(
        cast(Any, lambda: session),
        cast(Any, publisher),
        RideOutboxEventORM,
        default_topic="fallback",
    )

    assert await worker.flush_once() == 1

    select_stmt = session.statements[0]
    assert select_stmt._for_update_arg is not None
    assert select_stmt._for_update_arg.skip_locked is True
    assert publisher.calls[0][0] == "ride-events"
    assert publisher.calls[0][1].event_id == row_id
    assert publisher.calls[0][1].correlation_id == "corr-1"
    assert publisher.calls[0][1].idempotency_key == "idem-1"
    assert session.commits == 1
