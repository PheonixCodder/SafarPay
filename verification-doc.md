# Verification

## Overview

Driver onboarding and verification service. Drivers submit identity documents, license, selfie, and vehicle information. Documents undergo automated ML-based verification checks (identity matching, license validity) before final approval.

## Insights

```json
1. If the verification flow is not yet started (driver creation not started) this is the response from /me route:
{
    driver_id: uuid.UUID,
    overall_status: "not_started",
    identity: {
        status: "not_submitted",
        documents: [
            DocumentStatusResponse(id=uuid.UUID, document_type="ID_FRONT", status="not_submitted", rejection_reason=None, submitted_at=None),
            DocumentStatusResponse(id=uuid.UUID, document_type="ID_BACK", status="not_submitted", rejection_reason=None, submitted_at=None)
        ],
        rejection_reason: None,
    },
    license: { status: "not_submitted", documents: [...], rejection_reason: None },
    selfie: { status: "not_submitted", documents: [...], rejection_reason: None },
    vehicle: { status: "not_submitted", documents: [...], rejection_reason: None }
}
2. When the user submits the details and documents of any section it will check if there is a driver doc in the database if the doc is not there it will create a new one and save it in the database.
3. 
```

## Driver Creation & Verification Process

Routes to be used:
```
1. /driver/cnic
2. /driver/selfie
3. /driver/license
4. /driver/vehicle
5. /submit-review
```

Flow:
```
1. Four sections: Driver's License, ID Document, Selfie with ID, Vehicle Registration.
2. Each section opens a screen to submit details and documents.
3. After successful uploads, user is redirected to next section automatically.
4. After all sections completed, user is redirected to review submission screen.
5. On submit review, driver status updates to UNDER_REVIEW, user redirected to home.
6. UNDER_REVIEW: driver cannot update any details or documents.
7. New documents can only be uploaded if section status is REJECTED.
8. Review completion triggers verification.review_completed event to Kafka.
9. Consumer triggers IdentityVerificationEngine:
   - Checks names and CNIC numbers match across ID and license documents
   - If mismatch: reject driver, update status to REJECTED, publish review_completed event
10. If names match: trigger ImageVerificationEngine:
    - Checks selfie face matches ID face
    - If mismatch: reject driver, update status to REJECTED, publish review_completed event
```

---

## Get My Verification Status
```python
# No request body
```

Routes to be used:
```
1. GET /v1/verification/me
```

Flow:

1. **Fetch Driver**: Look up driver by user_id; if not found, return "not_started" response.
2. **Aggregate Status**: For each document group (identity, license, selfie, vehicle):
   - Fetch associated documents from repository
   - Determine group status: "not_submitted", "pending", "verified", or "rejected"
   - Include rejection reasons if any document rejected
3. **Compute Overall Status**:
   - UNDER_REVIEW → "under_review"
   - Any rejected group → "rejected"
   - All verified → "verified"
   - All not_submitted → "not_started"
   - Otherwise → "pending"
4. **Return** VerificationStatusResponse with driver_id, overall_status, and per-group details.

No Kafka events (read-only operation).

No WebSocket events (read-only operation).

Response:
```json
{
    "driver_id": "UUID | null",
    "overall_status": "not_started|under_review|pending|verified|rejected",
    "identity": {
        "status": "pending|verified|rejected|not_submitted",
        "documents": [
            {
                "id": "UUID",
                "document_type": "ID_FRONT|ID_BACK|...",
                "status": "pending|verified|rejected",
                "rejection_reason": "string | null",
                "submitted_at": "datetime | null"
            }
        ],
        "rejection_reason": "string | null"
    },
    "license": { ...same structure... },
    "selfie": { ...same structure... },
    "vehicle": { ...same structure... }
}
```

## Submit Identity Documents
```python
class IdentitySubmissionRequest(BaseModel):
    id_number: str = Field(..., description="The National Identity Card Number")
    expiry_date: date = Field(..., description="Expiry date of the CNIC")
```

Routes to be used:
```
1. POST /v1/verification/driver/cnic
```

Flow:

1. **Ensure Driver**: Fetch driver by user_id; create new Driver if not exists (verification_status=PENDING).
2. **Check Review State**: If driver.verification_status is UNDER_REVIEW, raise error (cannot modify during review).
3. **Process Documents**: For each doc_type [ID_FRONT, ID_BACK]:
   - Look up existing document by entity_id and document_type
   - If exists: update with new key (generated from user_id/prefix/uuid), reset status to PENDING, clear prior rejection
   - If not exists: create new Document with PENDING status
   - Generate presigned PUT URL for S3 upload (using identity bucket)
   - Delete old file from S3 if updating
4. **Persist**: Save/update document records.
5. **Return**: DocumentUploadUrlsResponse with presigned URLs keyed by document type.

No Kafka events.

Response:
```json
{
    "message": "Success. Please use these URLs to upload the required documents via PUT requests.",
    "urls": {
        "id_front": {
            "key": "user_id/identity/id_front_uuid",
            "url": "https://s3-presigned-put-url"
        },
        "id_back": {
            "key": "user_id/identity/id_back_uuid",
            "url": "https://s3-presigned-put-url"
        }
    }
}
```

## Submit License Documents
```python
class LicenseSubmissionRequest(BaseModel):
    license_number: str = Field(..., description="Driving License Number")
    expiry_date: date = Field(..., description="Expiry date of the Driving License")
```

Routes to be used:
```
1. POST /v1/verification/driver/license
```

Flow:

1. **Ensure Driver**: Fetch/create driver (same as identity flow).
2. **Check Review State**: Reject if UNDER_REVIEW.
3. **Process Documents**: For each doc_type [LICENSE_FRONT, LICENSE_BACK]:
   - Look up existing document
   - Generate new key, update/create document, set status=PENDING
   - Generate presigned PUT URL (using license bucket)
   - Clean up old file if updating
4. **Persist**: Save document records with license_number and expiry_date metadata.
5. **Return**: DocumentUploadUrlsResponse with presigned URLs.

No Kafka events.

Response:
```json
{
    "message": "Success. Please use these URLs to upload the required documents via PUT requests.",
    "urls": {
        "license_front": {"key": "...", "url": "..."},
        "license_back": {"key": "...", "url": "..."}
    }
}
```

## Submit Selfie
```python
class SelfieSubmissionRequest(BaseModel):
    # No text fields required for this step, just signaling the step
    pass
```

Routes to be used:
```
1. POST /v1/verification/driver/selfie
```

Flow:

1. **Ensure Driver**: Fetch/create driver.
2. **Check Review State**: Reject if UNDER_REVIEW.
3. **Process Document**: For doc_type [SELFIE_ID]:
   - Look up existing document
   - Generate new key, update/create document, set status=PENDING
   - Generate presigned PUT URL (using license bucket)
4. **Persist**: Save document record.
5. **Return**: DocumentUploadUrlsResponse with single selfie URL.

No Kafka events.

Response:
```json
{
    "message": "Success. Please use these URLs to upload the required documents via PUT requests.",
    "urls": {
        "selfie_id": {"key": "user_id/selfie/selfie_id_uuid", "url": "https://s3-presigned-put-url"}
    }
}
```

## Submit Vehicle Information & Documents
```python
class VehicleSubmissionRequest(BaseModel):
    vehicle_id: uuid.UUID | None = Field(None, description="Provide this to update an existing vehicle.")
    brand: str = Field(..., min_length=1, max_length=50)
    model: str = Field(..., min_length=1, max_length=50)
    color: str = Field(..., min_length=1, max_length=30)
    vehicle_type: VehicleType
    max_passengers: int = Field(4, ge=1, le=10)
    plate_number: str = Field(..., min_length=1, max_length=20)
    production_year: int = Field(..., ge=1980, le=2100)
```

Routes to be used:
```
1. POST /v1/verification/driver/vehicle
```

Flow:

1. **Ensure Driver**: Fetch driver by user_id.
2. **Check Review State**: Reject if UNDER_REVIEW.
3. **Check Existing Vehicles**: Query DriverVehicle for this driver. If vehicle_id provided:
   - Verify vehicle exists and belongs to driver
   - Verify no other vehicle of same type exists for driver (except the one being updated)
   - Update vehicle record with new details
