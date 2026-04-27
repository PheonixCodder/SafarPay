"""Application use cases containing business logic for verification service."""
from __future__ import annotations

import asyncio
import uuid
import logging
from datetime import datetime, timezone
from typing import Any

from sp.core.config import get_settings
from sp.infrastructure.messaging.publisher import EventPublisher
from sp.infrastructure.cache.manager import CacheManager
from ..domain.interfaces import (
    DriverRepositoryProtocol,
    VehicleRepositoryProtocol,
    DocumentRepositoryProtocol,
    DriverVehicleRepositoryProtocol,
    StorageProviderProtocol,
    VerificationRejectionRepositoryProtocol,
)
from verification.domain.models import (
    Driver,
    Vehicle,
    Document,
    DocumentType,
    EntityType,
    VerificationStatus,
    VerificationRejection,
)
from verification.domain.exceptions import (
    DriverNotFoundError,
    InvalidDocumentStateError,
    MLProcessingError,
)
from sp.infrastructure.messaging.events import VerificationReviewRequestedEvent
from .schemas import (
    IdentitySubmissionRequest,
    LicenseSubmissionRequest,
    SelfieSubmissionRequest,
    VehicleSubmissionRequest,
    DocumentUploadUrlsResponse,
    PresignedUrlResponse,
    VerificationStatusResponse,
    RequirementGroupStatusResponse,
    DocumentStatusResponse,
    ReviewSubmissionResponse,
)
from .services.rejection_resolver import RejectionResolver
from .services.identity_verification_engine import IdentityVerificationEngine, VerificationBundle

logger = logging.getLogger("verification.use_cases")


