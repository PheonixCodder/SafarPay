from __future__ import annotations

from datetime import date
from typing import Any, cast
from uuid import UUID, uuid4

import pytest
from sp.core.config import Settings
from verification.application.schemas import (
    IdentitySubmissionRequest,
    LicenseSubmissionRequest,
    SelfieSubmissionRequest,
    VehicleSubmissionRequest,
)
from verification.application.services.identity_verification_engine import VerificationResult
from verification.application.use_cases import VerificationUseCases
from verification.domain.exceptions import DriverNotFoundError, InvalidDocumentStateError
from verification.domain.models import (
    Document,
    DocumentType,
    Driver,
    DriverVehicle,
    EntityType,
    Vehicle,
    VehicleType,
    VerificationRejection,
    VerificationStatus,
)


class FakeDriverRepo:
    def __init__(self) -> None:
        self.by_id: dict[UUID, Driver] = {}

    async def find_by_id(self, driver_id: UUID) -> Driver | None:
        return self.by_id.get(driver_id)

    async def find_by_user_id(self, user_id: UUID) -> Driver | None:
        return next((d for d in self.by_id.values() if d.user_id == user_id), None)

    async def save(self, driver: Driver) -> Driver:
        self.by_id[driver.id] = driver
        return driver

    async def update(self, driver: Driver) -> Driver:
        self.by_id[driver.id] = driver
        return driver


class FakeVehicleRepo:
    def __init__(self) -> None:
        self.by_id: dict[UUID, Vehicle] = {}

    async def find_by_id(self, vehicle_id: UUID) -> Vehicle | None:
        return self.by_id.get(vehicle_id)

    async def find_by_plate_number(self, plate_number: str) -> Vehicle | None:
        return next((v for v in self.by_id.values() if v.plate_number == plate_number), None)

    async def save(self, vehicle: Vehicle) -> Vehicle:
        self.by_id[vehicle.id] = vehicle
        return vehicle

    async def update(self, vehicle: Vehicle) -> Vehicle:
        self.by_id[vehicle.id] = vehicle
        return vehicle


class FakeDocumentRepo:
    def __init__(self) -> None:
        self.by_id: dict[UUID, Document] = {}

    async def find_by_id(self, document_id: UUID) -> Document | None:
        return self.by_id.get(document_id)

    async def find_by_entity_id(self, entity_id: UUID) -> list[Document]:
        return [d for d in self.by_id.values() if d.entity_id == entity_id]

    async def find_by_entity_and_type(self, entity_id: UUID, document_type: str) -> Document | None:
        return next(
            (
                d
                for d in self.by_id.values()
                if d.entity_id == entity_id and d.document_type.value == document_type
            ),
            None,
        )

    async def save(self, document: Document) -> Document:
        self.by_id[document.id] = document
        return document

    async def update(self, document: Document) -> Document:
        self.by_id[document.id] = document
        return document


class FakeDriverVehicleRepo:
    def __init__(self) -> None:
        self.links: dict[UUID, DriverVehicle] = {}

    async def find_by_driver_id(self, driver_id: UUID) -> list[DriverVehicle]:
        return [dv for dv in self.links.values() if dv.driver_id == driver_id]

    async def find_active_by_driver_id(self, driver_id: UUID) -> DriverVehicle | None:
        return next(
            (dv for dv in self.links.values() if dv.driver_id == driver_id and dv.is_currently_selected),
            None,
        )

    async def link_driver_vehicle(
        self, driver_id: UUID, vehicle_id: UUID, vehicle_type: VehicleType
    ) -> DriverVehicle:
        link = DriverVehicle(
            id=uuid4(),
            driver_id=driver_id,
            vehicle_id=vehicle_id,
            vehicle_type=vehicle_type,
        )
        self.links[link.id] = link
        return link

    async def set_active_vehicle(self, driver_id: UUID, vehicle_id: UUID) -> None:
        for link in self.links.values():
            if link.driver_id == driver_id:
                link.is_currently_selected = link.vehicle_id == vehicle_id


