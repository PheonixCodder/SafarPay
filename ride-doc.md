# Ride

## Ride Creation
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

Routes to be used:
```
1. POST /rides
```

Flow:

1. **Map Request to ServiceRequest**: Map all fields from CreateRideRequest to the ServiceRequest domain model.
2. **Create Ride**: Instantiate a new ServiceRequest aggregate via `ServiceRequest.create()` and save it.
3. **Map Stops**: Convert StopInput objects to Stop domain objects and persist.
4. **Map Detail**: Convert the detail field (service-type-specific) to the appropriate detail model (CityRideDetail, IntercityDetail, FreightDetail, CourierDetail, or GroceryDetail) and persist.
5. **Transaction**: Insert ServiceRequest and Stop models in a single database transaction via `repo.create_full()`.
6. **Cache**: Store ride's id, passenger_id, assigned_driver_id, and service_type in Redis with 30-minute TTL.
7. **Extract Stops**: Identify PICKUP and DROPOFF stops from the detail model for geospatial matching.
8. **Kafka - ServiceRequestCreatedEvent**: Publish to topic `service.request.created` with ride details and pickup/dropoff coordinates for driver matching:

    ```json
    {
        "ride_id": "UUID",
        "passenger_id": "UUID",
        "service_type": "CITY_RIDE|INTERCITY|FREIGHT|COURIER|GROCERY",
        "category": "MINI|RICKSHAW|RIDE_AC|...",
        "pickup_latitude": float,
        "pickup_longitude": float,
        "dropoff_latitude": float | null,
        "dropoff_longitude": float | null,
        "vehicle_type": "SEDAN|HATCHBACK|...",
        "matching_radius_km": 5.0
    }
    ```

9. **WebSocket - RIDE_CREATED**: Broadcast `RIDE_CREATED` event to passenger via `/ws/passengers` with payload:

    ```json
    {
        "ride_id": "UUID",
        "status": "CREATED"
    }
    ```

10. **Response**: Return RideResponse to passenger. Ride is now in MATCHING state and ready for driver assignment (FIXED mode) or bidding (BID_BASED/HYBRID).

Kafka Event payloads:
```json
ServiceRequestCreatedEvent:
    {
        "ride_id": "UUID",
        "passenger_id": "UUID",
        "service_type": "CITY_RIDE|INTERCITY|FREIGHT|COURIER|GROCERY",
        "category": "MINI|RICKSHAW|RIDE_AC|PREMIUM|BIKE|COMFORT|SHARE|PRIVATE",
        "pickup_latitude": float,
        "pickup_longitude": float,
        "dropoff_latitude": float,
        "dropoff_longitude": float,
        "vehicle_type": str,
        "matching_radius_km": 5.0
    }
```

Websocket payloads:
```json
RIDE_CREATED:
    {
        "ride_id": "UUID",
        "status": "CREATED"
    }
```

## Get All Rides (Passenger)
```python
class GetRidesRequest(QueryParams):
    status: RideStatus
    offset: int
    limit: int
```

Routes to be used:
```
1. GET /rides?status=CREATED&limit=20&offset=0
```

Flow:

1. **Query Repository**: Fetch rides for the passenger from the repository filtered by status (optional), limit, and offset.
2. **Convert to Summary**: Map each ServiceRequest to RideSummaryResponse (excludes detailed stops, proofs, verification codes).
3. **Return**: List of ride summaries to passenger.

No Kafka events (read-only operation).

No WebSocket events (read-only operation).

Response includes:
- List of ride summaries with id, passenger_id, assigned_driver_id, service_type, category, status, created_at, scheduled_at
- Pickup and dropoff stop summaries

## Get Single Ride
```python
class GetRidesRequest:
    ride_id: UUID
```

Routes to be used:
```
1. GET /rides/{ride_id}
```

Flow:

1. **Fetch Ride**: Retrieve the ride by ID from repository; raise 404 if not found.
2. **Cache**: Store ride's id, status, passenger_id, assigned_driver_id, and service_type in Redis with 30-minute TTL.
3. **Convert to Response**: Map ServiceRequest to RideResponse including full stops, proof_images, and verification_codes lists.
4. **Return**: Complete ride details to caller.

## Cancel Ride
```python
class CancelRideRequest(BaseModel):
    reason: str | None = Field(None, max_length=500)
```

Routes to be used:
```
1. POST /rides/{ride_id}/cancel
```

Flow:

1. **Fetch Ride**: Retrieve ride by ID; ensure the requesting user is the passenger who created the ride.
2. **Cancel**: Call `ride.cancel(reason)` to transition status to CANCELLED and record timestamps.
3. **Persist**: Update ride status, cancelled_at, and cancellation_reason in database.
4. **Delete Cache**: Remove ride from Redis cache.
5. **Kafka - ServiceRequestCancelledEvent**: Publish to topic `service.request.cancelled`:

    ```json
    {
        "ride_id": "UUID",
        "reason": "string"
    }
    ```

6. **WebSocket - RIDE_CANCELLED**: Broadcast to passenger:

    ```json
    {
        "ride_id": "UUID",
        "reason": "string"
    }
    ```

7. **WebSocket - JOB_CANCELLED**: If ride has an assigned driver, broadcast to driver to notify job cancellation:

    ```json
    {
        "ride_id": "UUID"
    }
    ```

Kafka Event payloads:
```json
ServiceRequestCancelledEvent:
    {
        "ride_id": "UUID",
        "reason": "string"
    }
```

Websocket payloads:
```json
RIDE_CANCELLED:
    {
        "ride_id": "UUID",
        "reason": "string"
    }
```

```json
JOB_CANCELLED:
    {
        "ride_id": "UUID"
    }
```

## Accept Ride (Fixed Price)
```python
class AcceptRideRequest(BaseModel):
    """No driver_id — the acting driver is derived from the authenticated JWT principal."""
```

Routes to be used:
```
1. POST /rides/{ride_id}/accept
```

Flow:

1. **Fetch Ride**: Retrieve ride by ID.
2. **Validate Pricing Mode**: Ensure ride.pricing_mode is FIXED. Reject BID_BASED and HYBRID (these use the Bidding Service).
3. **Validate State**: Ensure ride can transition from MATCHING to ACCEPTED.
4. **Assign Driver**: Call `ride.accept(driver_id)` to assign driver and update accepted_at timestamp.
5. **Persist**: Update ride status, accepted_at, and assigned_driver_id in database.
6. **Cache**: Update ride in Redis cache.
7. **Kafka - ServiceRequestAcceptedEvent**: Publish to topic `service.request.accepted`:

    ```json
    {
        "ride_id": "UUID",
        "driver_id": "UUID"
    }
    ```