4. **Create New Vehicle** (if no vehicle_id):
   - Verify no other vehicle of same type exists
   - Create Vehicle record
   - Link to driver via DriverVehicle junction table
5. **Set Active Vehicle**: Mark this vehicle as currently selected for the driver.
6. **Process Documents**: For each doc_type [REGISTRATION_DOC_FRONT, REGISTRATION_DOC_BACK, VEHICLE_PHOTO_FRONT, VEHICLE_PHOTO_BACK]:
   - Look up existing document by vehicle entity_id
   - Generate new key, update/create document, set status=PENDING
   - Generate presigned PUT URL (using vehicle bucket)
7. **Persist**: Save all vehicle and document records.
8. **Return**: DocumentUploadUrlsResponse with presigned URLs for all vehicle documents.

No Kafka events.

Response:
```json
{
    "message": "Success. Please use these URLs to upload the required documents via PUT requests.",
    "urls": {
        "registration_doc_front": {"key": "...", "url": "..."},
        "registration_doc_back": {"key": "...", "url": "..."},
        "vehicle_photo_front": {"key": "...", "url": "..."},
        "vehicle_photo_back": {"key": "...", "url": "..."}
    }
}
```

## Submit for Review
```python
# No request body
```

Routes to be used:
```
1. POST /v1/verification/submit-review
```

Flow:

1. **Fetch Driver**: Retrieve driver by user_id; error if not found.
2. **Check Preconditions**:
   - If already UNDER_REVIEW: error
   - If already VERIFIED/REJECTED: error (finalized)
3. **Fetch Driver Documents**: Get all documents for driver entity.
4. **Validate Required Driver Docs**: Check presence of {ID_FRONT, ID_BACK, LICENSE_FRONT, LICENSE_BACK, SELFIE_ID}. Error if any missing.
5. **Fetch Active Vehicle**: Query DriverVehicle for driver's active vehicle; error if none.
6. **Fetch Vehicle Documents**: Get all documents for vehicle entity.
7. **Validate Required Vehicle Docs**: Check presence of {REGISTRATION_DOC_FRONT, REGISTRATION_DOC_BACK, VEHICLE_PHOTO_FRONT, VEHICLE_PHOTO_BACK}. Error if any missing.
8. **Update Driver Status**: Set verification_status=UNDER_REVIEW, increment review_attempts, set last_reviewed_at=now.
9. **Persist**: Save updated driver.
10. **Kafka - VerificationReviewRequestedEvent**: Publish to topic `verification.review_requested`:

    ```json
    {
        "event_id": "UUID",
        "event_type": "verification.review_requested",
        "timestamp": "2026-01-01T00:00:00Z",
        "version": 1,
        "idempotency_key": "UUID",
        "correlation_id": "UUID | null",
        "payload": {
            "user_id": "UUID",
            "driver_id": "UUID"
        }
    }
    ```

11. **Return**: ReviewSubmissionResponse with status and estimated processing time.

Kafka Event payloads:
```json
VerificationReviewRequestedEvent:
    {
        "event_id": "UUID",
        "event_type": "verification.review_requested",
        "timestamp": "2026-01-01T00:00:00Z",
        "version": 1,
        "idempotency_key": "UUID",
        "correlation_id": "UUID | null",
        "payload": {
            "user_id": "UUID",
            "driver_id": "UUID"
        }
    }
```

## Kafka Events (Background Processing)

When review is submitted, a background worker picks up the VerificationReviewRequestedEvent and executes ML-based verification:

1. **Acquire Lock**: Redis distributed lock (180s TTL) prevents duplicate processing
2. **Fetch Documents**: ID_FRONT, ID_BACK, LICENSE_FRONT, LICENSE_BACK, SELFIE_ID + vehicle docs
3. **Download from S3**: Parallel fetch of document bytes
4. **Run IdentityVerificationEngine**:
   - OCR extraction from ID and license documents (cnic_raw_text, license_raw_text)
   - Name and CNIC number matching across documents
   - Face matching between selfie and ID photo
