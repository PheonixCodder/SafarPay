"""Run the verification review flow against local fixture files.

This script intentionally uses the real VerificationUseCases and
IdentityVerificationEngine, while replacing DB/S3/Kafka/Redis with in-memory
test doubles.
"""
from __future__ import annotations

import argparse
import asyncio
import json
import sys
import uuid
from dataclasses import asdict
from datetime import date, datetime, timezone
from pathlib import Path
from types import SimpleNamespace
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "libs" / "platform" / "src"))
sys.path.insert(0, str(REPO_ROOT / "services" / "verification"))


def ensure_verification_imports() -> None:
    """Import verification modules lazily so fixture validation stays fast."""
    global IdentityVerificationEngine
    global RejectionResolver
    global VerificationUseCases
    global Document
    global DocumentType
    global Driver
    global DriverServiceCapability
    global DriverVehicle
    global EntityType
    global ServiceType
    global Vehicle
    global VehicleType
    global VerificationRejection

    from verification.application.services.identity_verification_engine import (
        IdentityVerificationEngine,
    )
    from verification.application.services.rejection_resolver import RejectionResolver
    from verification.application.use_cases import VerificationUseCases
    from verification.domain.models import (
        Document,
        DocumentType,
        Driver,
        DriverServiceCapability,
        DriverVehicle,
        EntityType,
        ServiceType,
        Vehicle,
        VehicleType,
        VerificationRejection,
    )


class InMemoryDriverRepo:
    def __init__(self) -> None:
        self.items: dict[uuid.UUID, Driver] = {}

    async def find_by_id(self, driver_id: uuid.UUID) -> Driver | None:
        return self.items.get(driver_id)

    async def find_by_user_id(self, user_id: uuid.UUID) -> Driver | None:
        return next((driver for driver in self.items.values() if driver.user_id == user_id), None)

    async def save(self, driver: Driver) -> Driver:
        now = datetime.now(timezone.utc)
        driver.created_at = driver.created_at or now
        driver.updated_at = now
        self.items[driver.id] = driver
        return driver

    async def update(self, driver: Driver) -> Driver:
        driver.updated_at = datetime.now(timezone.utc)
        self.items[driver.id] = driver
        return driver


class InMemoryVehicleRepo:
    def __init__(self) -> None:
        self.items: dict[uuid.UUID, Vehicle] = {}

    async def find_by_id(self, vehicle_id: uuid.UUID) -> Vehicle | None:
        return self.items.get(vehicle_id)

    async def find_by_plate_number(self, plate_number: str) -> Vehicle | None:
        return next(
            (vehicle for vehicle in self.items.values() if vehicle.plate_number == plate_number),
            None,
        )

    async def save(self, vehicle: Vehicle) -> Vehicle:
        now = datetime.now(timezone.utc)
        vehicle.created_at = vehicle.created_at or now
        vehicle.updated_at = now
        self.items[vehicle.id] = vehicle
        return vehicle

    async def update(self, vehicle: Vehicle) -> Vehicle:
        vehicle.updated_at = datetime.now(timezone.utc)
        self.items[vehicle.id] = vehicle
        return vehicle


class InMemoryDocumentRepo:
    def __init__(self) -> None:
        self.items: dict[uuid.UUID, Document] = {}

    async def find_by_id(self, document_id: uuid.UUID) -> Document | None:
        return self.items.get(document_id)

    async def find_by_entity_id(self, entity_id: uuid.UUID) -> list[Document]:
        return [doc for doc in self.items.values() if doc.entity_id == entity_id]

    async def find_by_entity_and_type(
        self,
        entity_id: uuid.UUID,
        document_type: str,
    ) -> Document | None:
        return next(
            (
                doc
                for doc in self.items.values()
                if doc.entity_id == entity_id and doc.document_type.value == document_type
            ),
            None,
        )

    async def save(self, document: Document) -> Document:
        now = datetime.now(timezone.utc)
        document.created_at = document.created_at or now
        document.updated_at = now
        self.items[document.id] = document
        return document

    async def update(self, document: Document) -> Document:
        document.updated_at = datetime.now(timezone.utc)
        self.items[document.id] = document
        return document


