# Verification Service Documentation

## Overview

The Verification service owns driver onboarding and KYC. A user becomes a driver candidate by submitting identity documents, driving license documents, selfie with ID, and vehicle information/documents. The service returns S3 presigned PUT URLs for direct client uploads, then processes review requests through ML-backed background verification.

Base path:

```text
/api/v1/verification
```

HTTP endpoints require an authenticated auth user through `CurrentUser`. The driver profile is keyed by `verification.drivers.id`, while the caller identity comes from auth `users.id`.

---

## Driver Service And Vehicle Taxonomy

Verification owns driver vehicles and driver service capabilities.

Canonical physical vehicles:

```text
CAR, MOTORCYCLE, RICKSHAW, VAN, PICKUP, MINI_TRUCK, TRUCK
```

Driver service capabilities:

```text
CITY_RIDE, INTERCITY, FREIGHT, COURIER, GROCERY
```

Rules:

- `vehicle_type` is the physical vehicle only.
- `service_type` is the driver work capability enabled by that vehicle.
- A driver cannot register more than one vehicle of the same canonical vehicle type.
- Submitting vehicle information with `service_type` creates or reactivates a `driver_service_capabilities` record for that `driver + vehicle + service_type`.

---

## Verification Lifecycle

```text
not_started -> pending -> under_review -> verified
                                      \-> rejected
```

Rules:

- If no driver exists for the current user, `/me` returns `overall_status="not_started"`.
- Submitting any section creates the driver record if missing and sets submitted documents to `pending`.
- Documents cannot be changed while driver status is `under_review`.
- `submit-review` requires all driver and vehicle documents.
- `submit-review` rejects drivers already `under_review`, `verified`, or `rejected`.
- Background review updates document and driver states to `verified` or `rejected`.
- Rejections are stored in `VerificationRejection` records and are resolved when documents are resubmitted.

---

## Get My Verification Status

Route:

```text
GET /api/v1/verification/me
```

Flow:

1. Load driver by `current_user.user_id`.
2. If driver does not exist, return grouped `not_submitted` status and `overall_status="not_started"`.
3. Load driver documents and active vehicle documents.
4. Compute group status for identity, license, selfie, and vehicle.
5. Resolve rejection reasons for rejected documents.
6. Compute overall status:
   - driver `UNDER_REVIEW` -> `under_review`
   - any group rejected -> `rejected`
   - all groups verified -> `verified`
   - all groups not submitted -> `not_started`
   - otherwise -> `pending`

Response:

```json
{
  "driver_id": "UUID | null",
  "overall_status": "not_started|pending|under_review|verified|rejected",
  "identity": {
    "status": "not_submitted|pending|verified|rejected",
    "documents": [],
    "rejection_reason": "string | null"
  },
  "license": { "status": "pending", "documents": [], "rejection_reason": null },
  "selfie": { "status": "pending", "documents": [], "rejection_reason": null },
  "vehicle": { "status": "pending", "documents": [], "rejection_reason": null }
}
```

---

## Submit Identity Documents

Route:

```text
POST /api/v1/verification/driver/cnic
```

Schema:

```python
class IdentitySubmissionRequest(BaseModel):
    id_number: str
    expiry_date: date
```

Flow:

1. Ensure driver exists for current auth user.
2. Reject if driver is `UNDER_REVIEW`.
3. Upsert `ID_FRONT` and `ID_BACK` document records.
4. Store `id_number` on both document records.
5. Store CNIC `expiry_date` on `ID_FRONT` only; `ID_BACK` has no expiry date.
6. Resolve old rejections for replaced documents.
7. Delete old S3 objects when replacing previous file keys.
8. Return presigned PUT URLs.

Response:

```json
{
  "message": "Success. Please use these URLs to upload the required documents via PUT requests.",
  "urls": {
    "id_front": { "key": "s3-key", "url": "https://presigned-put" },
    "id_back": { "key": "s3-key", "url": "https://presigned-put" }
  }
}
```

---

## Submit License Documents

Route:

```text
POST /api/v1/verification/driver/license
```

Schema:

```python
class LicenseSubmissionRequest(BaseModel):
    license_number: str
    expiry_date: date
```

Flow:

1. Ensure driver exists.
2. Reject if driver is `UNDER_REVIEW`.
3. Upsert `LICENSE_FRONT` and `LICENSE_BACK`.
4. Store license number and expiry metadata.
5. Resolve previous rejections and rotate S3 keys on update.
6. Return presigned PUT URLs.

Pakistan e-license handling:

- The API shape stays the same and still returns both `license_front` and `license_back` upload URLs.
- For e-license documents that only have a front image, upload the same front image to both returned URLs.
- For physical licenses, upload the separate front and back images.

Response URLs:

```json
{
  "license_front": { "key": "s3-key", "url": "https://presigned-put" },
  "license_back": { "key": "s3-key", "url": "https://presigned-put" }
}
```