8. **WebSocket - DRIVER_ASSIGNED**: Broadcast to passenger:

    ```json
    {
        "ride_id": "UUID",
        "driver_id": "UUID"
    }
    ```

9. **WebSocket - JOB_ASSIGNED**: Broadcast to assigned driver:

    ```json
    {
        "ride_id": "UUID"
    }
    ```

Kafka Event payloads:
```json
ServiceRequestAcceptedEvent:
    {
        "ride_id": "UUID",
        "driver_id": "UUID"
    }
```

Websocket payloads:
```json
DRIVER_ASSIGNED:
    {
        "ride_id": "UUID",
        "driver_id": "UUID"
    }
```

```json
JOB_ASSIGNED:
    {
        "ride_id": "UUID"
    }
```

## Start Ride
```python
class VerifyAndStartRequest(BaseModel):
    """Optional OTP code submitted at ride start."""
    verification_code: str | None = Field(None, min_length=4, max_length=10)
```

Routes to be used:
```
1. POST /rides/{ride_id}/start
```

Flow:

1. **Fetch Ride**: Retrieve ride by ID.
2. **Authorize Driver**: Ensure caller is the assigned driver.
3. **Verify OTP (if required)**: If ride.requires_otp_start, verify the code against the active VerificationCode for this ride:
   - Find active code from repository
   - Call `code.verify(submitted_code, driver_id=driver_id)` which checks expiry, attempts, and code match
   - Persist updated code with verified_at and verified_by_driver_id
4. **Start**: Call `ride.start()` to transition from ACCEPTED to ARRIVING.
5. **Persist**: Update ride status in database.
6. **Cache**: Update ride in Redis.
7. **Kafka - ServiceRequestStartedEvent**: Publish to topic `service.request.started`:

    ```json
    {
        "ride_id": "UUID"
    }
    ```

8. **WebSocket - RIDE_STARTED**: Broadcast to passenger:

    ```json
    {
        "ride_id": "UUID"
    }
    ```

Kafka Event payloads:
```json
ServiceRequestStartedEvent:
    {
        "ride_id": "UUID"
    }
```

Websocket payloads:
```json
RIDE_STARTED:
    {
        "ride_id": "UUID"
    }
```

## Complete Ride
```python
class VerifyAndCompleteRequest(BaseModel):
    """Optional OTP code submitted at ride completion.

    No driver_id — the acting driver is derived from the authenticated JWT principal.
    """
    verification_code: str | None = Field(None, min_length=4, max_length=10)
    final_price: float | None = Field(None, ge=0)
```

Routes to be used:
```
1. POST /rides/{ride_id}/complete
```

Flow:

1. **Fetch Ride**: Retrieve ride by ID.
2. **Authorize Driver**: Ensure caller is the assigned driver.
3. **Verify OTP (if required)**: If ride.requires_otp_end, verify the code against active VerificationCode:
   - Find active code from repository
   - Call `code.verify(submitted_code, driver_id=driver_id)`
   - Persist updated code
4. **Complete**: Call `ride.complete()` to transition to COMPLETED and set completed_at.
5. **Persist**: Update ride status, completed_at, and final_price in database.
6. **Delete Cache**: Remove ride from Redis cache.
7. **Kafka - ServiceRequestCompletedEvent**: Publish to topic `service.request.completed`:

    ```json
    {
        "ride_id": "UUID",
        "final_price": float
    }
    ```

8. **WebSocket - RIDE_COMPLETED**: Broadcast to passenger:

    ```json
    {
        "ride_id": "UUID",
        "final_price": float
    }
    ```

Kafka Event payloads:
```json
ServiceRequestCompletedEvent:
    {
        "ride_id": "UUID",
        "final_price": float
    }
```

Websocket payloads:
```json
RIDE_COMPLETED:
    {
        "ride_id": "UUID",
        "final_price": float
    }
```

## Create Stop
```python
class AddStopRequest(BaseModel):
    sequence_order: int = Field(..., ge=1)
    stop_type: StopType
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    place_name: str | None = Field(None, max_length=255)
    address_line_1: str | None = Field(None, max_length=255)
    city: str | None = Field(None, max_length=120)
    country: str | None = Field(None, max_length=120)
    contact_name: str | None = Field(None, max_length=255)
    contact_phone: str | None = Field(None, max_length=30)
    instructions: str | None = None
```

Routes to be used:
```
1. POST /rides/{ride_id}/stops
```

Flow:

1. **Fetch Ride**: Retrieve ride by ID; ensure ride is still active (not COMPLETED/CANCELLED).
2. **Create Stop**: Instantiate Stop via `Stop.create()` with sequence_order, stop_type, coordinates, and optional metadata.
3. **Persist**: Save stop via StopRepository.
4. **WebSocket - STOP_UPDATED**: Broadcast to passenger:

    ```json
    {
        "ride_id": "UUID",
        "stop_id": "UUID",
        "action": "added"
    }
    ```

5. **Return**: StopResponse with full stop details.

Websocket payloads:
```json
STOP_UPDATED:
    {
        "ride_id": "UUID",
        "stop_id": "UUID",
        "action": "added"
    }
```

## Arrived at Stop
```python
# No request body - stop_id is URL path parameter
```

Routes to be used:
```
1. POST /stops/{stop_id}/arrived
```

Flow:

1. **Fetch Stop**: Retrieve stop by ID; raise 404 if not found.
2. **Fetch Ride**: Retrieve ride by stop.service_request_id.
3. **Authorize Driver**: Ensure caller is the assigned driver for this ride.
4. **Mark Arrived**: Call `stop.mark_arrived()` which sets arrived_at to current UTC time (fails if stop already completed).
5. **Update Ride State**: If ride status is ACCEPTED, transition to ARRIVING via `ride.driver_arriving()`.
6. **Persist**: Update stop.arrived_at in database; update ride status if changed.
7. **Kafka - ServiceStopArrivedEvent**: Publish to topic `service.stop.arrived`:

    ```json
    {
        "ride_id": "UUID",
        "stop_id": "UUID"
    }
    ```

8. **WebSocket - STOP_UPDATED**: Broadcast to passenger:

    ```json
    {
        "ride_id": "UUID",
        "stop_id": "UUID",
        "action": "arrived"
    }
    ```

