"""Concrete SQLAlchemy repositories for the verification service."""
from __future__ import annotations

from typing import Any, cast
from uuid import UUID

from sp.infrastructure.db.repository import BaseRepository
from sqlalchemy import select, update
from sqlalchemy.engine import CursorResult
from sqlalchemy.ext.asyncio import AsyncSession

from ..domain.interfaces import (
    DocumentRepositoryProtocol,
    DriverRepositoryProtocol,
    DriverVehicleRepositoryProtocol,
    VehicleRepositoryProtocol,
    VerificationRejectionRepositoryProtocol,
)
from ..domain.models import Document, Driver, DriverVehicle, Vehicle, VerificationRejection
from .orm_models import (
    DocumentORM,
    DriverORM,
    DriverVehicleORM,
    VehicleORM,
    VehicleType,
    VerificationRejectionORM,
)


class DriverRepository(BaseRepository[DriverORM], DriverRepositoryProtocol):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, DriverORM)

    def _to_domain(self, orm: DriverORM) -> Driver:
        return Driver(
            id=orm.id,
            user_id=orm.user_id,
            verification_status=orm.verification_status,
            review_attempts=orm.review_attempts,
            last_reviewed_at=orm.last_reviewed_at,
            created_at=orm.created_at,
            updated_at=orm.updated_at,
        )

    async def find_by_id(self, driver_id: UUID) -> Driver | None:  # type: ignore[override]
        result = await self._session.execute(
            select(DriverORM).where(DriverORM.id == driver_id)
        )
        orm = result.scalar_one_or_none()
        return self._to_domain(orm) if orm else None

    async def find_by_user_id(self, user_id: UUID) -> Driver | None:
        result = await self._session.execute(
            select(DriverORM).where(DriverORM.user_id == user_id)
        )
        orm = result.scalar_one_or_none()
        return self._to_domain(orm) if orm else None

    async def save(self, driver: Driver) -> Driver:  # type: ignore[override]
        orm = DriverORM(
            id=driver.id,
            user_id=driver.user_id,
            verification_status=driver.verification_status,
        )
        self._session.add(orm)
        await self._session.flush()
        return self._to_domain(orm)

    async def update(self, driver: Driver) -> Driver:
        await self._session.execute(
            update(DriverORM)
            .where(DriverORM.id == driver.id)
            .values(
                verification_status=driver.verification_status,
                review_attempts=driver.review_attempts,
                last_reviewed_at=driver.last_reviewed_at,
            )
        )
        await self._session.flush()
        return driver


class VehicleRepository(BaseRepository[VehicleORM], VehicleRepositoryProtocol):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, VehicleORM)

    def _to_domain(self, orm: VehicleORM) -> Vehicle:
        return Vehicle(
            id=orm.id,
            brand=orm.brand,
            model=orm.model,
            year=orm.year,
            color=orm.color,
            plate_number=orm.plate_number,
            max_passengers=orm.max_passengers,
            vehicle_type=orm.vehicle_type,
            verification_status=orm.verification_status,
            is_active=orm.is_active,
            created_at=orm.created_at,
            updated_at=orm.updated_at,
        )

    async def find_by_id(self, vehicle_id: UUID) -> Vehicle | None:  # type: ignore[override]
        result = await self._session.execute(
            select(VehicleORM).where(VehicleORM.id == vehicle_id)
        )
        orm = result.scalar_one_or_none()
        return self._to_domain(orm) if orm else None

    async def find_by_plate_number(self, plate_number: str) -> Vehicle | None:
        result = await self._session.execute(
            select(VehicleORM).where(VehicleORM.plate_number == plate_number)
        )
        orm = result.scalar_one_or_none()
        return self._to_domain(orm) if orm else None

    async def save(self, vehicle: Vehicle) -> Vehicle:  # type: ignore[override]
        orm = VehicleORM(
            id=vehicle.id,
            brand=vehicle.brand,
            model=vehicle.model,
            year=vehicle.year,
            color=vehicle.color,
            plate_number=vehicle.plate_number,
            max_passengers=vehicle.max_passengers,
            vehicle_type=vehicle.vehicle_type,
            verification_status=vehicle.verification_status,
            is_active=vehicle.is_active,
        )
        self._session.add(orm)
        await self._session.flush()
        return self._to_domain(orm)

    async def update(self, vehicle: Vehicle) -> Vehicle:
        await self._session.execute(
            update(VehicleORM)
            .where(VehicleORM.id == vehicle.id)
            .values(
                brand=vehicle.brand,
                model=vehicle.model,
                year=vehicle.year,
                color=vehicle.color,
                plate_number=vehicle.plate_number,
                max_passengers=vehicle.max_passengers,
                vehicle_type=vehicle.vehicle_type,
                verification_status=vehicle.verification_status,
                is_active=vehicle.is_active,
            )
        )
        await self._session.flush()
        return vehicle