class VerificationUseCases:
    def __init__(
        self,
        driver_repo: DriverRepositoryProtocol,
        vehicle_repo: VehicleRepositoryProtocol,
        document_repo: DocumentRepositoryProtocol,
        driver_vehicle_repo: DriverVehicleRepositoryProtocol,
        storage_provider: StorageProviderProtocol,
        rejection_resolver: RejectionResolver,
        identity_engine: IdentityVerificationEngine,
        event_publisher: EventPublisher,
        rejection_repo: VerificationRejectionRepositoryProtocol,
        cache_manager: CacheManager,
        settings: Any = None,
    ) -> None:
        self.driver_repo = driver_repo
        self.vehicle_repo = vehicle_repo
        self.document_repo = document_repo
        self.driver_vehicle_repo = driver_vehicle_repo
        self.storage_provider = storage_provider
        self.rejection_resolver = rejection_resolver
        self.identity_engine = identity_engine
        self.event_publisher = event_publisher
        self.rejection_repo = rejection_repo
        self.cache_manager = cache_manager
        self.settings = settings or get_settings()

    async def _ensure_driver(self, user_id: uuid.UUID) -> Driver:
        """Fetch existing driver or create a new one for write operations."""
        driver = await self.driver_repo.find_by_user_id(user_id)
        if not driver:
            driver = Driver(id=uuid.uuid4(), user_id=user_id)
            await self.driver_repo.save(driver)
            
        if driver.verification_status == VerificationStatus.UNDER_REVIEW:
            raise InvalidDocumentStateError("Driver is currently under review. Cannot modify documents.")
            
        return driver

    async def _generate_presigned_url(self, bucket: str, key: str) -> PresignedUrlResponse:
        url = await self.storage_provider.generate_presigned_put_url(
            bucket_name=bucket, object_key=key
        )
        return PresignedUrlResponse(key=key, url=url)

    async def _upsert_document(
        self,
        entity_id: uuid.UUID,
        entity_type: EntityType,
        doc_type: DocumentType,
        user_id: uuid.UUID,
        bucket_name: str,
        key_prefix: str,
        document_number: str | None = None,
        expiry_date: Any = None,
    ) -> PresignedUrlResponse:
        """Idempotently create or update a document and return an upload URL."""
        doc = await self.document_repo.find_by_entity_and_type(entity_id, doc_type.value)
        key = f"{user_id}/{key_prefix}/{doc_type.value}_{uuid.uuid4().hex}"

        if doc:
            old_key = doc.file_key
            doc.file_key = key
            if document_number:
                doc.document_number = document_number
            if expiry_date:
                doc.expiry_date = expiry_date
            doc.verification_status = VerificationStatus.PENDING
            await self.rejection_resolver.resolve_previous_rejections(doc.id)
            await self.document_repo.update(doc)
            
            # Clean up old file
            if old_key:
                await self.storage_provider.delete_object(bucket_name, old_key)
        else:
            doc = Document(
                id=uuid.uuid4(),
                document_type=doc_type,
                file_key=key,
                entity_id=entity_id,
                entity_type=entity_type,
                document_number=document_number,
                expiry_date=expiry_date,
                verification_status=VerificationStatus.PENDING,
            )
            await self.document_repo.save(doc)

        return await self._generate_presigned_url(bucket_name, key)

    async def request_verification_review(self, user_id: uuid.UUID) -> dict[str, Any]:
        """Trigger a review of all submitted documents."""
        driver = await self.driver_repo.find_by_user_id(user_id)
        if not driver:
            raise DriverNotFoundError("Driver not found.")
        
        if driver.verification_status == VerificationStatus.UNDER_REVIEW:
            raise InvalidDocumentStateError("Driver is already under review.")
        if driver.verification_status in [VerificationStatus.VERIFIED, VerificationStatus.REJECTED]:
            raise InvalidDocumentStateError("Driver verification is already finalized.")
            
        driver_docs = await self.document_repo.find_by_entity_id(driver.id)
        required_driver_docs = {DocumentType.ID_FRONT, DocumentType.ID_BACK, DocumentType.LICENSE_FRONT, DocumentType.LICENSE_BACK, DocumentType.SELFIE_ID}
        
        active_vehicle = await self.driver_vehicle_repo.find_active_by_driver_id(driver.id)
        if not active_vehicle:
            raise InvalidDocumentStateError("No active vehicle found.")
            
        vehicle_docs = await self.document_repo.find_by_entity_id(active_vehicle.vehicle_id)
        required_vehicle_docs = {DocumentType.REGISTRATION_DOC_FRONT, DocumentType.REGISTRATION_DOC_BACK, DocumentType.VEHICLE_PHOTO_FRONT, DocumentType.VEHICLE_PHOTO_BACK}
        
        missing_driver_docs = required_driver_docs - {doc.document_type for doc in driver_docs}
        missing_vehicle_docs = required_vehicle_docs - {doc.document_type for doc in vehicle_docs}
        
        if missing_driver_docs or missing_vehicle_docs:
            raise InvalidDocumentStateError(f"Missing required documents. Driver: {missing_driver_docs}, Vehicle: {missing_vehicle_docs}")

        driver.verification_status = VerificationStatus.UNDER_REVIEW
        driver.review_attempts += 1
        driver.last_reviewed_at = datetime.now(timezone.utc)
        await self.driver_repo.update(driver)
        
        event = VerificationReviewRequestedEvent(payload={"user_id": str(user_id), "driver_id": str(driver.id)})
        await self.event_publisher.publish(event)
        
        return {"status": "UNDER_REVIEW", "estimated_time_seconds": 30}

    async def execute_verification_review(self, driver_id: uuid.UUID) -> None:
        """Background worker logic: ML verification and state persistence."""
        lock_key = f"review_lock:{driver_id}"
        lock_token = uuid.uuid4().hex
        # Try to acquire lock for 180 seconds
        if not await self.cache_manager.set("verification", lock_key, lock_token, ttl=180, nx=True):
            logger.warning("Verification review already in progress for driver_id=%s. Skipping.", driver_id)
            return

        try:
            await self._execute_verification_review_internal(driver_id)
        finally:
            current_token = await self.cache_manager.get("verification", lock_key)
            if current_token == lock_token:
                await self.cache_manager.delete("verification", lock_key)

    async def _execute_verification_review_internal(self, driver_id: uuid.UUID) -> None:
        """Internal logic for verification review."""
        trace_id = uuid.uuid4()
        logger.info(f"[{trace_id}] Starting verification review for driver {driver_id}")
        
        driver = await self.driver_repo.find_by_id(driver_id)
        if not driver:
            logger.info(f"[{trace_id}] Driver {driver_id} not found.")
            return
            
        if driver.verification_status in [VerificationStatus.VERIFIED, VerificationStatus.REJECTED]:
            logger.info(f"[{trace_id}] Driver {driver_id} already processed.")
            return  # Idempotency guard
            
        try:
            # 1. Fetch Docs
            driver_docs = await self.document_repo.find_by_entity_id(driver.id)
            active_vehicle = await self.driver_vehicle_repo.find_active_by_driver_id(driver.id)
            vehicle_docs = await self.document_repo.find_by_entity_id(active_vehicle.vehicle_id) if active_vehicle else []
            
            all_docs = {doc.document_type: doc for doc in driver_docs + vehicle_docs}
            
            # 2. Fetch S3 Bytes in parallel
            doc_types_to_fetch = [
                DocumentType.ID_FRONT, DocumentType.ID_BACK,
                DocumentType.LICENSE_FRONT, DocumentType.LICENSE_BACK,
                DocumentType.SELFIE_ID,
            ]
            
            buckets = {
                DocumentType.ID_FRONT: self.settings.S3_IDENTITY_BUCKET,
                DocumentType.ID_BACK: self.settings.S3_IDENTITY_BUCKET,
                DocumentType.LICENSE_FRONT: self.settings.S3_LICENSE_BUCKET,
                DocumentType.LICENSE_BACK: self.settings.S3_LICENSE_BUCKET,
                DocumentType.SELFIE_ID: self.settings.S3_LICENSE_BUCKET,
            }
            
            fetch_tasks = []
            for doc_type in doc_types_to_fetch:
                doc = all_docs.get(doc_type)
                if doc:
                    fetch_tasks.append(self.storage_provider.get_object_bytes(buckets[doc_type], doc.file_key))
                else:
                    raise ValueError(f"Missing document type {doc_type} during execution.")
                    
            fetched_bytes = await asyncio.gather(*fetch_tasks)
            doc_bytes = dict(zip(doc_types_to_fetch, fetched_bytes, strict=True))
            
            bundle = VerificationBundle(
                id_front=doc_bytes[DocumentType.ID_FRONT],
                id_back=doc_bytes[DocumentType.ID_BACK],
                license_front=doc_bytes[DocumentType.LICENSE_FRONT],
                license_back=doc_bytes[DocumentType.LICENSE_BACK],
                selfie=doc_bytes[DocumentType.SELFIE_ID],
                id_front_meta=all_docs[DocumentType.ID_FRONT].metadata_json or {},
                license_front_meta=all_docs[DocumentType.LICENSE_FRONT].metadata_json or {},
            )
            
            # 3. Run Engine (respecting internal semaphore by wrapping the whole phase)
            # We move OCR into the engine's run or just ensure we don't bypass it.
            # Actually, the engine's run() method should ideally handle OCR internal caching.
            # For now, let's just make sure we call a unified entry point if possible, 
            # or wrap these in the same semaphore if we had access to it.
            # Since we don't want to change the engine's interface too much right now, 
            # we'll just use the run() method which correctly uses the semaphore for heavy tasks.
            
            result = await asyncio.wait_for(
                self.identity_engine.run(bundle),
                timeout=60.0
            )

            # Update OCR meta from result if available (ensuring persistence)
            if result.extracted_data:
                if "cnic_raw_text" in result.extracted_data:
                    all_docs[DocumentType.ID_FRONT].metadata_json = {"ocr_text": result.extracted_data["cnic_raw_text"]}
                    await self.document_repo.update(all_docs[DocumentType.ID_FRONT])
                if "license_raw_text" in result.extracted_data:
                    all_docs[DocumentType.LICENSE_FRONT].metadata_json = {"ocr_text": result.extracted_data["license_raw_text"]}
                    await self.document_repo.update(all_docs[DocumentType.LICENSE_FRONT])
            
            # 4. Persistence
            # Meta is already saved in 3a for OCR, now finalize
            
            if result.success:
                identity_doc_types = [
                    DocumentType.ID_FRONT, DocumentType.ID_BACK,
                    DocumentType.LICENSE_FRONT, DocumentType.LICENSE_BACK,
                    DocumentType.SELFIE_ID
                ]
                vehicle_doc_types = [
                    DocumentType.REGISTRATION_DOC_FRONT, DocumentType.REGISTRATION_DOC_BACK,
                    DocumentType.VEHICLE_PHOTO_FRONT, DocumentType.VEHICLE_PHOTO_BACK
                ]
                for doc_type in identity_doc_types + vehicle_doc_types:
                    if doc_type in all_docs:
                        doc = all_docs[doc_type]
                        doc.verification_status = VerificationStatus.VERIFIED
                        await self.document_repo.update(doc)
                    
                driver.verification_status = VerificationStatus.VERIFIED
                await self.driver_repo.update(driver)
            else:
                identity_doc_types = [
                    DocumentType.ID_FRONT, DocumentType.ID_BACK,
                    DocumentType.LICENSE_FRONT, DocumentType.LICENSE_BACK,
                    DocumentType.SELFIE_ID
                ]
                vehicle_doc_types = [
                    DocumentType.REGISTRATION_DOC_FRONT, DocumentType.REGISTRATION_DOC_BACK,
                    DocumentType.VEHICLE_PHOTO_FRONT, DocumentType.VEHICLE_PHOTO_BACK
                ]
                for doc_type in identity_doc_types + vehicle_doc_types:
                    if doc_type in all_docs:
                        doc = all_docs[doc_type]
                        doc.verification_status = VerificationStatus.REJECTED
                        await self.document_repo.update(doc)
                    
                driver.verification_status = VerificationStatus.REJECTED
                await self.driver_repo.update(driver)
                
                # Insert rejections linked to documents
                for error in result.errors:
                    doc_type = error.get("document_type")
                    doc_id = None
                    if doc_type and doc_type in all_docs:
                        doc_id = all_docs[doc_type].id

                    rej = VerificationRejection(
                        id=uuid.uuid4(),
                        driver_id=driver.id,
                        document_id=doc_id,
                        rejection_reason_code=error.get("code", "UNKNOWN_ERROR"),
                        admin_comment=error.get("details", None),
                    )
                    await self.rejection_repo.create_rejection(rej)

        except MLProcessingError as e:
            logger.error(f"[{trace_id}] Verification ML failed for driver {driver.id}: {e}")
            identity_doc_types = [
                DocumentType.ID_FRONT, DocumentType.ID_BACK,
                DocumentType.LICENSE_FRONT, DocumentType.LICENSE_BACK,
                DocumentType.SELFIE_ID
            ]
            for doc_type in identity_doc_types:
                if doc_type in all_docs:
                    doc = all_docs[doc_type]
                    doc.verification_status = VerificationStatus.REJECTED
                    await self.document_repo.update(doc)
            
            rej = VerificationRejection(
                id=uuid.uuid4(),
                driver_id=driver.id,
                document_id=None,
                rejection_reason_code="ML_PROCESSING_ERROR",
                admin_comment=str(e),
            )
            await self.rejection_repo.create_rejection(rej)

            driver.verification_status = VerificationStatus.REJECTED
            await self.driver_repo.update(driver)
        except Exception as e:
            logger.exception(f"[{trace_id}] Verification infra failed for driver {driver.id}: {e}")
            driver.verification_status = VerificationStatus.PENDING
            await self.driver_repo.update(driver)
            raise

    async def submit_identity_documents(
        self, user_id: uuid.UUID, request: IdentitySubmissionRequest
    ) -> DocumentUploadUrlsResponse:
        driver = await self._ensure_driver(user_id)
        bucket = self.settings.S3_IDENTITY_BUCKET

        urls = {}
        for doc_type in [DocumentType.ID_FRONT, DocumentType.ID_BACK]:
            urls[doc_type.value] = await self._upsert_document(
                entity_id=driver.id,
                entity_type=EntityType.DRIVER,
                doc_type=doc_type,
                user_id=user_id,
                bucket_name=bucket,
                key_prefix="identity",
                document_number=request.id_number,
                expiry_date=request.expiry_date,
            )

        return DocumentUploadUrlsResponse(urls=urls)

    async def submit_license_documents(
        self, user_id: uuid.UUID, request: LicenseSubmissionRequest
    ) -> DocumentUploadUrlsResponse:
        driver = await self._ensure_driver(user_id)
        bucket = self.settings.S3_LICENSE_BUCKET

        urls = {}
        for doc_type in [DocumentType.LICENSE_FRONT, DocumentType.LICENSE_BACK]:
            urls[doc_type.value] = await self._upsert_document(
                entity_id=driver.id,
                entity_type=EntityType.DRIVER,
                doc_type=doc_type,
                user_id=user_id,
                bucket_name=bucket,
                key_prefix="license",
                document_number=request.license_number,
                expiry_date=request.expiry_date,
            )

        return DocumentUploadUrlsResponse(urls=urls)

    async def submit_selfie(
        self, user_id: uuid.UUID, request: SelfieSubmissionRequest
    ) -> DocumentUploadUrlsResponse:
        driver = await self._ensure_driver(user_id)
        bucket = self.settings.S3_LICENSE_BUCKET

        doc_type = DocumentType.SELFIE_ID
        url = await self._upsert_document(
            entity_id=driver.id,
            entity_type=EntityType.DRIVER,
            doc_type=doc_type,
            user_id=user_id,
            bucket_name=bucket,
            key_prefix="selfie",
        )

        return DocumentUploadUrlsResponse(urls={doc_type.value: url})

    async def submit_vehicle_info_and_documents(
        self, user_id: uuid.UUID, request: VehicleSubmissionRequest
    ) -> DocumentUploadUrlsResponse:
        driver = await self._ensure_driver(user_id)

        if request.vehicle_id:
            vehicle = await self.vehicle_repo.find_by_id(request.vehicle_id)
            if not vehicle:
                raise ValueError("Provided vehicle_id does not exist.")
            # Verify driver ownership
            driver_vehicles = await self.driver_vehicle_repo.find_by_driver_id(driver.id)
            if not any(dv.vehicle_id == vehicle.id for dv in driver_vehicles):
                raise ValueError("Vehicle does not belong to this driver.")

            vehicle.brand = request.brand
            vehicle.model = request.model
            vehicle.year = request.production_year
            vehicle.color = request.color
            vehicle.plate_number = request.plate_number
            vehicle.max_passengers = request.max_passengers
            vehicle.vehicle_type = request.vehicle_type
            await self.vehicle_repo.update(vehicle)
        else:
            vehicle = Vehicle(
                id=uuid.uuid4(),
                brand=request.brand,
                model=request.model,
                year=request.production_year,
                color=request.color,
                plate_number=request.plate_number,
                max_passengers=request.max_passengers,
                vehicle_type=request.vehicle_type,
            )
            await self.vehicle_repo.save(vehicle)
            await self.driver_vehicle_repo.link_driver_vehicle(
                driver_id=driver.id, vehicle_id=vehicle.id
            )

        await self.driver_vehicle_repo.set_active_vehicle(driver.id, vehicle.id)

        bucket = self.settings.S3_VEHICLE_BUCKET
        doc_types = [
            DocumentType.REGISTRATION_DOC_FRONT,
            DocumentType.REGISTRATION_DOC_BACK,
            DocumentType.VEHICLE_PHOTO_FRONT,
            DocumentType.VEHICLE_PHOTO_BACK,
        ]

        urls = {}
        for doc_type in doc_types:
            urls[doc_type.value] = await self._upsert_document(
                entity_id=vehicle.id,
                entity_type=EntityType.VEHICLE,
                doc_type=doc_type,
                user_id=user_id,
                bucket_name=bucket,
                key_prefix=f"vehicle/{vehicle.id}",
            )

        return DocumentUploadUrlsResponse(urls=urls)

    async def _compute_group_status(
        self, docs: list[Document], required_types: list[DocumentType]
    ) -> RequirementGroupStatusResponse:
        """Compute the aggregate status of a requirement group."""
        group_docs = [doc for doc in docs if doc.document_type in required_types]
        
        doc_responses = []
        for doc in group_docs:
            rejection_reason = await self.rejection_resolver.get_rejection_reason(doc.id)
            
            doc_responses.append(
                DocumentStatusResponse(
                    id=doc.id,
                    document_type=doc.document_type,
                    status=doc.verification_status,
                    rejection_reason=rejection_reason,
                    submitted_at=doc.created_at,
                )
            )

        if not group_docs or len(group_docs) < len(required_types):
            return RequirementGroupStatusResponse(
                status="not_submitted", documents=doc_responses
            )

        is_all_verified = all(d.verification_status == VerificationStatus.VERIFIED for d in group_docs)
        if is_all_verified:
            return RequirementGroupStatusResponse(
                status="verified", documents=doc_responses
            )

        has_rejected = any(d.verification_status == VerificationStatus.REJECTED for d in group_docs)
        if has_rejected:
            rejected_doc = next(
                (d for d in doc_responses if d.status == VerificationStatus.REJECTED), None
            )
            return RequirementGroupStatusResponse(
                status="rejected",
                documents=doc_responses,
                rejection_reason=rejected_doc.rejection_reason if rejected_doc else None,
            )

        return RequirementGroupStatusResponse(
            status="pending", documents=doc_responses
        )

    async def get_verification_status(self, user_id: uuid.UUID) -> VerificationStatusResponse:
        driver = await self.driver_repo.find_by_user_id(user_id)
        if not driver:
            return VerificationStatusResponse(
                overall_status="not_started",
                identity=RequirementGroupStatusResponse(status="not_submitted", documents=[]),
                license=RequirementGroupStatusResponse(status="not_submitted", documents=[]),
                selfie=RequirementGroupStatusResponse(status="not_submitted", documents=[]),
                vehicle=RequirementGroupStatusResponse(status="not_submitted", documents=[]),
            )

        driver_docs = await self.document_repo.find_by_entity_id(driver.id)
        
        identity_status = await self._compute_group_status(
            driver_docs, [DocumentType.ID_FRONT, DocumentType.ID_BACK]
        )
        license_status = await self._compute_group_status(
            driver_docs, [DocumentType.LICENSE_FRONT, DocumentType.LICENSE_BACK]
        )
        selfie_status = await self._compute_group_status(
            driver_docs, [DocumentType.SELFIE_ID]
        )

        active_driver_vehicle = await self.driver_vehicle_repo.find_active_by_driver_id(driver.id)
        vehicle_docs = []
        if active_driver_vehicle:
            vehicle_docs = await self.document_repo.find_by_entity_id(active_driver_vehicle.vehicle_id)

        vehicle_status = await self._compute_group_status(
            vehicle_docs,
            [
                DocumentType.REGISTRATION_DOC_FRONT,
                DocumentType.REGISTRATION_DOC_BACK,
                DocumentType.VEHICLE_PHOTO_FRONT,
                DocumentType.VEHICLE_PHOTO_BACK,
            ],
        )

        statuses = [identity_status.status, license_status.status, selfie_status.status, vehicle_status.status]
        
        if driver.verification_status == VerificationStatus.UNDER_REVIEW:
            overall_status = "under_review"
        elif "rejected" in statuses:
            overall_status = "rejected"
        elif all(s == "verified" for s in statuses):
            overall_status = "verified"
        elif all(s == "not_submitted" for s in statuses):
            overall_status = "not_started"
        else:
            overall_status = "pending"

        return VerificationStatusResponse(
            driver_id=driver.id,
            overall_status=overall_status,
            identity=identity_status,
            license=license_status,
            selfie=selfie_status,
            vehicle=vehicle_status,
        )
