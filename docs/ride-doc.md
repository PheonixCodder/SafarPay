# Ride Service Documentation

## Overview

The Ride service owns service-request creation, ride lifecycle state, fixed-price acceptance, stop tracking, ride OTP verification, proof uploads, nearby-driver lookup, Kafka events, and passenger/driver WebSocket updates.

Base path:

```text
/api/v1
```

Identity rule:

- Passenger identity is auth `user_id`.
- Driver identity is verification `driver_id`.
- `CurrentDriver` resolves `driver_id` from `verification.drivers` using the authenticated auth user.
- `OptionalDriverId` is used on routes that can be called by either passenger or driver.

---

## Pricing Modes

```python
class PricingMode(str, Enum):
    FIXED = "FIXED"
    BID_BASED = "BID_BASED"
    HYBRID = "HYBRID"
```

Mode behavior:

| Mode | Assignment path |
|---|---|
| `FIXED` | Driver accepts directly through `POST /rides/{ride_id}/accept` |
| `BID_BASED` | Drivers bid in Bidding service; passenger accepts a bid |
| `HYBRID` | Drivers bid and passenger may counter; passenger or driver can finalize through Bidding service |

Direct ride acceptance is invalid for `BID_BASED` and `HYBRID`.

---

## Create Ride

Route:

```text
POST /api/v1/rides
```

Schema:

```python
class CreateRideRequest(BaseModel):
    service_type: ServiceType
    category: ServiceCategory
    pricing_mode: PricingMode = PricingMode.FIXED
    stops: list[StopInput] = Field(..., min_length=2)
    detail: ServiceDetailInput
    baseline_min_price: float | None = Field(None, ge=0)
    baseline_max_price: float | None = Field(None, ge=0)
    scheduled_at: datetime | None = None
    auto_accept_driver: bool = True
```

Validation:

- At least one `PICKUP` stop is required.
- At least one `DROPOFF` stop is required.
- Stop `sequence_order` values must be unique.
- `detail.service_type` must match top-level `service_type`.
- `baseline_min_price` must not exceed `baseline_max_price`.

Flow:

1. Authenticated passenger calls the route.
2. `ServiceRequest.create()` builds a new domain object.
3. Stops are sorted by `sequence_order` and converted to domain `Stop` objects.
4. Service-type detail payload is stored in the matching detail table.
5. `repo.create_full()` persists request, stops, and detail atomically.
6. Use case calls `ride.begin_matching()`, so newly created rides enter `MATCHING`.
7. Ride snapshot is cached in Redis for 30 minutes.
8. `service.request.created` is published to the `ride-events` topic.
9. Passenger WebSocket receives `RIDE_CREATED`.
10. Response returns full `RideResponse`.

Kafka payload:

```json
{
  "ride_id": "UUID",
  "passenger_id": "UUID",
  "passenger_user_id": "UUID",
  "service_type": "CITY_RIDE",
  "category": "MINI",
  "pricing_mode": "FIXED|BID_BASED|HYBRID",
  "baseline_min_price": 400.0,
  "baseline_max_price": 600.0,
  "auto_accept_driver": true,
  "pickup_latitude": 31.52,
  "pickup_longitude": 74.35,
  "dropoff_latitude": 31.60,
  "dropoff_longitude": 74.40,
  "vehicle_type": "SEDAN",
  "matching_radius_km": 5.0
}
```

WebSocket payload:

```json
{
  "event": "RIDE_CREATED",
  "data": {
    "ride_id": "UUID",
    "status": "MATCHING"
  }
}
```

---

## List Passenger Rides

Route:

```text
GET /api/v1/rides?status=MATCHING&status=ACCEPTED&limit=20&offset=0
```

Flow:

1. Authenticated passenger is resolved through `CurrentUser`.
2. Repository fetches only rides owned by `current_user.user_id`.
3. Optional repeated `status` query filters by one or more statuses.
4. Response returns lightweight `RideSummaryResponse` list.

---

## Get Ride

Route:

```text
GET /api/v1/rides/{ride_id}
```

Flow:

1. Ride is loaded by ID.
2. Full related data is included: stops, proofs, verification codes, pickup/dropoff convenience fields.
3. Ride snapshot is refreshed in Redis.
4. Response returns `RideResponse`.

Current route does not enforce participant ownership in the router. Access policy should be reviewed before exposing this endpoint beyond trusted clients.

---

## Cancel Ride

Route:

```text
POST /api/v1/rides/{ride_id}/cancel
```

Schema:

```python
class CancelRideRequest(BaseModel):
    reason: str | None = Field(None, max_length=500)
```

Flow:

1. Ride is loaded by ID.
2. Caller must be the passenger who created the ride.
3. Domain transition sets status to `CANCELLED`.
4. Cancel metadata is persisted.
5. Redis ride cache is deleted.
6. `service.request.cancelled` is published.
7. Passenger receives `RIDE_CANCELLED`.
8. Assigned driver, if any, receives `JOB_CANCELLED`.

Kafka payload:

```json
{
  "ride_id": "UUID",
  "passenger_user_id": "UUID",
  "assigned_driver_id": "UUID | null",
  "driver_id": "UUID | null",
  "reason": "string | null"
}
```

---

## Accept Fixed-Price Ride

Route:

```text
POST /api/v1/rides/{ride_id}/accept
```

Schema:

```python
class AcceptRideRequest(BaseModel):
    pass
```

Flow:

1. `CurrentDriver` resolves the acting verification `driver_id`.
2. Ride is loaded by ID.
3. Ride must use `PricingMode.FIXED`.
4. Ride must be in a valid state for acceptance, normally `MATCHING`.
5. Driver is assigned and status becomes `ACCEPTED`.
6. Redis ride cache is updated.
7. `service.request.accepted` is published.
8. Passenger receives `DRIVER_ASSIGNED`.
9. Driver receives `JOB_ASSIGNED`.

Kafka payload:

```json
{
  "ride_id": "UUID",
  "passenger_user_id": "UUID",
  "driver_id": "UUID",
  "pricing_mode": "FIXED",
  "final_price": null
}
```

Invalid pricing mode response:

```text
Direct accept not allowed for BID_BASED/HYBRID pricing. Use the Bidding Service instead.
```

---

## Bidding-Based Assignment

For `BID_BASED` and `HYBRID`, final assignment is driven by the Bidding service. The Ride service consumes accepted bid events and calls the internal assignment use case.

Flow:

1. Ride is created and enters `MATCHING`.
2. Bidding service creates a session for non-FIXED pricing modes.
3. Drivers bid or accept counters.
4. Bidding service publishes `BID_ACCEPTED`.
5. Ride Kafka consumer calls `InternalAssignDriverUseCase`.
6. Ride becomes `ACCEPTED`.
7. `service.request.accepted` is published with `passenger_user_id`.
8. Location and communication services use the accepted event to start ride tracking/conversation setup.

Internal accepted event emitted by Ride after assignment:

```json
{
  "ride_id": "UUID",
  "driver_id": "UUID",
  "passenger_user_id": "UUID",
  "pricing_mode": "BID_BASED|HYBRID",
  "final_price": 450.0
}
```

---

## Start Ride

Route:

```text
POST /api/v1/rides/{ride_id}/start
```

Schema:

```python
class VerifyAndStartRequest(BaseModel):
    verification_code: str | None = Field(None, min_length=4, max_length=10)
```

Flow:

1. `CurrentDriver` resolves acting driver.
2. Ride must exist and be assigned to that driver.
3. If ride requires start OTP, `verification_code` must be provided.
4. Active ride verification code is loaded and verified with `driver_id`.
5. Ride starts and transitions according to domain state machine.
6. Ride cache is updated.
7. `service.request.started` is published.
8. Passenger receives `RIDE_STARTED`.

Kafka payload:

```json
{
  "ride_id": "UUID"
}
```

---

## Complete Ride

Route:

```text
POST /api/v1/rides/{ride_id}/complete
```

Schema:

```python
class VerifyAndCompleteRequest(BaseModel):
    verification_code: str | None = Field(None, min_length=4, max_length=10)
    final_price: float | None = Field(None, ge=0)
```

Flow:

1. `CurrentDriver` resolves acting driver.
2. Ride must exist and be assigned to that driver.
3. If ride requires end OTP, `verification_code` must be provided.
4. Active ride verification code is verified with `driver_id`.
5. Ride transitions to `COMPLETED`.
6. Completion timestamp and final price are persisted.
7. Ride cache is deleted.
8. `service.request.completed` is published.
9. Passenger receives `RIDE_COMPLETED`.

Kafka payload:

```json
{
  "ride_id": "UUID",
  "passenger_user_id": "UUID",
  "assigned_driver_id": "UUID",
  "driver_id": "UUID",
  "final_price": 450.0
}
```

---

## Stops

### Add Stop

Route:

```text
POST /api/v1/rides/{ride_id}/stops
```

Schema:

```python
class AddStopRequest(BaseModel):
    sequence_order: int = Field(..., ge=1)
    stop_type: StopType
    latitude: float
    longitude: float
    place_name: str | None = None
    address_line_1: str | None = None
    city: str | None = None
    country: str | None = None
    contact_name: str | None = None
    contact_phone: str | None = None
    instructions: str | None = None
```

Flow:

1. Ride is loaded.
2. Ride must be active.
3. Stop is created and persisted.
4. Passenger receives `STOP_UPDATED` with `action="added"`.

Current route delegates directly to use case and does not pass `CurrentUser`; access policy should be reviewed before public exposure.

### Mark Stop Arrived

Route:

```text
POST /api/v1/stops/{stop_id}/arrived
```

Flow:

1. `CurrentDriver` resolves driver.
2. Stop and ride are loaded.
3. Driver must be the assigned ride driver.
4. Stop `arrived_at` is set.
5. If ride was `ACCEPTED`, it transitions to `ARRIVING`.
6. `service.stop.arrived` is published.
7. Passenger receives `STOP_UPDATED` with `action="arrived"`.

### Mark Stop Completed

Route:

```text
POST /api/v1/stops/{stop_id}/completed
```

Flow:

1. `CurrentDriver` resolves driver.
2. Stop and ride are loaded.
3. Driver must be assigned to the ride.
4. Stop must have arrived first.
5. Stop `completed_at` is set.
6. `service.stop.completed` is published.
7. Passenger receives `STOP_UPDATED` with `action="completed"`.

---

## Ride Verification Codes

### Generate Code

Route:

```text
POST /api/v1/rides/{ride_id}/verification-codes
```

Schema:

```python
class GenerateVerificationCodeRequest(BaseModel):
    stop_id: UUID | None = None
    expires_in_minutes: int = Field(default=15, ge=1, le=60)
    max_attempts: int = Field(default=5, ge=1, le=10)
    length: int = Field(default=6, ge=4, le=8)
```

Flow:

1. Ride must exist.
2. Numeric code is generated.
3. Code is persisted with expiry and max attempts.
4. `service.verification.generated` is published.
5. Response excludes raw code value.

### Verify Code

Route:

```text
POST /api/v1/rides/{ride_id}/verification-codes/verify
```

Schema:

```python
class VerifyCodeRequest(BaseModel):
    code: str = Field(..., min_length=4, max_length=10)
    user_id: UUID | None = None
    driver_id: UUID | None = None
```

Validation:

- Exactly one of `user_id` or `driver_id` must be provided.

Flow:

1. Ride must exist.
2. Active code is loaded.
3. Code validates expiry, attempts, replay, and value.
4. Verification metadata is persisted.
5. `service.verification.verified` is published.

---

## Proof Uploads

Proof upload is a three-step flow:

```text
POST /rides/{ride_id}/proofs/upload-url
PUT <presigned_url> directly to S3
POST /rides/{ride_id}/proofs
```