5. **Result Handling**:
   - **Success**: All documents → VERIFIED, driver → VERIFIED
   - **Failure**:
     - MLProcessingError or mismatched data → all identity docs → REJECTED, driver → REJECTED
     - VerificationRejection records created for each error with rejection_reason_code
   - **Persist OCR results** in document.metadata_json
6. **Publish Events** (note: the existing code publishes review_requested on submission; review completion updates DB state but no explicit event published — consumer may emit document.verified events separately)

---

# Database Models (Domain Layer)

## Driver
```python
class Driver:
    id: uuid.UUID
    user_id: uuid.UUID
    verification_status: VerificationStatus = VerificationStatus.PENDING
    review_attempts: int = 0
    last_reviewed_at: datetime | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
```

## Vehicle
```python
class Vehicle:
    id: uuid.UUID
    brand: str
    model: str
    year: int
    color: str
    plate_number: str
    max_passengers: int = 4
    vehicle_type: VehicleType = VehicleType.ECONOMY
    verification_status: VerificationStatus = VerificationStatus.PENDING
    is_active: bool = True
    created_at: datetime | None = None
    updated_at: datetime | None = None
```

## DriverVehicle
```python
class DriverVehicle:
    id: uuid.UUID
    driver_id: uuid.UUID
    vehicle_id: uuid.UUID
    vehicle_type: VehicleType = VehicleType.ECONOMY
    is_currently_selected: bool = False
    assigned_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    created_at: datetime | None = None
    updated_at: datetime | None = None
```

## Document
```python
class Document:
    id: uuid.UUID
    document_type: DocumentType
    file_key: str
    entity_id: uuid.UUID
    entity_type: EntityType
    document_number: str | None = None
    expiry_date: date | None = None
    verification_status: VerificationStatus = VerificationStatus.PENDING
    metadata_json: dict | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
```

## VerificationRejection
```python
class VerificationRejection:
    id: uuid.UUID
    driver_id: uuid.UUID
    rejection_reason_code: str
    document_id: uuid.UUID | None = None
    admin_comment: str | None = None
    is_resolved: bool = False
    rejected_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    created_at: datetime | None = None
    updated_at: datetime | None = None
```

## DriverStats
```python
class DriverStats:
    driver_id: uuid.UUID
    rating_avg: float = 0.0
    total_rides: int = 0
    acceptance_rate: float = 0.0
    cancellation_rate: float = 0.0
    online_minutes_today: int = 0
```

---

# Enums

## VerificationStatus
```python
class VerificationStatus(str, Enum):
    PENDING = "pending"
    UNDER_REVIEW = "under_review"
    VERIFIED = "verified"
    REJECTED = "rejected"
    SUSPENDED = "suspended"
```

## VehicleType
```python
class VehicleType(str, Enum):
    MOTO = "moto"
    ECONOMY = "economy"
    COMFORT = "comfort"
    FREIGHT = "freight"
```

## EntityType
```python
class EntityType(str, Enum):
    DRIVER = "driver"
    VEHICLE = "vehicle"
```

## DocumentType
```python
class DocumentType(str, Enum):
    ID_FRONT = "id_front"
    ID_BACK = "id_back"
    SELFIE_ID = "selfie_id"
    LICENSE_FRONT = "license_front"
    LICENSE_BACK = "license_back"
    REGISTRATION_DOC_FRONT = "registration_doc_front"
    REGISTRATION_DOC_BACK = "registration_doc_back"
    VEHICLE_PHOTO_FRONT = "vehicle_photo_front"
    VEHICLE_PHOTO_BACK = "vehicle_photo_back"
```

---

# Routes Summary

### Verification Service Routes

| Method | URL | Description |
|--------|-----|-------------|
| GET | `/v1/verification/me` | Get my full verification status |
| POST | `/v1/verification/driver/cnic` | Submit identity documents (CNIC front & back) |
| POST | `/v1/verification/driver/license` | Submit driving license documents (front & back) |
| POST | `/v1/verification/driver/selfie` | Submit selfie with driving license |
| POST | `/v1/verification/driver/vehicle` | Submit vehicle information and registration/photo documents |
| POST | `/v1/verification/submit-review` | Submit all documents for verification review |