class InMemoryDriverVehicleRepo:
    def __init__(self) -> None:
        self.items: dict[uuid.UUID, DriverVehicle] = {}

    async def find_by_driver_id(self, driver_id: uuid.UUID) -> list[DriverVehicle]:
        return [link for link in self.items.values() if link.driver_id == driver_id]

    async def find_active_by_driver_id(self, driver_id: uuid.UUID) -> DriverVehicle | None:
        return next(
            (
                link
                for link in self.items.values()
                if link.driver_id == driver_id and link.is_currently_selected
            ),
            None,
        )

    async def link_driver_vehicle(
        self,
        driver_id: uuid.UUID,
        vehicle_id: uuid.UUID,
        vehicle_type: VehicleType,
    ) -> DriverVehicle:
        existing = next(
            (
                link
                for link in self.items.values()
                if link.driver_id == driver_id and link.vehicle_id == vehicle_id
            ),
            None,
        )
        if existing:
            return existing
        link = DriverVehicle(
            id=uuid.uuid4(),
            driver_id=driver_id,
            vehicle_id=vehicle_id,
            vehicle_type=vehicle_type,
        )
        self.items[link.id] = link
        return link

    async def set_active_vehicle(self, driver_id: uuid.UUID, vehicle_id: uuid.UUID) -> None:
        for link in self.items.values():
            if link.driver_id == driver_id:
                link.is_currently_selected = link.vehicle_id == vehicle_id


class InMemoryCapabilityRepo:
    def __init__(self) -> None:
        self.items: dict[uuid.UUID, DriverServiceCapability] = {}

    async def find_by_driver_id(self, driver_id: uuid.UUID) -> list[DriverServiceCapability]:
        return [item for item in self.items.values() if item.driver_id == driver_id]

    async def find_by_driver_and_service(
        self,
        driver_id: uuid.UUID,
        service_type: ServiceType,
    ) -> list[DriverServiceCapability]:
        return [
            item
            for item in self.items.values()
            if item.driver_id == driver_id and item.service_type == service_type
        ]

    async def upsert_capability(
        self,
        driver_id: uuid.UUID,
        vehicle_id: uuid.UUID,
        service_type: ServiceType,
    ) -> DriverServiceCapability:
        existing = next(
            (
                item
                for item in self.items.values()
                if item.driver_id == driver_id
                and item.vehicle_id == vehicle_id
                and item.service_type == service_type
            ),
            None,
        )
        if existing:
            existing.is_active = True
            return existing
        item = DriverServiceCapability(
            id=uuid.uuid4(),
            driver_id=driver_id,
            vehicle_id=vehicle_id,
            service_type=service_type,
        )
        self.items[item.id] = item
        return item


class InMemoryRejectionRepo:
    def __init__(self) -> None:
        self.items: list[VerificationRejection] = []

    async def create_rejection(self, rejection: VerificationRejection) -> VerificationRejection:
        self.items.append(rejection)
        return rejection

    async def find_active_rejection_by_document(
        self,
        document_id: uuid.UUID,
    ) -> VerificationRejection | None:
        return next(
            (
                item
                for item in reversed(self.items)
                if item.document_id == document_id and not item.is_resolved
            ),
            None,
        )

    async def mark_rejections_resolved(self, document_id: uuid.UUID) -> None:
        for item in self.items:
            if item.document_id == document_id:
                item.is_resolved = True


class LocalStorageProvider:
    def __init__(self, case_dir: Path) -> None:
        self.case_dir = case_dir

    async def generate_presigned_put_url(
        self,
        bucket_name: str,
        object_key: str,
        expires_in: int = 3600,
        content_type: str = "image/jpeg",
    ) -> str:
        return f"file://{(self.case_dir / object_key).resolve()}"

    async def get_object_bytes(self, bucket_name: str, object_key: str) -> bytes:
        path = (self.case_dir / object_key).resolve()
        if not path.exists():
            raise FileNotFoundError(f"Missing fixture file for {object_key}: {path}")
        return path.read_bytes()

    async def delete_object(self, bucket_name: str, object_key: str) -> None:
        return None