class FakeStorage:
    def __init__(self) -> None:
        self.deleted: list[tuple[str, str]] = []
        self.fetched: list[tuple[str, str]] = []

    async def generate_presigned_put_url(
        self, bucket_name: str, object_key: str, expires_in: int = 3600, content_type: str = "image/jpeg"
    ) -> str:
        return f"https://s3.test/{bucket_name}/{object_key}"

    async def get_object_bytes(self, bucket_name: str, object_key: str) -> bytes:
        self.fetched.append((bucket_name, object_key))
        return b"image"

    async def delete_object(self, bucket_name: str, object_key: str) -> None:
        self.deleted.append((bucket_name, object_key))


class FakeRejectionResolver:
    def __init__(self) -> None:
        self.reasons: dict[UUID, str] = {}
        self.resolved: list[UUID] = []

    async def get_rejection_reason(self, document_id: UUID) -> str | None:
        return self.reasons.get(document_id)

    async def resolve_previous_rejections(self, document_id: UUID) -> None:
        self.resolved.append(document_id)


class FakeIdentityEngine:
    def __init__(self, result: VerificationResult | None = None) -> None:
        self.result = result or VerificationResult(
            success=True,
            errors=[],
            extracted_data={"cnic_raw_text": "CNIC OK", "license_raw_text": "LICENSE OK"},
        )

    async def run(self, bundle: Any) -> VerificationResult:
        return self.result


class FakePublisher:
    def __init__(self) -> None:
        self.events: list[Any] = []

    async def publish(self, event: Any) -> None:
        self.events.append(event)


class FakeRejectionRepo:
    def __init__(self) -> None:
        self.rejections: list[VerificationRejection] = []

    async def find_active_rejection_by_document(self, document_id: UUID) -> VerificationRejection | None:
        return next((r for r in self.rejections if r.document_id == document_id and not r.is_resolved), None)

    async def mark_rejections_resolved(self, document_id: UUID) -> None:
        for rejection in self.rejections:
            if rejection.document_id == document_id:
                rejection.is_resolved = True

    async def create_rejection(self, rejection: VerificationRejection) -> VerificationRejection:
        self.rejections.append(rejection)
        return rejection


class FakeCache:
    def __init__(self) -> None:
        self.allow_lock = True
        self.deleted: list[tuple[str, str, str]] = []

    async def set(self, namespace: str, key: str, value: str, *, ttl: int, nx: bool) -> bool:
        return self.allow_lock

    async def delete_if_equals(self, namespace: str, key: str, value: str) -> None:
        self.deleted.append((namespace, key, value))


class VerificationFixture:
    def __init__(self) -> None:
        self.driver_repo = FakeDriverRepo()
        self.vehicle_repo = FakeVehicleRepo()
        self.document_repo = FakeDocumentRepo()
        self.driver_vehicle_repo = FakeDriverVehicleRepo()
        self.storage = FakeStorage()
        self.resolver = FakeRejectionResolver()
        self.engine = FakeIdentityEngine()
        self.publisher = FakePublisher()
        self.rejection_repo = FakeRejectionRepo()
        self.cache = FakeCache()
        self.settings = Settings(
            S3_IDENTITY_BUCKET="identity",
            S3_LICENSE_BUCKET="license",
            S3_VEHICLE_BUCKET="vehicle",
        )
        self.uc = VerificationUseCases(
            driver_repo=self.driver_repo,
            vehicle_repo=self.vehicle_repo,
            document_repo=self.document_repo,
            driver_vehicle_repo=self.driver_vehicle_repo,
            storage_provider=self.storage,
            rejection_resolver=cast(Any, self.resolver),
            identity_engine=cast(Any, self.engine),
            event_publisher=cast(Any, self.publisher),
            rejection_repo=self.rejection_repo,
            cache_manager=cast(Any, self.cache),
            settings=self.settings,
        )


@pytest.fixture
def fx() -> VerificationFixture:
    return VerificationFixture()