### WebSocket Endpoints
_None — verification uses Kafka for async events_

### Kafka Events

#### VerificationReviewRequestedEvent
Published to topic `verification.review_requested` when a driver submits for review.

Payload:
```json
{
    "user_id": "UUID",
    "driver_id": "UUID"
}
```

#### (Background) Verification Outcomes
The background worker updates document and driver statuses to VERIFIED or REJECTED based on ML engine results. Rejection details are stored in VerificationRejection records. Per-document verification may emit `document.verified` events.

---

# Infrastructure Components

## 1. IdentityVerificationEngine

This is an ML service that performs OCR, face matching, and name verification across identity documents.

### Purpose

Automate KYC verification using computer vision and ML to validate that identity documents are authentic, not expired, and belong to the same person.

### Key Methods

- `run(bundle: VerificationBundle)`: Main entry point that processes all documents. Runs OCR on ID front/back and license front, extracts names, cross-checks them with fuzzy matching, validates expiry dates, and performs face matching between selfie and ID photo.
- `_extract_ocr(image_bytes)`: Uses PaddleOCR to extract text from document images.
- `_crop_face(image_bytes)`: Uses DeepFace to detect and crop face from ID photo.
- `_match_faces(selfie_bytes, id_face_img)`: Compares selfie against ID face using Facenet512 model (distance < 0.6 = match).
- `_cross_check_names(*names)`: Fuzzy matches names across documents using rapidfuzz (threshold 85%).
- `_parse_date(text)`: Extracts expiry dates using dateutil parser with keyword matching.

### Design Decisions

- **Semaphore-limited concurrency**: Only 2 concurrent verifications allowed (async semaphore) to control GPU/memory usage.
- **Timeout protection**: 60-second timeout on entire ML pipeline to prevent hanging.
- **OCR caching**: Extracted text is cached in document metadata to avoid re-processing on retries.
- **Async wrapper over sync ML**: Heavy ML operations (OpenCV, DeepFace, PaddleOCR) run in thread pool via `run_in_executor` to avoid blocking event loop.
- **Graceful degradation**: Specific ML errors (face detection failure) are captured as `MLProcessingError` rather than crashing the entire flow.

---

## 2. RejectionResolver

Helper service that fetches and manages verification rejection reasons.

### Purpose

Encapsulates the logic for retrieving the latest active rejection reason for a document, keeping the use cases clean.

### Key Methods

- `get_rejection_reason(document_id)`: Returns the latest non-resolved rejection reason (admin comment or reason code) for a document.
- `resolve_previous_rejections(document_id)`: Marks all active rejections for a document as resolved when the document is re-submitted.

### Design Decisions

- **Separation of concerns**: Use cases don't need to know rejection repository details.
- **Idempotency**: Allows documents to be re-updated without needing to manually clear old rejections.

---

## 3. S3StorageProvider

Implements the `StorageProviderProtocol` using AWS S3 for document storage.

### Purpose

Provides presigned URLs for direct client-to-S3 uploads and downloads, keeping the service stateless and not handling large binary payloads.

### Key Methods