### Generate Upload URL

Route:

```text
POST /api/v1/rides/{ride_id}/proofs/upload-url
```

Schema:

```python
class ProofUploadUrlRequest(BaseModel):
    proof_type: ProofType
    file_name: str | None = None
    mime_type: str = "image/jpeg"
    stop_id: UUID | None = None
```

Identity behavior:

- If caller has a driver profile, router passes resolved `driver_id`.
- Otherwise router passes auth `current_user.user_id`.
- Use case compares that actor against `ride.assigned_driver_id` or `ride.passenger_id`.

Flow:

1. Ride is loaded.
2. Caller must be passenger or assigned driver.
3. S3 key is generated with `build_proof_key`.
4. Presigned PUT URL is generated for the requested MIME type.
5. URL and `file_key` are returned.

### Register Proof Metadata

Route:

```text
POST /api/v1/rides/{ride_id}/proofs
```

Schema:

```python
class UploadProofRequest(BaseModel):
    proof_type: ProofType
    file_key: str
    file_name: str | None = None
    mime_type: str | None = None
    file_size_bytes: int | None = None
    checksum_sha256: str | None = None
    is_primary: bool = False
    stop_id: UUID | None = None
```

Identity behavior:

- Clients cannot supply uploader IDs.
- Passenger uploader is set from auth `user_id`.
- Driver uploader is set from resolved verification `driver_id`.

Flow:

1. Ride is loaded.
2. Caller must be ride passenger or assigned driver.
3. Proof metadata is persisted.
4. `service.proof.uploaded` is published.
5. Response returns proof record.

### Get Proof URL

Route:

```text
GET /api/v1/rides/{ride_id}/proofs/{proof_id}/url
```

Flow:

1. Proof is found among ride proofs.
2. Caller must be the original uploader.
3. S3 presigned GET URL is generated.
4. Response returns proof metadata plus `view_url`.

---

## Nearby Drivers

Route:

```text
GET /api/v1/drivers/nearby?lat=31.52&lng=74.35&radius=5&ride_id=<optional>
```

Flow:

1. Query parameters are validated.
2. Ride service calls Geospatial service through `GeospatialClient`.
3. Candidates may be cached by `ride_id`.
4. `driver.matching.requested` is published.
5. Response returns ranked candidates.

Response:

```json
{
  "ride_id": "UUID | null",
  "candidates": [
    {
      "driver_id": "UUID",
      "distance_km": 1.2,
      "vehicle_type": "SEDAN",
      "rating": 4.8,
      "priority_score": 0.91,
      "estimated_arrival_minutes": 6.0
    }
  ],
  "count": 1
}
```

---

## WebSocket Endpoints

### Driver Channel

Route:

```text
WS /api/v1/ws/drivers?token=<JWT>
```

Auth:

- `get_current_driver_ws` verifies token and resolves verification `driver_id`.

Flow:

1. Socket is accepted and registered under `driver_id`.
2. Client may send text `"ping"`.
3. Server replies with `{"event":"pong"}`.
4. Driver receives job events such as `NEW_JOB`, `JOB_ASSIGNED`, `JOB_CANCELLED`, `JOB_UPDATED`.

### Passenger Channel

Route:

```text
WS /api/v1/ws/passengers?token=<JWT>&ride_id=<optional>
```

Auth:

- Token is verified with `get_current_user_ws`.
- Role must be `passenger`.

Flow:

1. Socket is accepted and registered under auth `user_id`.
2. If `ride_id` is provided, socket subscribes to that ride.
3. Client may send text `"ping"`.
4. Server replies with `{"event":"pong"}`.

---

## Domain Models

### ServiceRequest

```python
class ServiceRequest:
    id: UUID
    passenger_id: UUID
    assigned_driver_id: UUID | None
    service_type: ServiceType
    category: ServiceCategory
    pricing_mode: PricingMode
    status: RideStatus
    baseline_min_price: float | None
    baseline_max_price: float | None
    final_price: float | None
    auto_accept_driver: bool
    scheduled_at: datetime | None
    accepted_at: datetime | None
    completed_at: datetime | None
    cancelled_at: datetime | None
```