async def seed_complete_driver(fx: VerificationFixture, user_id: UUID) -> tuple[Driver, Vehicle]:
    driver = await fx.driver_repo.save(Driver(id=uuid4(), user_id=user_id))
    vehicle = await fx.vehicle_repo.save(
        Vehicle(
            id=uuid4(),
            brand="Toyota",
            model="Yaris",
            year=2024,
            color="White",
            plate_number="ABC-123",
        )
    )
    await fx.driver_vehicle_repo.link_driver_vehicle(driver.id, vehicle.id, vehicle.vehicle_type)
    await fx.driver_vehicle_repo.set_active_vehicle(driver.id, vehicle.id)
    for doc_type in [
        DocumentType.ID_FRONT,
        DocumentType.ID_BACK,
        DocumentType.LICENSE_FRONT,
        DocumentType.LICENSE_BACK,
        DocumentType.SELFIE_ID,
    ]:
        await fx.document_repo.save(
            Document(
                id=uuid4(),
                document_type=doc_type,
                file_key=f"driver/{doc_type.value}",
                entity_id=driver.id,
                entity_type=EntityType.DRIVER,
            )
        )
    for doc_type in [
        DocumentType.REGISTRATION_DOC_FRONT,
        DocumentType.REGISTRATION_DOC_BACK,
        DocumentType.VEHICLE_PHOTO_FRONT,
        DocumentType.VEHICLE_PHOTO_BACK,
    ]:
        await fx.document_repo.save(
            Document(
                id=uuid4(),
                document_type=doc_type,
                file_key=f"vehicle/{doc_type.value}",
                entity_id=vehicle.id,
                entity_type=EntityType.VEHICLE,
            )
        )
    return driver, vehicle


@pytest.mark.asyncio
async def test_get_verification_status_all_major_states(fx: VerificationFixture) -> None:
    user_id = uuid4()
    not_started = await fx.uc.get_verification_status(user_id)
    assert not_started.overall_status == "not_started"

    driver = await fx.driver_repo.save(Driver(id=uuid4(), user_id=user_id))
    pending = await fx.uc.get_verification_status(user_id)
    assert pending.overall_status == "not_started"

    doc = await fx.document_repo.save(
        Document(
            id=uuid4(),
            document_type=DocumentType.ID_FRONT,
            file_key="id-front",
            entity_id=driver.id,
            entity_type=EntityType.DRIVER,
        )
    )
    await fx.document_repo.save(
        Document(
            id=uuid4(),
            document_type=DocumentType.ID_BACK,
            file_key="id-back",
            entity_id=driver.id,
            entity_type=EntityType.DRIVER,
        )
    )
    fx.resolver.reasons[doc.id] = "bad image"
    doc.verification_status = VerificationStatus.REJECTED
    rejected = await fx.uc.get_verification_status(user_id)
    assert rejected.overall_status == "rejected"
    assert rejected.identity.rejection_reason == "bad image"

    driver.verification_status = VerificationStatus.UNDER_REVIEW
    under_review = await fx.uc.get_verification_status(user_id)
    assert under_review.overall_status == "under_review"


@pytest.mark.asyncio
async def test_identity_license_selfie_submission_create_and_update_documents(
    fx: VerificationFixture,
) -> None:
    user_id = uuid4()
    identity = await fx.uc.submit_identity_documents(
        user_id,
        IdentitySubmissionRequest(id_number="12345", expiry_date=date(2030, 1, 1)),
    )
    assert set(identity.urls) == {"id_front", "id_back"}

    driver = await fx.driver_repo.find_by_user_id(user_id)
    assert driver is not None
    first_doc = await fx.document_repo.find_by_entity_and_type(driver.id, "id_front")
    assert first_doc is not None
    old_key = first_doc.file_key

    await fx.uc.submit_identity_documents(
        user_id,
        IdentitySubmissionRequest(id_number="12345", expiry_date=date(2031, 1, 1)),
    )
    assert ("identity", old_key) in fx.storage.deleted
    assert len(fx.storage.deleted) == 2
    assert first_doc.id in fx.resolver.resolved
    assert len(fx.resolver.resolved) == 2

    license_resp = await fx.uc.submit_license_documents(
        user_id,
        LicenseSubmissionRequest(license_number="L-1", expiry_date=date(2030, 1, 1)),
    )
    selfie_resp = await fx.uc.submit_selfie(user_id, SelfieSubmissionRequest())
    assert set(license_resp.urls) == {"license_front", "license_back"}
    assert set(selfie_resp.urls) == {"selfie_id"}

    driver.verification_status = VerificationStatus.UNDER_REVIEW
    with pytest.raises(InvalidDocumentStateError):
        await fx.uc.submit_selfie(user_id, SelfieSubmissionRequest())