class RecordingEventPublisher:
    def __init__(self) -> None:
        self.events: list[Any] = []

    async def publish(self, event: Any) -> None:
        self.events.append(event)


class InMemoryCache:
    def __init__(self) -> None:
        self.values: dict[str, str] = {}

    async def set(
        self,
        namespace: str,
        key: str,
        value: str,
        ttl: int | None = None,
        nx: bool = False,
    ) -> bool:
        namespaced = f"{namespace}:{key}"
        if nx and namespaced in self.values:
            return False
        self.values[namespaced] = value
        return True

    async def delete_if_equals(self, namespace: str, key: str, expected_value: str) -> bool:
        namespaced = f"{namespace}:{key}"
        if self.values.get(namespaced) == expected_value:
            del self.values[namespaced]
            return True
        return False


def parse_date(value: str | None) -> date | None:
    if not value:
        return None
    return date.fromisoformat(value)


def serialize_enum(value: Any) -> Any:
    if hasattr(value, "value"):
        return value.value
    if isinstance(value, uuid.UUID):
        return str(value)
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    return value


def dataclass_to_json_dict(value: Any) -> dict[str, Any]:
    return json.loads(json.dumps(asdict(value), default=serialize_enum))


def load_case(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def validate_assets(case: dict[str, Any], case_dir: Path) -> None:
    missing: list[str] = []
    for doc_type, document in case["documents"].items():
        asset_path = case_dir / document["path"]
        if not asset_path.exists():
            missing.append(f"{doc_type}: {asset_path}")
    if missing:
        joined = "\n  - ".join(missing)
        raise FileNotFoundError(f"Missing fixture assets:\n  - {joined}")


async def build_use_cases(case: dict[str, Any], case_dir: Path) -> tuple[
    VerificationUseCases,
    InMemoryDriverRepo,
    InMemoryVehicleRepo,
    InMemoryDocumentRepo,
    InMemoryDriverVehicleRepo,
    InMemoryRejectionRepo,
    RecordingEventPublisher,
]:
    ensure_verification_imports()

    user_id = uuid.UUID(case["user_id"])
    driver_id = uuid.UUID(case["driver_id"])
    vehicle_id = uuid.UUID(case["vehicle_id"])
    vehicle_case = case["vehicle"]
    vehicle_type = VehicleType(vehicle_case["vehicle_type"])

    driver_repo = InMemoryDriverRepo()
    vehicle_repo = InMemoryVehicleRepo()
    document_repo = InMemoryDocumentRepo()
    driver_vehicle_repo = InMemoryDriverVehicleRepo()
    capability_repo = InMemoryCapabilityRepo()
    rejection_repo = InMemoryRejectionRepo()
    event_publisher = RecordingEventPublisher()
    cache = InMemoryCache()

    driver = Driver(id=driver_id, user_id=user_id)
    vehicle = Vehicle(
        id=vehicle_id,
        brand=vehicle_case["brand"],
        model=vehicle_case["model"],
        year=int(vehicle_case["year"]),
        color=vehicle_case["color"],
        plate_number=vehicle_case["plate_number"],
        max_passengers=int(vehicle_case.get("max_passengers", 4)),
        vehicle_type=vehicle_type,
    )

    await driver_repo.save(driver)
    await vehicle_repo.save(vehicle)
    await driver_vehicle_repo.link_driver_vehicle(driver.id, vehicle.id, vehicle.vehicle_type)
    await driver_vehicle_repo.set_active_vehicle(driver.id, vehicle.id)

    for doc_type_value, document_case in case["documents"].items():
        doc_type = DocumentType(doc_type_value)
        entity_type = (
            EntityType.VEHICLE
            if doc_type
            in {
                DocumentType.REGISTRATION_DOC_FRONT,
                DocumentType.REGISTRATION_DOC_BACK,
                DocumentType.VEHICLE_PHOTO_FRONT,
                DocumentType.VEHICLE_PHOTO_BACK,
            }
            else EntityType.DRIVER
        )
        entity_id = vehicle.id if entity_type == EntityType.VEHICLE else driver.id
        await document_repo.save(
            Document(
                id=uuid.uuid4(),
                document_type=doc_type,
                file_key=document_case["path"],
                entity_id=entity_id,
                entity_type=entity_type,
                document_number=document_case.get("document_number"),
                expiry_date=parse_date(document_case.get("expiry_date")),
                metadata_json=document_case.get("metadata_json") or {},
            )
        )

    settings = SimpleNamespace(
        S3_IDENTITY_BUCKET="local-identity",
        S3_LICENSE_BUCKET="local-license",
        S3_VEHICLE_BUCKET="local-vehicle",
        VERIFICATION_REVIEW_TIMEOUT_SECONDS=600.0,
    )

    use_cases = VerificationUseCases(
        driver_repo=driver_repo,
        vehicle_repo=vehicle_repo,
        document_repo=document_repo,
        driver_vehicle_repo=driver_vehicle_repo,
        storage_provider=LocalStorageProvider(case_dir),
        rejection_resolver=RejectionResolver(rejection_repo),
        identity_engine=IdentityVerificationEngine(),
        event_publisher=event_publisher,
        rejection_repo=rejection_repo,
        cache_manager=cache,
        driver_service_capability_repo=capability_repo,
        settings=settings,
    )

    return (
        use_cases,
        driver_repo,
        vehicle_repo,
        document_repo,
        driver_vehicle_repo,
        rejection_repo,
        event_publisher,
    )


async def run(case_path: Path, validate_only: bool) -> None:
    case_path = case_path.resolve()
    case_dir = case_path.parent
    case = load_case(case_path)
    validate_assets(case, case_dir)

    if validate_only:
        print("Fixture assets are present.")
        return

    (
        use_cases,
        driver_repo,
        vehicle_repo,
        document_repo,
        _driver_vehicle_repo,
        rejection_repo,
        event_publisher,
    ) = await build_use_cases(case, case_dir)

    user_id = uuid.UUID(case["user_id"])
    driver_id = uuid.UUID(case["driver_id"])

    submission = await use_cases.request_verification_review(user_id)
    await use_cases.execute_verification_review(driver_id)

    driver = await driver_repo.find_by_id(driver_id)
    documents = sorted(
        document_repo.items.values(),
        key=lambda item: item.document_type.value,
    )
    vehicles = sorted(
        vehicle_repo.items.values(),
        key=lambda item: item.plate_number,
    )

    summary = {
        "submission": submission.model_dump(),
        "driver": dataclass_to_json_dict(driver),
        "vehicles": [dataclass_to_json_dict(vehicle) for vehicle in vehicles],
        "documents": [dataclass_to_json_dict(document) for document in documents],
        "rejections": [dataclass_to_json_dict(rejection) for rejection in rejection_repo.items],
        "events": [
            {
                "event_type": getattr(event, "event_type", event.__class__.__name__),
                "payload": getattr(event, "payload", None),
            }
            for event in event_publisher.events
        ],
    }
    print(json.dumps(summary, indent=2, default=serialize_enum))


def main() -> None:
    parser = argparse.ArgumentParser(description="Run local verification review fixture.")
    parser.add_argument(
        "--case",
        type=Path,
        default=Path(__file__).with_name("sample_case.json"),
        help="Path to the JSON case file.",
    )
    parser.add_argument(
        "--validate-only",
        action="store_true",
        help="Only verify that all fixture assets referenced by the case exist.",
    )
    args = parser.parse_args()

    asyncio.run(run(args.case, args.validate_only))


if __name__ == "__main__":
    main()