Kafka Event payloads:
```json
ServiceStopArrivedEvent:
    {
        "ride_id": "UUID",
        "stop_id": "UUID"
    }
```

Websocket payloads:
```json
STOP_UPDATED:
    {
        "ride_id": "UUID",
        "stop_id": "UUID",
        "action": "arrived"
    }
```

## Stop Completed
```python
# No request body - stop_id is URL path parameter
```

Routes to be used:
```
1. POST /stops/{stop_id}/completed
```

Flow:

1. **Fetch Stop**: Retrieve stop by ID; raise 404 if not found.
2. **Fetch Ride**: Retrieve ride by stop.service_request_id.
3. **Authorize Driver**: Ensure caller is the assigned driver.
4. **Mark Completed**: Call `stop.mark_completed()` which sets completed_at to current UTC time (requires arrived_at to be set first).
5. **Persist**: Update stop.completed_at in database.
6. **Kafka - ServiceStopCompletedEvent**: Publish to topic `service.stop.completed`:

    ```json
    {
        "ride_id": "UUID",
        "stop_id": "UUID"
    }
    ```

7. **WebSocket - STOP_UPDATED**: Broadcast to passenger:

    ```json
    {
        "ride_id": "UUID",
        "stop_id": "UUID",
        "action": "completed"
    }
    ```

Kafka Event payloads:
```json
ServiceStopCompletedEvent:
    {
        "ride_id": "UUID",
        "stop_id": "UUID"
    }
```

Websocket payloads:
```json
STOP_UPDATED:
    {
        "ride_id": "UUID",
        "stop_id": "UUID",
        "action": "completed"
    }
```

## Generate Verification Code
```python
class GenerateVerificationCodeRequest(BaseModel):
    stop_id: UUID | None = None
    expires_in_minutes: int = Field(default=15, ge=1, le=60)
    max_attempts: int = Field(default=5, ge=1, le=10)
    length: int = Field(default=6, ge=4, le=8)
```

Routes to be used:
```
1. POST /rides/{ride_id}/verification-codes
```

Flow:

1. **Fetch Ride**: Verify ride exists; raise 404 if not.
2. **Generate Code**: Create VerificationCode via `VerificationCode.generate()` which produces a cryptographically random numeric code with specified length, max_attempts, expiry, and optional stop_id.
3. **Persist**: Save code via VerificationCodeRepository.
4. **Kafka - ServiceVerificationGeneratedEvent**: Publish to topic `service.verification.generated`:

    ```json
    {
        "ride_id": "UUID",
        "code_id": "UUID"
    }
    ```

5. **Return**: VerificationCodeResponse (excludes the actual code value for security — code is delivered out-of-band e.g., SMS).

Kafka Event payloads:
```json
ServiceVerificationGeneratedEvent:
    {
        "ride_id": "UUID",
        "code_id": "UUID"
    }
```

## Verify Verification Code
```python
class VerifyCodeRequest(BaseModel):
    code: str = Field(..., min_length=4, max_length=10)
    user_id: UUID | None = None
    driver_id: UUID | None = None
```

Routes to be used:
```
1. POST /rides/{ride_id}/verification-codes/verify
```

Flow:

1. **Fetch Ride**: Verify ride exists.
2. **Find Active Code**: Retrieve the active verification code for this ride.
3. **Verify**: Call `code.verify(submitted_code, user_id=user_id, driver_id=driver_id)` which validates:
   - Exactly one of user_id or driver_id is provided
   - Code is not already verified
   - Code has not expired
   - Attempts remaining (>0)
   - Code matches (constant-time comparison)
4. **Persist**: Update code with is_verified=True, verified_at, and verified_by_* fields.
5. **Kafka - ServiceVerificationVerifiedEvent**: Publish to topic `service.verification.verified`:

    ```json
    {
        "ride_id": "UUID",
        "code_id": "UUID"
    }
    ```

Kafka Event payloads:
```json
ServiceVerificationVerifiedEvent:
    {
        "ride_id": "UUID",
        "code_id": "UUID"
    }
```

## Generate Upload Proof URL
```python
class ProofUploadUrlRequest(BaseModel):
    proof_type: ProofType
    file_name: str | None = Field(None, max_length=255, description="Original filename; used to derive the S3 key extension")
    mime_type: str = Field(
        default="image/jpeg",
        description="MIME type the client will upload with. Must match Content-Type in the PUT request.",
    )
    stop_id: UUID | None = Field(None, description="Associate the proof with a specific stop")
```

Routes to be used:
```
1. POST /rides/{ride_id}/proofs/upload-url
```

Flow:

1. **Fetch Ride**: Load ride details; raise 404 if not found.
2. **Authorize**: Verify actor (user or driver) is either the ride passenger or the assigned driver.
3. **Build Key**: Generate unique storage key using `build_proof_key(ride_id, proof_type, file_name)`.
4. **Generate Presigned URL**: Create S3 PUT URL with specified content_type and 15-minute expiry.
5. **Log**: Record generation event.
6. **Return**: ProofUploadUrlResponse with presigned_url, file_key, expires_in_seconds, proof_type, and mime_type.

Response includes:
```json
{
    "presigned_url": "https://...",
    "file_key": "proofs/{ride_id}/{proof_type}/{filename}",
    "expires_in_seconds": 900,
    "proof_type": "PICKUP|DROPOFF",
    "mime_type": "image/jpeg"
}
```

## Upload Proof Data
```python
class UploadProofRequest(BaseModel):
    proof_type: ProofType
    file_key: str = Field(..., max_length=500, description="S3 / object-storage key returned by the upload-url endpoint")
    file_name: str | None = Field(None, max_length=255)
    mime_type: str | None = Field(None, max_length=120)
    file_size_bytes: int | None = Field(None, ge=0)
    checksum_sha256: str | None = Field(None, max_length=64)
    is_primary: bool = False
    stop_id: UUID | None = None
```

Routes to be used:
```
1. POST /rides/{ride_id}/proofs
```

Flow:

1. **Fetch Ride**: Retrieve ride by ID; raise 404 if not exists.
2. **Authorize**: Ensure uploader (user or driver) is the passenger or assigned driver.
3. **Create Proof**: Instantiate ProofImage with validated uploader IDs (from JWT, NOT request body) and metadata.
4. **Persist**: Save proof via ProofRepository.
5. **Kafka - ServiceProofUploadedEvent**: Publish to topic `service.proof.uploaded`:

    ```json
    {
        "ride_id": "UUID",
        "proof_id": "UUID",
        "proof_type": "PICKUP|DROPOFF"
    }
    ```