class DocumentRepository(BaseRepository[DocumentORM], DocumentRepositoryProtocol):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, DocumentORM)

    def _to_domain(self, orm: DocumentORM) -> Document:
        return Document(
            id=orm.id,
            document_type=orm.document_type,
            file_key=orm.file_key,
            entity_id=orm.entity_id,
            entity_type=orm.entity_type,
            document_number=orm.document_number,
            expiry_date=orm.expiry_date,
            verification_status=orm.verification_status,
            metadata_json=orm.metadata_json,
            created_at=orm.created_at,
            updated_at=orm.updated_at,
        )

    async def find_by_id(self, document_id: UUID) -> Document | None:  # type: ignore[override]
        result = await self._session.execute(
            select(DocumentORM).where(DocumentORM.id == document_id)
        )
        orm = result.scalar_one_or_none()
        return self._to_domain(orm) if orm else None

    async def find_by_entity_id(self, entity_id: UUID) -> list[Document]:
        result = await self._session.execute(
            select(DocumentORM).where(DocumentORM.entity_id == entity_id)
        )
        return [self._to_domain(orm) for orm in result.scalars().all()]

    async def find_by_entity_and_type(
        self, entity_id: UUID, document_type: str
    ) -> Document | None:
        result = await self._session.execute(
            select(DocumentORM).where(
                DocumentORM.entity_id == entity_id,
                DocumentORM.document_type == document_type,
            )
        )
        orm = result.scalar_one_or_none()
        return self._to_domain(orm) if orm else None

    async def save(self, document: Document) -> Document:  # type: ignore[override]
        orm = DocumentORM(
            id=document.id,
            document_type=document.document_type,
            file_key=document.file_key,
            entity_id=document.entity_id,
            entity_type=document.entity_type,
            document_number=document.document_number,
            expiry_date=document.expiry_date,
            verification_status=document.verification_status,
            metadata_json=document.metadata_json,
        )
        self._session.add(orm)
        await self._session.flush()
        return self._to_domain(orm)

    async def update(self, document: Document) -> Document:
        await self._session.execute(
            update(DocumentORM)
            .where(DocumentORM.id == document.id)
            .values(
                file_key=document.file_key,
                document_number=document.document_number,
                expiry_date=document.expiry_date,
                verification_status=document.verification_status,
                metadata_json=document.metadata_json,
            )
        )
        await self._session.flush()
        return document