- `generate_presigned_put_url(bucket, key, expires_in, content_type)`: Generates a presigned PUT URL for uploading a document (default 1 hour expiry).
- `get_object_bytes(bucket, key)`: Fetches raw bytes from S3 for ML processing (runs in thread pool).
- `delete_object(bucket, key)`: Removes old document versions when updating (error-tolerant - logs but doesn't fail).

### Design Decisions

- **Async boto3**: All S3 operations run via `asyncio.to_thread` to avoid blocking.
- **No direct binary handling**: Service never receives document bytes, only S3 keys - reduces memory and bandwidth usage.
- **Region configuration**: Falls back to 'us-east-1' if AWS_REGION not set.

---

## 4. Verification ORM Models

SQLAlchemy models mapping to the `verification` schema in PostgreSQL.

### Models

- **DriverORM**: Core driver profile, linked to auth users (1:1). Tracks verification status, review attempts, and last review timestamp.
- **VehicleORM**: Vehicle details with verification status. One driver can have multiple vehicles (via DriverVehicle).
- **DocumentORM**: Polymorphic document storage with `entity_id` and `entity_type`. Stores file_key (S3 path), document type, verification status, and OCR metadata (JSONB).
- **DriverVehicleORM**: Junction table linking drivers to vehicles with a unique constraint on (driver_id, vehicle_type).
- **VerificationRejectionORM**: Audit trail of rejections linked to specific documents.
- **DriverStatsORM**: Cached performance metrics (rating, total rides, acceptance/cancellation rates).

### Design Decisions

- **Unified document table**: Single `documents` table handles all entity types (driver and vehicle documents) via `entity_type` discriminator.
- **Soft delete via status**: Documents/vehicles aren't hard-deleted; status changes track lifecycle.
- **JSONB metadata**: Stores OCR results and other flexible attributes without schema changes.
- **Multiple schema**: All tables in `verification` schema, isolating from other services.

---

## 5. Verification Repositories

Concrete implementations of domain repository protocols using SQLAlchemy.

### Repositories

- **DriverRepository**: CRUD for drivers, find by user_id.
- **VehicleRepository**: CRUD for vehicles, unique plate enforcement at DB level.
- **DocumentRepository**: Finds documents by entity, handles updates with metadata (OCR text), manages S3 key rotations.
- **DriverVehicleRepository**: Links drivers to vehicles, enforces single active vehicle per driver, unique vehicle type per driver.
- **VerificationRejectionRepository**: Creates and queries rejections, marks resolved.

### Design Decisions

- **Protocol-based**: All repos implement domain interfaces, enabling testing via mocks.
- **ORM-to-domain mapping**: Clean separation - use cases work with domain objects only.
- **Atomic updates**: Status changes and metadata updates happen in single transaction.

---

## 6. Verification Dependencies

FastAPI dependency injection providers that wire infrastructure to use cases.

### Providers

- **Repository providers**: Create repo instances with request-scoped DB sessions.
- **StorageProvider**: Singleton S3 client.
- **IdentityEngine**: Retrieved from app state (singleton) - ML model loaded once.
- **EventPublisher**: From app state, publishes Kafka events.
- **CacheManager**: From app state, for distributed locks and caching.
- **RejectionResolver**: Scoped with rejection repository.

### Design Decisions

- **App state pattern**: Heavy objects (ML engine, publisher, cache) stored in FastAPI app.state to avoid per-request initialization.
- **Constructor injection**: Use cases receive all dependencies via __init__, making them testable.
- **Type aliases**: Clean dependency annotations (e.g., `DriverRepo = Annotated[...]`).

---

## 7. Verification Use Cases

Business logic orchestrator for the verification flow.

### Key Methods

- `_ensure_driver(user_id)`: Gets or creates driver, checks UNDER_REVIEW status.
- `submit_identity_documents/license/selfie/vehicle()`: Generates presigned URLs, upserts documents, cleans old S3 files.
- `request_verification_review()`: Validates all docs present, sets status to UNDER_REVIEW, publishes `VerificationReviewRequestedEvent`.
- `execute_verification_review()`: Background worker - acquires Redis lock, fetches S3 docs, runs ML engine, updates statuses, creates rejections on failure.
- `get_verification_status()`: Aggregates document statuses into overall driver status (not_started/pending/under_review/verified/rejected).

### Design Decisions

- **Redis distributed lock**: Prevents duplicate ML processing of same driver (180s TTL).
- **S3 parallel fetch**: Downloads all documents concurrently before ML processing.
- **Idempotent review**: Checks existing status before processing; skips if already VERIFIED/REJECTED.
- **Per-document rejection tracking**: Each failed document gets a rejection record with specific error code.
- **OCR persistence**: ML-extracted text saved to document metadata for future reference.

---

# End-to-end Flow

## 1. Document Submission (Happy Path)

1. **Client** → POST `/v1/verification/driver/cnic` with id_number and expiry_date
2. **Route** → `VerificationRouter` calls `submit_identity_documents` use case
3. **Use Case** → `_ensure_driver()` creates/finds driver record
4. **Repository** → `DocumentRepository` checks for existing document
5. **Storage** → `S3StorageProvider` generates presigned PUT URL (identity/id_front_uuid)
6. **Client** → PUTs document bytes directly to S3 (bypassing service)
7. **Repeat** → Same flow for id_back, license_front, license_back, selfie, vehicle info + docs
8. **Response** → Service returns presigned URLs; no Kafka events (synchronous phase)

## 2. Review Submission

1. **Client** → POST `/v1/verification/submit-review`
2. **Route** → `submit_verification_review` use case
3. **Validation** → Checks all required docs present (ID_FRONT/BACK, LICENSE_FRONT/BACK, SELFIE_ID, vehicle docs)
4. **Status Update** → Driver status → UNDER_REVIEW, increments review_attempts
5. **Kafka Publish** → `VerificationReviewRequestedEvent` to topic `verification.review_requested`
6. **Response** → Returns estimated_time_seconds=30

## 3. Background ML Verification

1. **Kafka Consumer** → Picks up `VerificationReviewRequestedEvent` (or scheduled task)
2. **Lock Acquire** → `CacheManager.set(nx=True, ttl=180)` prevents concurrent processing
3. **Fetch Documents** → `DocumentRepository.find_by_entity_id(driver.id)` gets all docs
4. **Parallel S3 Fetch** → `storage.get_object_bytes()` for ID_FRONT/BACK, LICENSE_FRONT/BACK, SELFIE_ID
5. **ML Engine** → `identity_engine.run(VerificationBundle)`:
   - OCR on ID and license (text extraction)
   - Name extraction and fuzzy matching (85% threshold)
   - Expiry date validation
   - Face detection and matching (DeepFace, threshold 0.6)
6. **Result Handling**:
   - **Success**: All docs → VERIFIED, driver → VERIFIED
   - **Failure**: Identity docs → REJECTED, driver → REJECTED, create `VerificationRejection` records per error
   - **MLProcessingError**: Specific handling, log and reject
7. **Metadata Update**: OCR results saved to document.metadata_json
8. **Kafka Events**: Status changes may emit document.verified events

## 4. Status Query

1. **Client** → GET `/v1/verification/me`
2. **Route** → `get_verification_status` use case
3. **Fetch** → Driver + all documents (grouped by type)
4. **Aggregate** → Per-group status (not_submitted/pending/verified/rejected)
5. **Compute** → Overall status based on driver status + group statuses
6. **Response** → VerificationStatusResponse with full breakdown

---

# Architectural Roles

- **IdentityVerificationEngine**: Executes ML-based KYC checks (OCR, face matching, name/date extraction) with concurrency control and timeout protection.
- **RejectionResolver**: Encapsulates rejection history lookup and resolution logic for clean use case code.
- **S3StorageProvider**: Manages document storage via presigned URLs, eliminating binary payload handling from the service.
- **Verification ORM Models**: Define `verification` schema entities (Driver, Vehicle, Document, DriverVehicle, Rejection) with proper relationships and constraints.
- **Verification Repositories**: Implement domain persistence contracts using SQLAlchemy with request-scoped sessions.
- **Verification Dependencies**: Wire FastAPI request lifecycle to domain use cases via dependency injection providers.
- **Verification Use Cases**: Orchestrate document submission, ML verification, status aggregation, and rejection tracking with distributed locking.

---

# See also

* **CLAUDE.md** — Project overview, service descriptions, dev commands
* **auth-doc.md**, **bidding-doc.md**, **ride-doc.md**, **location-doc.md** — Other service documentation
* **`libs/platform/src/sp/infrastructure/messaging/publisher.py`** — EventPublisher used for verification events
* **`libs/platform/src/sp/infrastructure/cache/manager.py`** — CacheManager for Redis distributed locks
* **`services/verification/verification/main.py`** — FastAPI app initialization and ML engine startup