6. **Return**: ProofImageResponse with proof details.

Kafka Event payloads:
```json
ServiceProofUploadedEvent:
    {
        "ride_id": "UUID",
        "proof_id": "UUID",
        "proof_type": "PICKUP|DROPOFF"
    }
```

## Get Proof URL
```python
# No request body - ride_id and proof_id are URL path parameters
```

Routes to be used:
```
1. GET /rides/{ride_id}/proofs/{proof_id}/url
```

Flow:

1. **Retrieve Proofs**: Fetch all proof records for the ride.
2. **Locate Proof**: Find specific proof by proof_id; raise 404 if not found.
3. **Authorize**: Verify actor (user or driver) is the original uploader.
4. **Generate Presigned GET URL**: Create time-limited S3 GET URL.
5. **Return**: ProofImageWithUrlResponse with proof metadata and view_url.

## Get Drivers Nearby
```python
# Query parameters (not a request body)
radius: float = Field(..., ge=0.1, le=100.0)
latitude: float = Field(..., ge=-90.0, le=90.0)
longitude: float = Field(..., ge=-180.0, le=180.0)
ride_id: UUID | None = None
```

Routes to be used:
```
1. GET /drivers/nearby?lat=...&lng=...&radius=...&ride_id=...
```

Flow:

1. **Search**: Query geospatial service for nearby drivers within radius, filtered by category, vehicle_type, fuel_types, and limit.
2. **Cache Candidates**: If ride_id provided, cache driver candidates (driver_id, distance_km, vehicle_type, priority_score) with 10-minute TTL.
3. **Kafka - DriverMatchingRequestedEvent**: Publish to message broker:

    ```json
    {
        "ride_id": "UUID | null",
        "candidate_count": int
    }
    ```

4. **Return**: NearbyDriversResponse with ride_id, candidate list (driver_id, distance_km, vehicle_type, rating, priority_score, estimated_arrival_minutes), and total count.

Kafka Event payloads:
```json
DriverMatchingRequestedEvent:
    {
        "ride_id": "UUID | null",
        "candidate_count": int
    }
```

Response includes:
```json
{
    "ride_id": "UUID | null",
    "count": int,
    "candidates": [
        {
            "driver_id": "UUID",
            "distance_km": float,
            "vehicle_type": str,
            "rating": float | null,
            "priority_score": float,
            "estimated_arrival_minutes": float | null
        }
    ]
}
```

## Drivers Websocket
```
1. WebSocket /ws/drivers?token=<JWT>
```

Flow:

1. **Authenticate**: Verify driver JWT and resolve driver_id.
2. **Register**: Add driver connection to WebSocketManager for real-time events (NEW_JOB, JOB_CANCELLED, JOB_ASSIGNED, JOB_UPDATED).
3. **Keep-alive Loop**: Monitor connection, respond to "ping" with '{"event":"pong"}'.
4. **Disconnect**: On WebSocketDisconnect, remove driver from manager and log.

Websocket payloads (received by driver):
```json
NEW_JOB:
    {
        "ride_id": "UUID",
        ...ride_payload
    }
```

```json
JOB_CANCELLED:
    {
        "ride_id": "UUID"
    }
```

```json
JOB_ASSIGNED:
    {
        "ride_id": "UUID"
    }
```

## Passengers Websocket
```
1. WebSocket /ws/passengers?token=<JWT>&ride_id=<optional>
```

Flow:

1. **Authenticate**: Verify passenger JWT; close connection with WS_1008_POLICY_VIOLATION if role is not "passenger".
2. **Register**: Add passenger connection to WebSocketManager.
3. **Subscribe (optional)**: If ride_id provided, subscribe to real-time updates for that specific ride.
4. **Keep-alive Loop**: Monitor connection, respond to "ping" with '{"event":"pong"}'.
5. **Disconnect**: Unsubscribe from ride (if subscribed) and remove from manager.

Websocket payloads (received by passenger):
```json
RIDE_UPDATED:
    {
        "ride_id": "UUID",
        ...ride_data
    }
```

```json
DRIVER_LOCATION:
    {
        "ride_id": "UUID",
        "latitude": float,
        "longitude": float
    }
```

```json
RIDE_CREATED:
    {
        "ride_id": "UUID",
        "status": "CREATED"
    }
```

```json
RIDE_CANCELLED:
    {
        "ride_id": "UUID",
        "reason": "string"
    }
```

```json
DRIVER_ASSIGNED:
    {
        "ride_id": "UUID",
        "driver_id": "UUID"
    }
```

```json
RIDE_STARTED:
    {
        "ride_id": "UUID"
    }
```

```json
RIDE_COMPLETED:
    {
        "ride_id": "UUID",
        "final_price": float
    }
```

```json
STOP_UPDATED:
    {
        "ride_id": "UUID",
        "stop_id": "UUID",
        "action": "added|arrived|completed"
    }
```

```json
JOB_CANCELLED:
    {
        "ride_id": "UUID"
    }
```

## Stop
```python
class Stop:
    """An ordered route point on a service request."""

    id: UUID
    service_request_id: UUID
    sequence_order: int
    stop_type: StopType
    latitude: float
    longitude: float

    place_name: str | None = None
    address_line_1: str | None = None
    address_line_2: str | None = None
    city: str | None = None
    state: str | None = None
    country: str | None = None
    postal_code: str | None = None

    contact_name: str | None = None
    contact_phone: str | None = None
    instructions: str | None = None

    arrived_at: datetime | None = None
    completed_at: datetime | None = None
```

## ProofImage
```python
class ProofImage:
    """
    Metadata for an uploaded proof-of-service image.

    Actual binary is stored in S3/object storage.  Only the key and
    metadata are persisted here.

    ORM fields:
        uploaded_by_user_id   — nullable FK → auth.users (passenger upload)
        uploaded_by_driver_id — nullable FK → verification.drivers (driver upload)
    Either may be set depending on who uploads; both may be null for
    system-generated proofs.
    """

    id: UUID
    service_request_id: UUID
    proof_type: ProofType
    file_key: str

    stop_id: UUID | None = None
    file_name: str | None = None
    mime_type: str | None = None
    file_size_bytes: int | None = None
    checksum_sha256: str | None = None
    is_primary: bool = False

    # Uploader identity — at most one should be set per record
    uploaded_by_user_id: UUID | None = None    # passenger
    uploaded_by_driver_id: UUID | None = None  # driver

    uploaded_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
```