class DriverVehicleRepository(BaseRepository[DriverVehicleORM], DriverVehicleRepositoryProtocol):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, DriverVehicleORM)

    def _to_domain(self, orm: DriverVehicleORM) -> DriverVehicle:
        return DriverVehicle(
            id=orm.id,
            driver_id=orm.driver_id,
            vehicle_id=orm.vehicle_id,
            vehicle_type=orm.vehicle_type,
            is_currently_selected=orm.is_currently_selected,
            assigned_at=orm.assigned_at,
            created_at=orm.created_at,
            updated_at=orm.updated_at,
        )

    async def find_by_driver_id(self, driver_id: UUID) -> list[DriverVehicle]:
        result = await self._session.execute(
            select(DriverVehicleORM).where(DriverVehicleORM.driver_id == driver_id)
        )
        return [self._to_domain(orm) for orm in result.scalars().all()]

    async def find_active_by_driver_id(self, driver_id: UUID) -> DriverVehicle | None:
        result = await self._session.execute(
            select(DriverVehicleORM).where(
                DriverVehicleORM.driver_id == driver_id,
                DriverVehicleORM.is_currently_selected.is_(True),
            )
        )
        orm = result.scalar_one_or_none()
        return self._to_domain(orm) if orm else None

    async def link_driver_vehicle(
        self, driver_id: UUID, vehicle_id: UUID, vehicle_type: VehicleType
    ) -> DriverVehicle:
        orm = DriverVehicleORM(
            driver_id=driver_id,
            vehicle_id=vehicle_id,
            vehicle_type=vehicle_type
        )
        self._session.add(orm)
        await self._session.flush()
        return self._to_domain(orm)

    async def set_active_vehicle(self, driver_id: UUID, vehicle_id: UUID) -> None:
        # First set all vehicles for this driver to inactive
        await self._session.execute(
            update(DriverVehicleORM)
            .where(DriverVehicleORM.driver_id == driver_id)
            .values(is_currently_selected=False)
        )
        # Then set the selected one to active
        result = await self._session.execute(
            update(DriverVehicleORM)
            .where(
                DriverVehicleORM.driver_id == driver_id,
                DriverVehicleORM.vehicle_id == vehicle_id,
            )
            .values(is_currently_selected=True)
        )
        if cast(CursorResult[Any], result).rowcount == 0:
            from verification.domain.exceptions import DriverNotFoundError
            raise DriverNotFoundError(f"DriverVehicle link not found for driver {driver_id} and vehicle {vehicle_id}")

        await self._session.flush()


class VerificationRejectionRepository(BaseRepository[VerificationRejectionORM], VerificationRejectionRepositoryProtocol):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, VerificationRejectionORM)

    def _to_domain(self, orm: VerificationRejectionORM) -> VerificationRejection:
        return VerificationRejection(
            id=orm.id,
            driver_id=orm.driver_id,
            document_id=orm.document_id,
            rejection_reason_code=orm.rejection_reason_code,
            admin_comment=orm.admin_comment,
            is_resolved=orm.is_resolved,
            rejected_at=orm.rejected_at,
            created_at=orm.created_at,
            updated_at=orm.updated_at,
        )

    async def find_active_rejection_by_document(
        self, document_id: UUID
    ) -> VerificationRejection | None:
        result = await self._session.execute(
            select(VerificationRejectionORM)
            .where(
                VerificationRejectionORM.document_id == document_id,
                VerificationRejectionORM.is_resolved.is_(False),
            )
            .order_by(VerificationRejectionORM.rejected_at.desc())
        )
        orm = result.scalars().first()
        return self._to_domain(orm) if orm else None

    async def mark_rejections_resolved(self, document_id: UUID) -> None:
        await self._session.execute(
            update(VerificationRejectionORM)
            .where(
                VerificationRejectionORM.document_id == document_id,
                VerificationRejectionORM.is_resolved.is_(False),
            )
            .values(is_resolved=True)
        )
        await self._session.flush()

    async def create_rejection(self, rejection: VerificationRejection) -> VerificationRejection:
        orm = VerificationRejectionORM(
            id=rejection.id,
            driver_id=rejection.driver_id,
            rejection_reason_code=rejection.rejection_reason_code,
            document_id=rejection.document_id,
            admin_comment=rejection.admin_comment,
            is_resolved=rejection.is_resolved,
            rejected_at=rejection.rejected_at,
        )
        self._session.add(orm)
        await self._session.flush()
        return self._to_domain(orm)