### Stop

```python
class Stop:
    id: UUID
    service_request_id: UUID
    sequence_order: int
    stop_type: StopType
    latitude: float
    longitude: float
    arrived_at: datetime | None
    completed_at: datetime | None
```

### ProofImage

```python
class ProofImage:
    id: UUID
    service_request_id: UUID
    stop_id: UUID | None
    proof_type: ProofType
    file_key: str
    uploaded_by_user_id: UUID | None
    uploaded_by_driver_id: UUID | None
```

### VerificationCode

```python
class VerificationCode:
    id: UUID
    service_request_id: UUID
    stop_id: UUID | None
    code: str
    attempts: int
    max_attempts: int
    expires_at: datetime | None
    verified_at: datetime | None
```

---

## Ride Status Transitions

```python
CREATED -> MATCHING -> ACCEPTED -> ARRIVING -> IN_PROGRESS -> COMPLETED
CREATED -> CANCELLED
MATCHING -> CANCELLED
ACCEPTED -> CANCELLED
ARRIVING -> CANCELLED
IN_PROGRESS -> CANCELLED
```

---

## Routes Summary

| Method | URL | Description |
|---|---|---|
| POST | `/api/v1/rides` | Create ride in FIXED, BID_BASED, or HYBRID mode |
| GET | `/api/v1/rides` | List current passenger rides |
| GET | `/api/v1/rides/{ride_id}` | Get ride detail |
| POST | `/api/v1/rides/{ride_id}/cancel` | Passenger cancels ride |
| POST | `/api/v1/rides/{ride_id}/accept` | Driver accepts FIXED ride |
| POST | `/api/v1/rides/{ride_id}/start` | Assigned driver starts ride |
| POST | `/api/v1/rides/{ride_id}/complete` | Assigned driver completes ride |
| POST | `/api/v1/rides/{ride_id}/stops` | Add stop |
| POST | `/api/v1/stops/{stop_id}/arrived` | Assigned driver marks stop arrived |
| POST | `/api/v1/stops/{stop_id}/completed` | Assigned driver marks stop completed |
| POST | `/api/v1/rides/{ride_id}/verification-codes` | Generate ride OTP |
| POST | `/api/v1/rides/{ride_id}/verification-codes/verify` | Verify ride OTP |
| POST | `/api/v1/rides/{ride_id}/proofs/upload-url` | Generate proof presigned PUT URL |
| POST | `/api/v1/rides/{ride_id}/proofs` | Register proof metadata |
| GET | `/api/v1/rides/{ride_id}/proofs/{proof_id}/url` | Get proof presigned GET URL |
| GET | `/api/v1/drivers/nearby` | Find nearby driver candidates |
| WS | `/api/v1/ws/drivers` | Driver real-time ride channel |
| WS | `/api/v1/ws/passengers` | Passenger real-time ride channel |

---

## Infrastructure Components

### Repositories

`ServiceRequestRepository`, `StopRepository`, `ProofImageRepository`, and `VerificationCodeRepository` map the `service_request` schema to pure domain objects.

### WebSocketManager

Tracks in-memory driver/passenger sockets and ride subscriptions. It sends targeted driver and passenger events without persistence.

### GeospatialClient

HTTP adapter for driver matching. A null implementation is used when the geospatial service URL is absent.

### S3StorageProvider

Generates presigned PUT/GET URLs for proof images. The Ride service never receives binary proof payloads.

### Kafka Publisher And Consumer

Publishes ride lifecycle events to `ride-events` and consumes downstream events, including bidding assignment events, when Kafka is configured.

---

## See Also

- `services/ride/ride/api/router.py`
- `services/ride/ride/application/use_cases.py`
- `services/ride/ride/application/schemas.py`
- `services/bidding/bidding/application/use_cases.py`
- `services/location/location/application/use_cases.py`