## VerificationCode
```python
class VerificationCode:
    """
    OTP code used for ride handoff verification at start or completion.

    ORM fields:
        verified_by_user_id   — UUID (bare, no FK) — passenger verifier
        verified_by_driver_id — UUID (bare, no FK) — driver verifier
    The code can be verified from either side depending on the flow.
    """

    id: UUID
    service_request_id: UUID
    code: str

    stop_id: UUID | None = None
    is_verified: bool = False
    attempts: int = 0
    max_attempts: int = 5
    expires_at: datetime | None = None
    generated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    verified_at: datetime | None = None

    # Either user or driver will verify — track both separately
    verified_by_user_id: UUID | None = None
    verified_by_driver_id: UUID | None = None
```

## DriverCandidate
```python
class DriverCandidate:
    """A driver candidate returned from the geospatial / matching service."""

    driver_id: UUID
    latitude: float
    longitude: float
    distance_km: float
    vehicle_type: str
    rating: float | None = None
    priority_score: float = 0.0
    estimated_arrival_minutes: float | None = None
    composite_score: float = 0.0
    h3_cell: str | None = None
```

## ServiceRequest
```python
class ServiceRequest:
    """
    The aggregate root for a ride/service request lifecycle.

    Field mapping to ORM:
        passenger_id      → ServiceRequestORM.user_id           (NOT NULL, FK auth.users)
        assigned_driver_id → ServiceRequestORM.assigned_driver_id (nullable, FK verification.drivers)
    """

    id: UUID
    passenger_id: UUID           # maps to ORM.user_id
    service_type: ServiceType
    category: ServiceCategory
    pricing_mode: PricingMode
    status: RideStatus

    stops: list[Stop] = field(default_factory=list)
    proof_images: list[ProofImage] = field(default_factory=list)
    verification_codes: list[VerificationCode] = field(default_factory=list)

    assigned_driver_id: UUID | None = None   # maps to ORM.assigned_driver_id
    baseline_min_price: float | None = None
    baseline_max_price: float | None = None
    final_price: float | None = None

    scheduled_at: datetime | None = None
    is_scheduled: bool = False
    is_risky: bool = False
    auto_accept_driver: bool = True
    requires_otp_start: bool = False
    requires_otp_end: bool = False

    accepted_at: datetime | None = None
    completed_at: datetime | None = None
    cancelled_at: datetime | None = None
    cancellation_reason: str | None = None

    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
```

## CityRideDetail
```python
class CityRideDetail:
    service_request_id: UUID
    passenger_count: int = 1
    is_ac: bool = False
    preferred_vehicle_type: VehicleType | None = None
    driver_gender_preference: DriverGenderPreference = DriverGenderPreference.NO_PREFERENCE
    is_shared_ride: bool = False
    max_co_passengers: int | None = None
    allowed_fuel_types: list[FuelType] | None = None
    is_smoking_allowed: bool = False
    is_pet_allowed: bool = False
    requires_wheelchair_access: bool = False
    max_wait_time_minutes: int | None = None
    requires_otp_start: bool = True
    requires_otp_end: bool = True
    estimated_price: float | None = None
    surge_multiplier_applied: float | None = None
```

## IntercityDetail
```python
class IntercityDetail:
    service_request_id: UUID
    passenger_count: int
    luggage_count: int = 0
    child_count: int = 0
    senior_count: int = 0
    allowed_fuel_types: list[FuelType] | None = None
    preferred_departure_time: datetime | None = None
    departure_time_flexibility_minutes: int | None = None
    is_round_trip: bool = False
    return_time: datetime | None = None
    trip_distance_km: float | None = None
    estimated_duration_minutes: int | None = None
    route_polyline: str | None = None
    vehicle_type_requested: VehicleType | None = None
    min_vehicle_capacity: int | None = None
    requires_luggage_carrier: bool = False
    estimated_price: float | None = None
    price_per_km: float | None = None
    toll_estimate: float | None = None
    fuel_surcharge: float | None = None
    total_stops: int = 0  # operational cache
    is_multi_city_trip: bool = False
    requires_identity_verification: bool = False
    emergency_contact_name: str | None = None
    emergency_contact_number: str | None = None
    matching_priority_score: float | None = None
    demand_zone_id: str | None = None
    passenger_groups: list['IntercityPassengerGroup'] = field(default_factory=list)
```

## FreightDetail
```python
class FreightDetail:
    service_request_id: UUID
    cargo_weight: float
    cargo_type: str
    vehicle_type: VehicleType
    requires_loader: bool = False
    is_fragile: bool = False
    requires_temperature_control: bool = False
    declared_value: float | None = None
    commodity_notes: str | None = None
    estimated_load_hours: int | None = None
```

## CourierDetail
```python
class CourierDetail:
    service_request_id: UUID
    item_description: str
    recipient_name: str
    recipient_phone: str
    item_weight: float | None = None
    total_parcels: int = 1
    recipient_email: str | None = None
    is_fragile: bool = False
    requires_signature: bool = False
    declared_value: float | None = None
    special_handling_notes: str | None = None
```

## GroceryDetail
```python
class GroceryDetail:
    service_request_id: UUID
    store_id: UUID
    total_items: int = 0
    special_notes: str | None = None
    contactless_delivery: bool = False
    estimated_bag_count: int | None = None
```

## IntercityPassengerGroup
```python
class IntercityPassengerGroup:
    id: UUID
    intercity_service_request_id: UUID
    passenger_count: int
    luggage_count: int = 0
    full_name: str | None = None
    phone_number: str | None = None
    seat_preference: str | None = None
    special_needs: str | None = None
```

# Enums

## RideStatus
```python
class RideStatus(str, Enum):
    CREATED = "CREATED"
    MATCHING = "MATCHING"
    ACCEPTED = "ACCEPTED"
    ARRIVING = "ARRIVING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"
```

## ServiceType
```python
class ServiceType(str, Enum):
    CITY_RIDE = "CITY_RIDE"
    INTERCITY = "INTERCITY"
    FREIGHT = "FREIGHT"
    COURIER = "COURIER"
    GROCERY = "GROCERY"
```

## ServiceCategory
```python
class ServiceCategory(str, Enum):
    MINI = "MINI"
    RICKSHAW = "RICKSHAW"
    RIDE_AC = "RIDE_AC"
    PREMIUM = "PREMIUM"
    BIKE = "BIKE"
    COMFORT = "COMFORT"
    SHARE = "SHARE"
    PRIVATE = "PRIVATE"
```

## PricingMode
```python
class PricingMode(str, Enum):
    FIXED = "FIXED"
    BID_BASED = "BID_BASED"
    HYBRID = "HYBRID"
```

