from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

import pytest
from notification.domain.models import DevicePlatform, DeviceToken
from notification.infrastructure.orm_models import DevicePlatformORM, DeviceTokenORM
from notification.infrastructure.repositories import DeviceTokenRepository
from sqlalchemy.dialects import postgresql


class _ScalarResult:
    def __init__(self, orm: DeviceTokenORM) -> None:
        self._orm = orm

    def scalar_one(self) -> DeviceTokenORM:
        return self._orm


class _SessionSpy:
    def __init__(self, orm: DeviceTokenORM) -> None:
        self.orm = orm
        self.statements: list[object] = []
        self.flushed = False

    async def execute(self, statement: object) -> _ScalarResult:
        self.statements.append(statement)
        return _ScalarResult(self.orm)

    async def flush(self) -> None:
        self.flushed = True
        raise AssertionError("Device token upsert should be atomic and not select-then-flush")


@pytest.mark.asyncio
async def test_device_token_upsert_uses_atomic_postgres_conflict_update() -> None:
    now = datetime.now(timezone.utc)
    user_id = uuid4()
    driver_id = uuid4()
    existing_id = uuid4()
    token_value = "same-fcm-token"
    existing_orm = DeviceTokenORM(
        id=existing_id,
        user_id=user_id,
        driver_id=driver_id,
        token=token_value,
        platform=DevicePlatformORM.ANDROID,
        device_id="pixel-8",
        app_version="1.2.3",
        is_active=True,
        last_seen_at=now,
        created_at=now,
        updated_at=now,
    )
    session = _SessionSpy(existing_orm)
    repo = DeviceTokenRepository(session)  # type: ignore[arg-type]

    result = await repo.upsert(
        DeviceToken.register(
            user_id=user_id,
            driver_id=driver_id,
            token=token_value,
            platform=DevicePlatform.ANDROID,
            device_id="pixel-8",
            app_version="1.2.3",
        )
    )

    compiled = str(session.statements[0].compile(dialect=postgresql.dialect()))
    assert "ON CONFLICT ON CONSTRAINT uq_device_tokens_token DO UPDATE" in compiled
    assert result.id == existing_id
    assert result.token == token_value
    assert session.flushed is False
