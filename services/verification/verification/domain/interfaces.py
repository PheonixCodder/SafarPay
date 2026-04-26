"""Repository and Storage protocols for verification."""
from typing import Protocol, runtime_checkable
from uuid import UUID

from .models import (
    Driver,
    Vehicle,
    Document,
    DriverVehicle,
    VerificationRejection,
    DriverStats,
)


@runtime_checkable
class DriverRepositoryProtocol(Protocol):
    async def find_by_id(self, driver_id: UUID) -> Driver | None: ...
    async def find_by_user_id(self, user_id: UUID) -> Driver | None: ...
    async def save(self, driver: Driver) -> Driver: ...
    async def update(self, driver: Driver) -> Driver: ...


@runtime_checkable
class VehicleRepositoryProtocol(Protocol):
    async def find_by_id(self, vehicle_id: UUID) -> Vehicle | None: ...
    async def find_by_plate_number(self, plate_number: str) -> Vehicle | None: ...
    async def save(self, vehicle: Vehicle) -> Vehicle: ...
    async def update(self, vehicle: Vehicle) -> Vehicle: ...


@runtime_checkable
class DocumentRepositoryProtocol(Protocol):
    async def find_by_id(self, document_id: UUID) -> Document | None: ...
    async def find_by_entity_id(self, entity_id: UUID) -> list[Document]: ...
    async def find_by_entity_and_type(
        self, entity_id: UUID, document_type: str
    ) -> Document | None: ...
    async def save(self, document: Document) -> Document: ...
    async def update(self, document: Document) -> Document: ...


@runtime_checkable
class DriverVehicleRepositoryProtocol(Protocol):
    async def find_by_driver_id(self, driver_id: UUID) -> list[DriverVehicle]: ...
    async def find_active_by_driver_id(
        self, driver_id: UUID
    ) -> DriverVehicle | None: ...
    async def link_driver_vehicle(
        self, driver_id: UUID, vehicle_id: UUID
    ) -> DriverVehicle: ...
    async def set_active_vehicle(self, driver_id: UUID, vehicle_id: UUID) -> None: ...


@runtime_checkable
class StorageProviderProtocol(Protocol):
    async def generate_presigned_put_url(
        self, bucket_name: str, object_key: str, expires_in: int = 3600
    ) -> str:
        """Generate a presigned URL to upload an object to S3."""
        ...

    async def get_object_bytes(self, bucket_name: str, object_key: str) -> bytes:
        """Fetch an object's bytes directly from S3."""
        ...

    async def delete_object(self, bucket_name: str, object_key: str) -> None:
        """Delete an object from S3."""
        ...


@runtime_checkable
class VerificationRejectionRepositoryProtocol(Protocol):
    async def find_active_rejection_by_document(
        self, document_id: UUID
    ) -> VerificationRejection | None: ...
    
    async def mark_rejections_resolved(self, document_id: UUID) -> None: ...

    async def create_rejection(self, rejection: VerificationRejection) -> VerificationRejection: ...