## StopType
```python
class StopType(str, Enum):
    PICKUP = "PICKUP"
    DROPOFF = "DROPOFF"
    WAYPOINT = "WAYPOINT"
```

## ProofType
```python
class ProofType(str, Enum):
    PICKUP = "PICKUP"
    DROPOFF = "DROPOFF"
```

## VehicleType
```python
class VehicleType(str, Enum):
    SEDAN = "SEDAN"
    HATCHBACK = "HATCHBACK"
    SUV = "SUV"
    VAN = "VAN"
    BIKE = "BIKE"
    RICKSHAW = "RICKSHAW"
    TRUCK = "TRUCK"
    PICKUP = "PICKUP"
    MINI_TRUCK = "MINI_TRUCK"
    COASTER = "COASTER"
    BUS = "BUS"
    OTHER = "OTHER"
```

## DriverGenderPreference
```python
class DriverGenderPreference(str, Enum):
    NO_PREFERENCE = "NO_PREFERENCE"
    MALE = "MALE"
    FEMALE = "FEMALE"
    ANY = "ANY"
```

## FuelType
```python
class FuelType(str, Enum):
    PETROL = "PETROL"
    DIESEL = "DIESEL"
    CNG = "CNG"
    HYBRID = "HYBRID"
    ELECTRIC = "ELECTRIC"
```


# Valid lifecycle transitions
```python
VALID_TRANSITIONS: dict[RideStatus, frozenset[RideStatus]] = {
    RideStatus.CREATED:     frozenset({RideStatus.MATCHING,     RideStatus.CANCELLED}),
    RideStatus.MATCHING:    frozenset({RideStatus.ACCEPTED,     RideStatus.CANCELLED}),
    RideStatus.ACCEPTED:    frozenset({RideStatus.ARRIVING,     RideStatus.CANCELLED}),
    RideStatus.ARRIVING:    frozenset({RideStatus.IN_PROGRESS,  RideStatus.CANCELLED}),
    RideStatus.IN_PROGRESS: frozenset({RideStatus.COMPLETED,    RideStatus.CANCELLED}),
    RideStatus.COMPLETED:   frozenset(),
    RideStatus.CANCELLED:   frozenset(),
}
```

# Routes Summary

### Ride Service Routes

| Method | URL | Description |
|--------|-----|-------------|
| POST | `/rides` | Create a new ride (FIXED, BID_BASED, or HYBRID pricing) |
| GET | `/rides` | Get all rides for current user |
| GET | `/rides/{ride_id}` | Get a specific ride by ID |
| POST | `/rides/{ride_id}/cancel` | Cancel a ride (passenger only) |
| POST | `/rides/{ride_id}/accept` | Accept a FIXED-price ride as driver |
| POST | `/rides/{ride_id}/start` | Start a ride (driver, requires OTP if enabled) |
| POST | `/rides/{ride_id}/complete` | Complete a ride (driver, requires OTP if enabled) |
| POST | `/rides/{ride_id}/stops` | Add a stop to an active ride |
| POST | `/stops/{stop_id}/arrived` | Mark stop as arrived (driver) |
| POST | `/stops/{stop_id}/completed` | Mark stop as completed (driver) |
| POST | `/rides/{ride_id}/verification-codes` | Generate verification code (OTP) |
| POST | `/rides/{ride_id}/verification-codes/verify` | Verify verification code |
| POST | `/rides/{ride_id}/proofs/upload-url` | Generate presigned S3 PUT URL for proof upload (step 1) |
| POST | `/rides/{ride_id}/proofs` | Register proof metadata after S3 upload (step 3) |
| GET | `/rides/{ride_id}/proofs/{proof_id}/url` | Get proof image record + presigned GET URL |
| GET | `/drivers/nearby` | Get nearby drivers for matching |
| WS | `/ws/drivers` | WebSocket endpoint for driver real-time updates |
| WS | `/ws/passengers` | WebSocket endpoint for passenger real-time updates |

---

# Infrastructure Components

## 1. ServiceRequest ORM Model

Core ride domain model extending `Base` with all ride attributes and relationships.

### Fields

- **Core**: `id`, `passenger_id` (FK to auth.users), `assigned_driver_id` (FK to verification.drivers), `service_type`, `category`, `pricing_mode`, `status`, `auto_accept_driver`, `is_scheduled`, `is_risky`
- **Pricing**: `baseline_min_price`, `baseline_max_price`, `final_price`, `scheduled_at`
- **Lifecycle**: `accepted_at`, `completed_at`, `cancelled_at`, `cancellation_reason`
- **Relationships**: `stops` (1:N), `proof_images` (1:N), `verification_codes` (1:N), polymorphic detail (city_ride, intercity, freight, courier, grocery) via 1:1 FKs

### Design Decisions

- **Polymorphic detail pattern**: Uses nullable 1:1 FKs to detail tables (city_ride, intercity, etc.) rather than STI or JSONB - maintains referential integrity and type safety.
- **Separate schema (`service_request`)**: Isolates ride domain from billing/auth/verification schemas.
- **Extensive check constraints**: Enforce business rules at DB level (positive prices, valid coordinates, etc.).
- **Indexed foreign keys**: All FKs indexed for join performance.

---

## 2. Stop, ProofImage, VerificationCode ORM Models

Supporting models for ride lifecycle management.

### Stop (ServiceStopORM)

- `sequence_order` for route ordering
- Geographic: `latitude`, `longitude` (PostGIS-compatible Numeric)
- Address fields for display/geocoding
- Timestamps: `arrived_at`, `completed_at`
- Relationships to `proof_images` and `verification_codes`

### ProofImage (ServiceProofImageORM)

- Tracks S3 file_key for proof uploads (pickup/dropoff photos)
- Audit: `uploaded_by_user_id` or `uploaded_by_driver_id`
- Integrity: `checksum_sha256`, `file_size_bytes`, `mime_type`
- Links to `stop` (optional) and `service_request`

### VerificationCode (ServiceVerificationCodeORM)

- OTP for start/complete verification
- `code`, `attempts`, `max_attempts`, `expires_at`
- Tracks `verified_at` and who verified (user or driver)
- Prevents replay attacks via max_attempts

### Design Decisions

- **Immutable proof records**: Once uploaded, proofs are never modified (audit trail).
- **Coordination via stop**: Both proofs and verification codes link to stops for precise location context.
- **Separate verification from auth**: Ride-specific OTP independent of user authentication flow.