@pytest.mark.asyncio
async def test_vehicle_submission_create_update_and_reject_invalid_ownership(
    fx: VerificationFixture,
) -> None:
    user_id = uuid4()
    response = await fx.uc.submit_vehicle_info_and_documents(
        user_id,
        VehicleSubmissionRequest(
            vehicle_id=None,
            brand="Toyota",
            model="Yaris",
            color="White",
            vehicle_type=VehicleType.ECONOMY,
            max_passengers=4,
            plate_number="ABC-123",
            production_year=2024,
        ),
    )
    assert set(response.urls) == {
        "registration_doc_front",
        "registration_doc_back",
        "vehicle_photo_front",
        "vehicle_photo_back",
    }
    driver = await fx.driver_repo.find_by_user_id(user_id)
    assert driver is not None
    vehicle = next(iter(fx.vehicle_repo.by_id.values()))

    with pytest.raises(ValueError, match="already exists"):
        await fx.uc.submit_vehicle_info_and_documents(
            user_id,
            VehicleSubmissionRequest(
                vehicle_id=None,
                brand="Honda",
                model="City",
                color="Black",
                vehicle_type=VehicleType.ECONOMY,
                max_passengers=4,
                plate_number="XYZ-999",
                production_year=2024,
            ),
        )

    update = await fx.uc.submit_vehicle_info_and_documents(
        user_id,
        VehicleSubmissionRequest(
            vehicle_id=vehicle.id,
            brand="Toyota",
            model="Corolla",
            color="Black",
            vehicle_type=VehicleType.ECONOMY,
            max_passengers=4,
            plate_number="ABC-123",
            production_year=2025,
        ),
    )
    assert update.urls
    assert fx.vehicle_repo.by_id[vehicle.id].model == "Corolla"

    foreign = await fx.vehicle_repo.save(
        Vehicle(
            id=uuid4(),
            brand="Foreign",
            model="Car",
            year=2020,
            color="Red",
            plate_number="FOR-1",
        )
    )
    with pytest.raises(ValueError, match="does not belong"):
        await fx.uc.submit_vehicle_info_and_documents(
            user_id,
            VehicleSubmissionRequest(
                vehicle_id=foreign.id,
                brand="Foreign",
                model="Car",
                color="Red",
                vehicle_type=VehicleType.ECONOMY,
                max_passengers=4,
                plate_number="FOR-1",
                production_year=2020,
            ),
        )


@pytest.mark.asyncio
async def test_request_verification_review_validates_preconditions_and_publishes(
    fx: VerificationFixture,
) -> None:
    user_id = uuid4()
    with pytest.raises(DriverNotFoundError):
        await fx.uc.request_verification_review(user_id)

    driver = await fx.driver_repo.save(Driver(id=uuid4(), user_id=user_id))
    with pytest.raises(InvalidDocumentStateError, match="No active vehicle"):
        await fx.uc.request_verification_review(user_id)

    fx = VerificationFixture()
    driver, _vehicle = await seed_complete_driver(fx, user_id)
    response = await fx.uc.request_verification_review(user_id)
    assert response.status == "UNDER_REVIEW"
    assert driver.verification_status == VerificationStatus.UNDER_REVIEW
    assert driver.review_attempts == 1
    assert fx.publisher.events

    with pytest.raises(InvalidDocumentStateError):
        await fx.uc.request_verification_review(user_id)


@pytest.mark.asyncio
async def test_execute_verification_review_success_failure_and_locking(fx: VerificationFixture) -> None:
    user_id = uuid4()
    driver, _vehicle = await seed_complete_driver(fx, user_id)
    await fx.uc.execute_verification_review(driver.id)
    assert driver.verification_status == VerificationStatus.VERIFIED
    assert all(d.verification_status == VerificationStatus.VERIFIED for d in fx.document_repo.by_id.values())
    assert fx.cache.deleted

    fx = VerificationFixture()
    driver, _vehicle = await seed_complete_driver(fx, user_id)
    fx.engine.result = VerificationResult(
        success=False,
        errors=[{"document_type": DocumentType.ID_FRONT, "code": "FACE_MISMATCH", "details": "faces differ"}],
        extracted_data={},
    )
    await fx.uc.execute_verification_review(driver.id)
    assert driver.verification_status == VerificationStatus.REJECTED
    assert fx.rejection_repo.rejections[0].rejection_reason_code == "FACE_MISMATCH"

    fx = VerificationFixture()
    driver, _vehicle = await seed_complete_driver(fx, user_id)
    fx.cache.allow_lock = False
    await fx.uc.execute_verification_review(driver.id)
    assert driver.verification_status == VerificationStatus.PENDING
