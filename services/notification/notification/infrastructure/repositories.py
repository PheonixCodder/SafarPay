from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import func, select, update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from ..domain.models import (
    DevicePlatform,
    DeviceToken,
    Notification,
    NotificationChannel,
    NotificationStatus,
    NotificationType,
)
from .orm_models import (
    DevicePlatformORM,
    DeviceTokenORM,
    NotificationChannelORM,
    NotificationORM,
    NotificationStatusORM,
    NotificationTypeORM,
)


class NotificationNotFoundError(Exception):
    """Raised when a user-scoped notification is not found."""


class NotificationRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, notification: Notification) -> Notification:
        if notification.idempotency_key:
            existing = await self.find_by_idempotency_key(notification.idempotency_key)
            if existing:
                return existing
        orm = NotificationORM(
            id=notification.id,
            user_id=notification.user_id,
            type=NotificationTypeORM(notification.type.value),
            title=notification.title,
            message=notification.message,
            channel=NotificationChannelORM(notification.channel.value),
            status=NotificationStatusORM(notification.status.value),
            metadata_json=notification.metadata,
            source_service=notification.source_service,
            source_event_type=notification.source_event_type,
            source_event_id=notification.source_event_id,
            idempotency_key=notification.idempotency_key,
            deeplink=notification.deeplink,
            read_at=notification.read_at,
        )
        self._session.add(orm)
        await self._session.flush()
        return self._to_domain(orm)

    async def find_by_idempotency_key(self, idempotency_key: str) -> Notification | None:
        result = await self._session.execute(
            select(NotificationORM).where(NotificationORM.idempotency_key == idempotency_key)
        )
        orm = result.scalar_one_or_none()
        return self._to_domain(orm) if orm else None

    async def list_for_user(
        self,
        user_id: UUID,
        *,
        limit: int = 30,
        offset: int = 0,
        unread_only: bool = False,
    ) -> list[Notification]:
        stmt = select(NotificationORM).where(NotificationORM.user_id == user_id)
        if unread_only:
            stmt = stmt.where(NotificationORM.read_at.is_(None))
        stmt = stmt.order_by(NotificationORM.created_at.desc()).limit(limit).offset(offset)
        result = await self._session.execute(stmt)
        return [self._to_domain(orm) for orm in result.scalars().all()]

    async def count_for_user(self, user_id: UUID, *, unread_only: bool = False) -> int:
        stmt = select(func.count()).select_from(NotificationORM).where(NotificationORM.user_id == user_id)
        if unread_only:
            stmt = stmt.where(NotificationORM.read_at.is_(None))
        result = await self._session.execute(stmt)
        return int(result.scalar_one())

    async def unread_count(self, user_id: UUID) -> int:
        return await self.count_for_user(user_id, unread_only=True)

    async def mark_read(self, user_id: UUID, notification_id: UUID) -> Notification:
        now = datetime.now(timezone.utc)
        await self._session.execute(
            update(NotificationORM)
            .where(NotificationORM.id == notification_id, NotificationORM.user_id == user_id)
            .values(read_at=now)
        )
        await self._session.flush()
        result = await self._session.execute(
            select(NotificationORM).where(NotificationORM.id == notification_id, NotificationORM.user_id == user_id)
        )
        orm = result.scalar_one_or_none()
        if orm is None:
            raise NotificationNotFoundError("Notification not found")
        return self._to_domain(orm)

    async def mark_all_read(self, user_id: UUID) -> None:
        await self._session.execute(
            update(NotificationORM)
            .where(NotificationORM.user_id == user_id, NotificationORM.read_at.is_(None))
            .values(read_at=datetime.now(timezone.utc))
        )
        await self._session.flush()

    async def update_status(
        self,
        notification_id: UUID,
        status: NotificationStatus,
    ) -> Notification | None:
        await self._session.execute(
            update(NotificationORM)
            .where(NotificationORM.id == notification_id)
            .values(status=NotificationStatusORM(status.value))
        )
        await self._session.flush()
        result = await self._session.execute(
            select(NotificationORM).where(NotificationORM.id == notification_id)
        )
        orm = result.scalar_one_or_none()
        return self._to_domain(orm) if orm else None

    def _to_domain(self, orm: NotificationORM) -> Notification:
        return Notification(
            id=orm.id,
            user_id=orm.user_id,
            type=NotificationType(orm.type.value),
            title=orm.title,
            message=orm.message,
            channel=NotificationChannel(orm.channel.value),
            status=NotificationStatus(orm.status.value),
            metadata=orm.metadata_json or {},
            source_service=orm.source_service,
            source_event_type=orm.source_event_type,
            source_event_id=orm.source_event_id,
            idempotency_key=orm.idempotency_key,
            deeplink=orm.deeplink,
            read_at=orm.read_at,
            created_at=orm.created_at,
        )


class DeviceTokenRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def upsert(self, device_token: DeviceToken) -> DeviceToken:
        now = datetime.now(timezone.utc)
        stmt = insert(DeviceTokenORM).values(
            id=device_token.id,
            user_id=device_token.user_id,
            driver_id=device_token.driver_id,
            token=device_token.token,
            platform=DevicePlatformORM(device_token.platform.value),
            device_id=device_token.device_id,
            app_version=device_token.app_version,
            is_active=True,
            last_seen_at=now,
        )
        stmt = stmt.on_conflict_do_update(
            constraint="uq_device_tokens_token",
            set_={
                "user_id": device_token.user_id,
                "driver_id": device_token.driver_id,
                "platform": DevicePlatformORM(device_token.platform.value),
                "device_id": device_token.device_id,
                "app_version": device_token.app_version,
                "is_active": True,
                "last_seen_at": now,
                "updated_at": func.now(),
            },
        ).returning(DeviceTokenORM)
        result = await self._session.execute(stmt)
        orm = result.scalar_one()
        return self._to_domain(orm)

    async def deactivate(self, user_id: UUID, token: str) -> None:
        await self._session.execute(
            update(DeviceTokenORM)
            .where(DeviceTokenORM.user_id == user_id, DeviceTokenORM.token == token)
            .values(is_active=False, last_seen_at=datetime.now(timezone.utc))
        )
        await self._session.flush()

    async def active_tokens_for_user(self, user_id: UUID) -> list[DeviceToken]:
        result = await self._session.execute(
            select(DeviceTokenORM).where(
                DeviceTokenORM.user_id == user_id,
                DeviceTokenORM.is_active.is_(True),
            )
        )
        return [self._to_domain(orm) for orm in result.scalars().all()]

    async def active_tokens_for_driver(self, driver_id: UUID) -> list[DeviceToken]:
        result = await self._session.execute(
            select(DeviceTokenORM).where(
                DeviceTokenORM.driver_id == driver_id,
                DeviceTokenORM.is_active.is_(True),
            )
        )
        return [self._to_domain(orm) for orm in result.scalars().all()]

    def _to_domain(self, orm: DeviceTokenORM) -> DeviceToken:
        return DeviceToken(
            id=orm.id,
            user_id=orm.user_id,
            token=orm.token,
            platform=DevicePlatform(orm.platform.value),
            driver_id=orm.driver_id,
            device_id=orm.device_id,
            app_version=orm.app_version,
            is_active=orm.is_active,
            last_seen_at=orm.last_seen_at or orm.updated_at,
            created_at=orm.created_at,
        )