---

## 3. Ride Repositories

Concrete repositories implementing domain protocols with SQLAlchemy.

### ServiceRequestRepository

- `create_full(ride, stops, detail_data)`: Atomic creation of ride + detail + stops in single flush
- `find_by_id(ride_id, load_relations=True)`: Eager loads stops, proofs, codes, detail via `selectinload`
- `update_status()`: Centralized status transition with optional timestamps/pricing
- Domain-to-ORM mapping via `_ride_orm_to_domain()` and `_build_detail_orm()`

### StopRepository, ProofImageRepository, VerificationCodeRepository

- CRUD operations with domain mapping
- Convenience queries: `find_by_ride()`, `find_active_by_ride()` for codes
- State transition helpers: `update_arrived_at()`, `update_completed_at()`, `update_verification()`

### Design Decisions

- **Eager loading option**: `load_relations` flag controls join complexity for list vs detail views
- **Repository pattern**: Use cases work with domain objects only, unaware of ORM
- **Type-safe enums**: SQLAlchemy `Enum` types mapped to Python enums via `.value`

---

## 4. Ride Dependencies

FastAPI dependency injection wiring infrastructure to use cases.

### Providers

- **Repository providers**: Create scoped instances with AsyncSession
- **GeospatialClient**: HTTP adapter to `/api/v1/drivers/nearby` with fallback NullGeospatialClient
- **WebSocketManager**: Singleton for driver/passenger connections, broadcasts
- **S3StorageProvider**: Generates presigned PUT/GET URLs for proof images
- **CacheManager**: Redis for candidate caching and ride state caching
- **WebhookClient**: Dispatches ride jobs to driver apps with idempotency
- **EventPublisher**: Kafka event publishing (ServiceRequestCreatedEvent, etc.)

### Design Decisions

- **Null object pattern**: NullGeospatialClient allows local dev without geospatial service
- **App state singletons**: Heavy objects (WebSocketManager, CacheManager, publisher) in `app.state`
- **Constructor injection**: All use cases receive dependencies via __init__, enabling unit testing

---

## 5. Ride Use Cases

Orchestrates ride lifecycle from creation through completion.

### Key Methods

**CreateRideUseCase**
- Builds domain objects (ServiceRequest, Stops) from validated schemas
- Calls `create_full()` for atomic persistence
- Emits `ServiceRequestCreatedEvent` to Kafka (triggers geospatial matching)
- Enters MATCHING state (enables acceptance/bidding)

**AcceptRideUseCase**
- Validates FIXED pricing mode only (BID/HYBRID go through bidding service)
- Checks driver eligibility (via DriverEligibilityClient)
- State transition: CREATED -> ACCEPTED, sets assigned_driver_id
- Publishes ServiceRequestAcceptedEvent, broadcasts via WebSocket

**InternalAssignDriverUseCase**
- Used by bidding service after BID_ACCEPTED (bypass pricing mode check)
- Updates final_price from winning bid
- Publishes with passenger_user_id for location service tracking

**StartRideUseCase / CompleteRideUseCase**
- Optional OTP verification if `requires_otp_start/end` (city_ride)
- Verifies code via VerificationCodeRepository
- State transitions with timestamps
- Emits ServiceRequestStartedEvent / ServiceRequestCompletedEvent

**CancelRideUseCase**
- Passenger-only, validates ownership
- State: -> CANCELLED with reason
- Broadcasts cancellation to driver and passenger

**FindNearbyDriversUseCase**
- Calls GeospatialClient with lat/lng/radius/filters
- Caches candidates in Redis with TTL (10 min)
- Publishes DriverMatchingRequestedEvent
- Returns ranked DriverCandidate list (by composite_score, distance)

**BroadcastRideToDriversUseCase**
- Sends NEW_JOB WebSocket event to candidate drivers
- Dispatches webhook to driver apps (idempotent with key)
- Publishes DriverMatchingCompletedEvent

**Upload Proof Flow**
- GenerateProofUploadUrlUseCase -> presigned PUT URL (S3, 15 min expiry)
- Client uploads binary directly to S3 (bypasses service)
- UploadProofUseCase -> registers metadata (file_key, checksum, uploader)
- Emits ServiceProofUploadedEvent
- GetProofWithUrlUseCase -> retrieves proof + presigned GET URL for viewing

### Design Decisions

- **Event-driven**: Kafka events trigger downstream services (geospatial, location, notification)
- **WebSocket for real-time**: Sub-second driver/passenger updates vs. polling
- **OTP at ride boundaries**: Optional verification for start/complete (anti-fraud)
- **Separate geospatial service**: External HTTP adapter allows independent scaling
- **Proof upload via S3 direct**: Avoids proxying large binaries through ride service
- **Idempotent webhooks**: `idempotency_key={ride_id}:{driver_id}` prevents duplicate job dispatches

---

# End-to-end Flow

## 1. Create Ride (City Ride Example)

1. **Client** -> POST `/rides` with CreateRideRequest (service_type=CITY_RIDE, stops[], detail{})
2. **Route** -> `CreateRideUseCase.execute(cmd, passenger_id)`
3. **Domain Construction** -> `ServiceRequest.create()` validates invariants, creates in-memory domain objects
4. **Atomic Persistence** -> `create_full()`:
   - INSERT ServiceRequestORM
   - INSERT CityRideDetailORM
   - INSERT ServiceStopORM for each stop
5. **State Transition** -> `ride.begin_matching()` -> status=MATCHING
6. **Kafka Publish** -> `ServiceRequestCreatedEvent` (pickup/dropoff lat/lng, vehicle_type, radius)
7. **WebSocket** -> Broadcast RIDE_CREATED to passenger
8. **Response** -> RideResponse with full object
9. **Downstream** -> Geospatial service receives event, runs driver matching, publishes driver.candidates

## 2. Driver Matching & Broadcast

1. **Geospatial Service** -> Finds eligible drivers via H3 cell + PostGIS proximity
2. **Publishes** -> `driver.matching.completed` with candidate list
3. **RideKafkaConsumer** -> Consumes event, calls `InternalAssignDriverUseCase` (or client triggers FindNearbyDrivers)
4. **Alternative** -> Client calls GET `/drivers/nearby`, then POST `/broadcast` (Ride flow)
5. **Broadcast** -> `BroadcastRideToDriversUseCase`:
   - WebSocket: NEW_JOB event to candidate drivers
   - Webhook: HTTP POST to driver app `/internal/rides/jobs` with idempotency