---

## Submit Selfie With ID

Route:

```text
POST /api/v1/verification/driver/selfie
```

Schema:

```python
class SelfieSubmissionRequest(BaseModel):
    pass
```

Flow:

1. Ensure driver exists.
2. Reject if driver is `UNDER_REVIEW`.
3. Upsert `SELFIE_ID`.
4. Resolve old rejection if replacing a rejected selfie.
5. Return one presigned PUT URL.

Response URLs:

```json
{
  "selfie_id": { "key": "s3-key", "url": "https://presigned-put" }
}
```

---

## Submit Vehicle Information And Documents

Route:

```text
POST /api/v1/verification/driver/vehicle
```

Schema:

```python
class VehicleSubmissionRequest(BaseModel):
    vehicle_id: UUID | None = None
    brand: str
    model: str
    color: str
    vehicle_type: VehicleType
    service_type: ServiceType | None = None
    max_passengers: int = Field(4, ge=1, le=10)
    plate_number: str
    production_year: int = Field(..., ge=1980, le=2100)
```

Flow:

1. Ensure driver exists.
2. Reject if driver is `UNDER_REVIEW`.
3. Load all vehicles linked to this driver.
4. If `vehicle_id` is provided:
   - vehicle must exist,
   - vehicle must belong to this driver,
   - no other linked vehicle may already have the requested `vehicle_type`,
   - update brand, model, year, color, plate number, max passengers, and type.
5. If `vehicle_id` is absent:
   - reject if another vehicle of same `vehicle_type` is already linked,
   - create a new vehicle,
   - link it to the driver.
6. Mark this vehicle as the driver's active selected vehicle.
7. Upsert vehicle documents:
   - `REGISTRATION_DOC_FRONT`
   - `REGISTRATION_DOC_BACK`
   - `VEHICLE_PHOTO_FRONT`
   - `VEHICLE_PHOTO_BACK`
8. Registration documents do not carry expiry dates in this service.
9. Resolve old document rejections and rotate S3 keys.
10. Return presigned PUT URLs.

Response URLs:

```json
{
  "registration_doc_front": { "key": "s3-key", "url": "https://presigned-put" },
  "registration_doc_back": { "key": "s3-key", "url": "https://presigned-put" },
  "vehicle_photo_front": { "key": "s3-key", "url": "https://presigned-put" },
  "vehicle_photo_back": { "key": "s3-key", "url": "https://presigned-put" }
}
```

---

## Driver Vehicle Summary

Route:

```text
GET /api/v1/verification/driver/vehicles/summary?service_type=CITY_RIDE
```

Flow:

1. Load the current driver's linked vehicles.
2. Load `driver_service_capabilities` for that driver.
3. Return each vehicle with its physical type, vehicle id, attached services, and vehicle document group status.
4. `is_registered_for_service` is true when the vehicle already has an active capability for the requested service.

Response shape:

```json
{
  "service_type": "CITY_RIDE",
  "vehicles": [
    {
      "vehicle_type": "CAR",
      "vehicle_id": "UUID",
      "is_registered_for_service": true,
      "services": [{ "service_type": "CITY_RIDE", "is_active": true }],
      "vehicle_status": "pending",
      "vehicle_documents_status": "pending",
      "brand": "Toyota",
      "model": "Yaris",
      "plate_number": "ABC-123"
    }
  ]
}
```

---

## Attach Existing Vehicle To Service

Route:

```text
POST /api/v1/verification/driver/vehicles/{vehicle_id}/services
```

Request:

```json
{ "service_type": "COURIER" }
```

Flow:

1. Ensure the vehicle belongs to the current driver's linked vehicles.
2. Upsert an active `driver_service_capabilities` row for that vehicle and service.
3. Return the updated vehicle summary item.
4. Do not create another vehicle row and do not require vehicle document upload for service reuse.

---

## Submit For Review

Route:

```text
POST /api/v1/verification/submit-review
```

Flow:

1. Load driver by current auth user.
2. Reject if driver is missing.
3. Reject if already `UNDER_REVIEW`.
4. Reject if already `VERIFIED` or `REJECTED`.
5. Validate required driver documents:
   - `ID_FRONT`
   - `ID_BACK`
   - `LICENSE_FRONT`
   - `LICENSE_BACK`
   - `SELFIE_ID`
6. Validate active vehicle exists.
7. Validate required active vehicle documents:
   - `REGISTRATION_DOC_FRONT`
   - `REGISTRATION_DOC_BACK`
   - `VEHICLE_PHOTO_FRONT`
   - `VEHICLE_PHOTO_BACK`
8. Set driver status to `UNDER_REVIEW`.
9. Increment `review_attempts`.
10. Set `last_reviewed_at`.
11. Publish `verification.review_requested`.
12. Return review status and estimated processing time.

Response:

```json
{
  "status": "UNDER_REVIEW",
  "estimated_time_seconds": 30
}
```

Kafka event:

```json
{
  "event_type": "verification.review_requested",
  "payload": {
    "user_id": "UUID",
    "driver_id": "UUID"
  }
}
```

---

## Background ML Verification

Entry point:

```python
VerificationUseCases.execute_verification_review(driver_id)
```

Flow:

1. Acquire Redis distributed lock `verification:review_lock:{driver_id}` with 180 second TTL.
2. Load driver by `driver_id`.
3. Load driver documents and active vehicle documents.
4. Fetch document bytes from S3.
5. Run `IdentityVerificationEngine`.
6. On success:
   - mark documents `VERIFIED`,
   - mark driver `VERIFIED`.
7. On ML or validation failure:
   - mark relevant documents `REJECTED`,
   - mark driver `REJECTED`,
   - create `VerificationRejection` records.
8. Persist OCR/ML metadata in document `metadata_json`.
9. Release Redis lock with `delete_if_equals`.

Current implementation publishes `verification.review_requested` when the review is submitted. Review completion is persisted to the database; no guaranteed `verification.review_completed` Kafka event should be assumed unless added in code.

---

## Domain Models

### Driver

```python
class Driver:
    id: UUID
    user_id: UUID
    verification_status: VerificationStatus
    review_attempts: int
    last_reviewed_at: datetime | None
```

### Vehicle

```python
class Vehicle:
    id: UUID
    brand: str
    model: str
    year: int
    color: str
    plate_number: str
    max_passengers: int
    vehicle_type: VehicleType
    verification_status: VerificationStatus
    is_active: bool
```

### DriverVehicle

```python
class DriverVehicle:
    id: UUID
    driver_id: UUID
    vehicle_id: UUID
    vehicle_type: VehicleType
    is_currently_selected: bool
```

### Document

```python
class Document:
    id: UUID
    document_type: DocumentType
    file_key: str
    entity_id: UUID
    entity_type: EntityType
    document_number: str | None
    expiry_date: date | None
    verification_status: VerificationStatus
    metadata_json: dict | None
```

### VerificationRejection

```python
class VerificationRejection:
    id: UUID
    driver_id: UUID
    rejection_reason_code: str
    document_id: UUID | None
    admin_comment: str | None
    is_resolved: bool
    rejected_at: datetime
```

---

## Enums

```python
class VerificationStatus(str, Enum):
    PENDING = "pending"
    UNDER_REVIEW = "under_review"
    VERIFIED = "verified"
    REJECTED = "rejected"
    SUSPENDED = "suspended"

class VehicleType(str, Enum):
    MOTO = "moto"
    ECONOMY = "economy"
    COMFORT = "comfort"
    FREIGHT = "freight"

class EntityType(str, Enum):
    DRIVER = "driver"
    VEHICLE = "vehicle"

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

## Routes Summary

| Method | URL | Description |
|---|---|---|
| GET | `/api/v1/verification/me` | Get aggregated verification status |
| POST | `/api/v1/verification/driver/cnic` | Submit CNIC/identity details and upload URLs |
| POST | `/api/v1/verification/driver/license` | Submit license details and upload URLs |
| POST | `/api/v1/verification/driver/selfie` | Submit selfie-with-ID upload URL |
| POST | `/api/v1/verification/driver/vehicle` | Create/update vehicle and document upload URLs |
| POST | `/api/v1/verification/submit-review` | Submit completed driver profile for review |

WebSocket endpoints: none.

---

## Infrastructure Components

### IdentityVerificationEngine

Runs OCR and face matching across identity/license/selfie documents. Heavy ML work is isolated from HTTP routes and protected by background review locking.

### RejectionResolver

Reads active rejection reasons and resolves old rejections when documents are resubmitted.

### S3StorageProvider

Generates presigned PUT URLs for client uploads, downloads objects for ML review, and deletes old objects when replacing documents.

### Repositories

- `DriverRepository`
- `VehicleRepository`
- `DocumentRepository`
- `DriverVehicleRepository`
- `VerificationRejectionRepository`

Each maps ORM rows from the `verification` schema into pure domain models.

### Dependencies

FastAPI dependency providers assemble request-scoped repositories with app-state storage, cache, ML engine, rejection resolver, and event publisher.

---

## End-to-End Flow

```text
GET /me
POST /driver/cnic
POST /driver/license
POST /driver/selfie
POST /driver/vehicle
PUT documents directly to S3 using returned URLs
POST /submit-review
background execute_verification_review(driver_id)
GET /me
```

The mobile client never uploads binary files to the Verification service. It receives presigned URLs and uploads directly to S3.

---

## See Also

- `services/verification/verification/api/router.py`
- `services/verification/verification/application/use_cases.py`
- `services/verification/verification/application/schemas.py`
- `services/verification/verification/infrastructure/storage.py`