6. **Driver Response** -> Accepts via POST `/rides/{id}/accept` (FIXED) or bids via bidding service (BID_BASED/HYBRID)

## 3. Fixed-Price Ride Acceptance

1. **Driver** -> POST `/rides/{id}/accept` (FIXED pricing only)
2. **Route** -> `AcceptRideUseCase`
3. **Validation** -> Checks pricing_mode=FIXED, ride status=MATCHING
4. **Driver Eligibility** -> Calls DriverEligibilityClient (HTTP, 200ms timeout)
5. **State Transition** -> `ride.accept(driver_id)` -> status=ACCEPTED, assigned_driver_id=driver_id
6. **Persistence** -> `update_status()` with accepted_at, assigned_driver_id
7. **Kafka** -> Publishes ServiceRequestAcceptedEvent (consumed by location service for tracking)
8. **WebSocket** ->
   - To passenger: DRIVER_ASSIGNED (with driver_id)
   - To driver: JOB_ASSIGNED (with ride_id)
9. **Response** -> RideResponse

## 4. Bidding-Based Assignment (BID_BASED / HYBRID)

1. **Ride Created** -> Enters MATCHING state (same as FIXED)
2. **Bidding Service** -> Creates bidding session via POST `/bidding/sessions` (linked to ride_id)
3. **Drivers Bid** -> POST `/sessions/{id}/bids` with amount, ETA
4. **Auto-Accept (HYBRID)** -> If bid_amount <= baseline_min, BiddingService creates AUTO_ACCEPT_REQUESTED outbox event
5. **Driver Accepts** -> POST `/sessions/{id}/accept` (or auto-accept)
6. **Bidding Service Publishes** -> BID_ACCEPTED event to Kafka
7. **RideKafkaConsumer** -> Consumes BID_ACCEPTED:
   - Calls `InternalAssignDriverUseCase.execute(ride_id, driver_id, final_price=amount)`
   - Updates ride status to ACCEPTED
   - Publishes ServiceRequestAcceptedEvent with passenger_user_id
8. **Location Service** -> Subscribes to accepted event, begins tracking
9. **WebSocket** -> Broadcasts to passenger & driver

## 5. Start Ride (with OTP)

1. **Driver** -> POST `/rides/{id}/start` with VerifyAndStartRequest (optional verification_code)
2. **Route** -> `StartRideUseCase`
3. **Authorization** -> Checks assigned_driver_id matches
4. **OTP Verification (if required)** ->
   - Finds active code via VerificationCodeRepository
   - `code.verify(verification_code, driver_id)` -> validates match, marks verified
   - Persists via update_verification()
5. **State Transition** -> `ride.start()` -> status=ARRIVING (or IN_PROGRESS)
6. **Persistence** -> `update_status()` with no timestamps (arrived_at set later)
7. **Events** -> ServiceRequestStartedEvent via Kafka
8. **WebSocket** -> RIDE_STARTED to passenger

## 6. Stop Arrival & Completion

1. **Driver** -> POST `/stops/{id}/arrived`
2. **Route** -> `MarkStopArrivedUseCase`
3. **Validation** -> Driver assigned to ride, stop belongs to ride
4. **State** -> `stop.mark_arrived()` -> sets arrived_at=now
5. **Persistence** -> `update_arrived_at()`
6. **Check Ride Status** -> If ride was ACCEPTED, transition to ARRIVING
7. **Kafka** -> ServiceStopArrivedEvent
8. **WebSocket** -> STOP_UPDATED to passenger
9. **Repeat** -> POST `/stops/{id}/completed` when stop fulfilled (similar flow)

## 7. Proof Upload

1. **Driver/Passenger** -> POST `/rides/{id}/proofs/upload-url` with proof_type, file_name, mime_type
2. **Authorization** -> Checks passenger or assigned_driver_id matches
3. **Key Generation** -> `build_proof_key(ride_id, proof_type, file_name)` -> `rides/{ride_id}/proofs/PICKUP/{uuid}.jpg`
4. **S3 Presigned URL** -> `generate_presigned_put_url()` (15 min expiry)
5. **Client** -> PUT binary directly to S3 (bypasses service)
6. **Client** -> POST `/rides/{id}/proofs` with UploadProofRequest (file_key, checksum, etc.)
7. **Validation** -> Authorizes uploader, creates ProofImage domain object
8. **Persistence** -> ProofImageRepository.create()
9. **Event** -> ServiceProofUploadedEvent (ride_id, proof_id, proof_type)

## 8. Complete Ride

1. **Driver** -> POST `/rides/{id}/complete` with VerifyAndCompleteRequest (optional code, final_price)
2. **Route** -> `CompleteRideUseCase`
3. **Validation** -> Driver assigned, optional OTP verification (similar to start)
4. **State Transition** -> `ride.complete()` -> status=COMPLETED
5. **Persistence** -> `update_status()` with completed_at, final_price
6. **Cache** -> Delete ride from Redis cache
7. **Events** -> ServiceRequestCompletedEvent (ride_id, final_price)
8. **WebSocket** -> RIDE_COMPLETED to passenger
9. **Cleanup** -> Location service stops tracking

---

# Architectural Roles

- **ServiceRequest ORM Model**: Defines ride domain entity with polymorphic detail tables, comprehensive constraints, and lifecycle state machine in the `service_request` schema.
- **Stop/ProofImage/VerificationCode ORMs**: Supporting models for route sequencing, evidence capture, and OTP verification with referential integrity and auditability.
- **Ride Repositories**: Implement domain persistence contracts (ServiceRequest, Stop, Proof, VerificationCode) with eager loading, atomic creation, and type-safe enum mappings.
- **Ride Dependencies**: Wire GeospatialClient (nearby drivers), WebSocketManager (real-time), S3StorageProvider (proof uploads), CacheManager (candidate/ride caching), and EventPublisher (Kafka) into use cases via DI.
- **Ride Use Cases**: Orchestrate ride lifecycle from creation through matching, acceptance (fixed or bidding), OTP verification, stop tracking, proof uploads, and completion with event-driven integration.

---

# See also

* **CLAUDE.md** — Project overview, service descriptions, dev commands
* **auth-doc.md**, **verification-doc.md**, **bidding-doc.md**, **location-doc.md** — Other service documentation
* `services/ride/ride/main.py` — FastAPI app with WebSocket routes and startup/shutdown
* `libs/platform/src/sp/infrastructure/messaging/publisher.py` — EventPublisher for domain events
* `services/bidding/bidding/main.py` — Bidding service that integrates with ride assignment
