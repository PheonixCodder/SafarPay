
# Location Service Documentation

## Update Driver Location (HTTP Fallback)
```python
class LocationUpdateRequest(BaseModel):
    lat: float = Field(..., ge=-90.0, le=90.0, description="Latitude WGS-84")
    lng: float = Field(..., ge=-180.0, le=180.0, description="Longitude WGS-84")
    accuracy: float = Field(..., ge=0.0, description="Horizontal accuracy in metres")
    speed: float | None = Field(None, ge=0.0, description="Speed in km/h")
    heading: float | None = Field(None, ge=0.0, le=360.0, description="Heading in degrees (0=North)")
    ts: int = Field(..., description="Unix epoch milliseconds (client device clock)")
```

Routes to be used:
```
1. POST /drivers/{driver_id}/location
```

Flow:

1. **Authorization**: Verify caller is the driver (or admin) via JWT; reject 403 if not.
2. **Rate Limit Check**: Context-aware rate limit (ON_RIDE: 3/5s, ONLINE: 2/5s) via Redis; reject 429 if exceeded.
3. **Previous State Fetch**: Retrieve driver's last known location from Redis for jump detection.
4. **Domain Validation**: Convert request to `LocationUpdate` domain object; run `validate()` which checks:
   - Coordinate range [-90,90] / [-180,180]
   - Accuracy threshold (≤50m)
   - Speed cap (≤200 km/h declared)
   - Impossible jump detection via Haversine + time delta against previous ping
5. **Redis Persistence**: Store updated `DriverLocation` in Redis (Geo set + hash) with appropriate status (ON_RIDE vs ONLINE) and refresh TTL.
6. **PostGIS History**: Fire-and-forget async task appends location to PostGIS (with retry); never blocks the HTTP response.
7. **WebSocket Broadcast**: If `ride_id` present, broadcast `DRIVER_LOCATION_UPDATED` to all subscribed passengers on the ride.
8. **Kafka Event**: Best-effort publish `driver.location.updated` via outbox processor (if publisher configured).

Kafka Event payloads:
```json
driver.location.updated:
    {
        "driver_id": "UUID",
        "latitude": 31.52,
        "longitude": 74.35,
        "speed_kmh": 42.1,
        "heading": 180,
        "accuracy_meters": 8.5,
        "recorded_at": "2026-01-01T00:00:00Z",
        "ride_id": "UUID | null"
    }
```

Websocket payloads:
```json
DRIVER_LOCATION_UPDATED:
    {
        "event": "DRIVER_LOCATION_UPDATED",
        "timestamp": "2026-01-01T00:00:00Z",
        "data": {
            "driver_id": "UUID",
            "lat": 31.52,
            "lng": 74.35,
            "heading": 180,
            "speed": 42.1
        }
    }
```

No route-level database models mutated (domain model `DriverLocation` updated in Redis only; PostGIS record is append-only history).

---

## Update Passenger Location
```python
# Same LocationUpdateRequest schema as above
```

Routes to be used:
```
1. POST /passengers/{passenger_id}/location  (internal - called by passenger app)
```

Flow:

1. **Rate Limit Check**: 2/5s per passenger (more restrictive than driver when not on ride).
2. **Previous State Fetch**: Retrieve passenger's last location from Redis.
3. **Domain Validation**: Same `LocationUpdate.validate()` rules apply (accuracy, jumps, speed).
4. **Redis Persistence**: Store `PassengerLocation` in Redis (no Geo set; keyed by user_id).
5. **PostGIS History**: Fire-and-forget async append to PostGIS for safety/fraud trails.

No Kafka events (passenger locations are not broadcast externally).
No WebSocket events (passengers send locations; drivers receive via GetRideLocations).

No route-level database models mutated (Redis only + PostGIS history).

---

## Get Current Driver Location
```python
# No request body - driver_id is URL path parameter
```

Routes to be used:
```
1. GET /drivers/{driver_id}/location
```

Flow:

1. **Authorization**: Verify caller is the driver (or admin) via JWT.
2. **Redis Lookup**: Fetch `DriverLocation` from Redis.
3. **Staleness Check**: Reject 404 if last update >75s (+10s grace) ago.
4. **Build Response**: Map domain `DriverLocation` → `DriverLocationResponse`.

No Kafka events (read-only operation).
No WebSocket events (read-only operation).

Response model:
```json
{
    "driver_id": "UUID",
    "status": "ONLINE | ON_RIDE | OFFLINE",
    "lat": 31.52,
    "lng": 74.35,
    "heading": 180,
    "speed": 42.1,
    "accuracy": 8.5,
    "updated_at": "2026-01-01T00:00:00Z",
    "ride_id": "UUID | null"
}
```

---

## Set Driver Status (ONLINE / OFFLINE)
```python
class DriverStatusRequest(BaseModel):
    status: Literal["ONLINE", "OFFLINE"]
```

Routes to be used:
```
1. POST /drivers/{driver_id}/status
```

Flow:

1. **Authorization**: Verify caller is the driver (or admin) via JWT.
2. **Status Transition**:
   - ONLINE → Add driver to Redis Geo set (enables nearby-driver queries); set status ONLINE; clear ride_id.
   - OFFLINE → Remove driver from Redis Geo set; delete location hash; set status OFFLINE; clear ride_id.
3. **Kafka Event**: Optional publish `driver.status.changed` (if publisher configured) for analytics.

Kafka Event payloads:
```json
driver.status.changed:
    {
        "driver_id": "UUID",
        "status": "ONLINE | OFFLINE",
        "timestamp": "2026-01-01T00:00:00Z"
    }
```

No WebSocket events for status changes (drivers discover status via their own GET /location).

No route-level database models mutated (Redis Geo set + hash only).

---

## Get Nearby Drivers (Geospatial Service Internal)
```python
class NearbyDriversRequest(BaseModel):
    lat: float = Field(..., ge=-90.0, le=90.0)
    lng: float = Field(..., ge=-180.0, le=180.0)
    radius_km: float = Field(default=5.0, gt=0, le=50)
    max_results: int = Field(default=50, gt=0, le=200)
```

Routes to be used:
```
1. GET /drivers/nearby?lat=<>&lng=<>&radius_km=<>&max_results=<>
```

Flow:

1. **Geo Query**: Redis GEORADIUS on driver Geo set with lat/lng/radius_km.
2. **Fetch Details**: For each driver ID returned, fetch full `DriverLocation` hash.
3. **Filter Stale**: Exclude drivers whose last update is >75s old.
4. **Build Response**: Map to `NearbyDriversResponse` with `DriverLocationResponse` list.

No Kafka events (internal query).
No WebSocket events (HTTP response).

Response model:
```json
{
    "drivers": [
        {
            "driver_id": "UUID",
            "status": "ONLINE | ON_RIDE",
            "lat": 31.52,
            "lng": 74.35,
            "heading": 180,
            "speed": 42.1,
            "accuracy": 8.5,
            "updated_at": "2026-01-01T00:00:00Z",
            "ride_id": "UUID | null"
        }
    ],
    "radius_km": 5.0,
    "count": 23
}
```

---

## Get Ride Live Locations
```python
# No request body - ride_id and caller auth are from URL and JWT
```

Routes to be used:
```
1. GET /rides/{ride_id}/locations
```

Flow:

1. **Participant Cache Lookup**: Redis hash `ride:{ride_id}:participants` → (driver_id, passenger_user_id).
2. **Authorization**: Verify caller_id matches driver_id OR passenger_user_id from cache; reject 403 if not.
3. **Dual Fetch**: Concurrently fetch `DriverLocation` (driver_id) and `PassengerLocation` (passenger_user_id) from Redis.
4. **Build Response**: Map to `RideLocationsResponse` with both positions (may be null if not yet reported).

No Kafka events (read-only lookup).
No WebSocket events (HTTP response; separate WS endpoint exists for push).

Response model:
```json
{
    "ride_id": "UUID",
    "driver": {
        "driver_id": "UUID",
        "status": "ON_RIDE",
        "lat": 31.52,
        "lng": 74.35,
        "heading": 180,
        "speed": 42.1,
        "accuracy": 8.5,
        "updated_at": "2026-01-01T00:00:00Z",
        "ride_id": "UUID"
    },
    "passenger": {
        "user_id": "UUID",
        "lat": 31.521,
        "lng": 74.351,
        "accuracy": 10.0,
        "updated_at": "2026-01-01T00:00:00Z",
        "ride_id": "UUID"
    }
}
```

---

## Get Location History (Admin)
```python
class LocationHistoryRequest(BaseModel):
    since: datetime
    until: datetime
    actor_type: Literal["DRIVER", "PASSENGER"] = "DRIVER"
    # Validation: until > since; window ≤ 7 days
```

Routes to be used:
```
1. GET /actors/{actor_id}/history?since=<>&until=<>&actor_type=<>
```

Flow:

1. **Auth & Role Check**: JWT → caller_role; reject 403 if not admin/support.
2. **PostGIS Query**: SELECT * FROM location_history WHERE actor_id=? AND actor_type=? AND recorded_at BETWEEN since AND until ORDER BY recorded_at.
3. **Build Response**: Map rows → `LocationPointResponse` list; include total count.

No Kafka events (read-only admin query).
No WebSocket events (HTTP response).

Response model:
```json
{
    "actor_id": "UUID",
    "actor_type": "DRIVER",
    "ride_id": "UUID | null",
    "points": [
        {
            "lat": 31.52,
            "lng": 74.35,
            "speed": 42.1,
            "heading": 180,
            "accuracy": 8.5,
            "recorded_at": "2026-01-01T00:00:00Z"
        }
    ],
    "total": 1520
}
```

---

## Geocode (Mapbox Forward)
```python
class GeocodeRequest(BaseModel):
    address: str = Field(..., min_length=3)
```

Routes to be used:
```
1. POST /geocode
```

Flow:

1. **Cache Lookup**: Redis cache key `geocode:{md5(address)}`.
2. **Mapbox API**: On miss, call Mapbox Geocoding API; cache result 24h.
3. **Graceful Degradation**: If no candidates, return zero coordinates (never fails).

No Kafka events.
No WebSocket events.

Response model:
```json
{
    "formatted": "Model Town, Lahore, Pakistan",
    "coordinates": {
        "latitude": 31.5204,
        "longitude": 74.3587
    },
    "street": null,
    "city": null,
    "country": null,
    "postal_code": null
}
```

---

## Reverse Geocode (Mapbox)
```python
class ReverseGeocodeRequest(BaseModel):
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
```

Routes to be used:
```
1. POST /reverse
```

Flow:

1. **Cache Lookup**: Redis cache `reverse:{lat}:{lng}` rounded to 5 decimals.
2. **Mapbox API**: On miss, call Mapbox Reverse Geocoding; cache 24h.
3. **Return**: Structured address with street/city/country when available.

No Kafka events.
No WebSocket events.

Response model: same as Geocode (AddressResponse).

---

## WebSocket — Driver GPS Stream
**Endpoint**: `WS /ws/drivers/location?token=<JWT>`

**Auth Note**: Intentional exception to platform policy — mobile WebSocket clients cannot set Authorization headers, so JWT is passed via query parameter. HTTP endpoints use `Authorization: Bearer <token>` header exclusively.

**Client → Server message format**:
```json
{
    "lat": 31.52,
    "lng": 74.35,
    "accuracy": 8.5,
    "speed": 42.1,
    "heading": 180,
    "ts": 1714300000000,
    "ride_id": "UUID"  // optional, present when en route to pickup/dropoff
}
```

**Server → Client message formats**:
- **Heartbeat ping** (server-initiated every 30s idle):
  ```json
  {"event": "ping"}
  ```
- **Error** (validation/rate-limit):
  ```json
  {"event": "error", "detail": "rate_limit_exceeded" | "invalid_location" | "invalid_coordinates"}
  ```
- **Pong** (client reply to ping):
  ```json
  {"event": "pong"}
  ```

**Flow**:

1. **Auth**: Verify JWT → payload must have `role=driver` or `admin`. The `get_current_driver_ws` dependency resolves to `driver_id` (from `verification.drivers` table) using the `user_id` from the JWT — **NOT** using `user_id` directly as `driver_id`.
2. **Register**: `WebSocketManager.connect_driver(driver_id, websocket)`.
3. **Loop**:
   - Wait ≤30s for JSON message.
   - On timeout → send `{"event":"ping"}`; wait ≤10s for `{"event":"pong"}`; else close (1001).
   - If `event=ping` → reply `{"event":"pong"}`.
   - If `event=pong` → continue.
   - Otherwise parse as `LocationUpdateRequest`; process through `UpdateDriverLocationUseCase` (rate-limit, validate, store, history, broadcast, Kafka).
   - On `RateLimitExceededError`/validation errors → send error event, keep connection alive.
   - On `WebSocketDisconnect` → exit loop.
4. **Cleanup**: `disconnect_driver`, mark driver OFFLINE via `SetDriverStatusUseCase`.

**Side Effects**: Same as HTTP POST /drivers/{driver_id}/location (steps 2-8 of that flow).

No stored database models (transient WS session); persistent changes via Redis + PostGIS as above.

---

## WebSocket — Passenger Ride Tracking
**Endpoint**: `WS /ws/rides/{ride_id}/track?token=<JWT>`

**Client → Server**: Read-only from passenger perspective. Only ping/pong heartbeats.

**Server → Client message format**:
```json
{
    "event": "DRIVER_LOCATION_UPDATED",
    "timestamp": "2026-01-01T00:00:00Z",
    "data": {
        "driver_id": "UUID",
        "lat": 31.52,
        "lng": 74.35,
        "heading": 180,
        "speed": 42.1
    }
}
```

**Flow**:

1. **Auth**: Verify JWT (any role, typically passenger).
2. **Authorization**: Call `GetRideLocationsUseCase` to confirm caller is a participant (driver or passenger) of this ride; reject 403 if not.
3. **Register**: `ws_manager.connect_passenger(user_id, websocket)` + `subscribe_ride(ride_id, user_id)`.
4. **Heartbeat Loop**: Wait ≤30s for any text; on timeout send `"ping"`; expect `"pong"` within 10s else close (1001). If client sends `"ping"` → reply `"pong"`.
5. **On Disconnect**: `unsubscribe_ride`, `disconnect_passenger`.

**Push Source**: Driver GPS stream (via `UpdateDriverLocationUseCase`) calls `ws_manager.broadcast_driver_location()` which pushes to all passengers subscribed to that `ride_id`.

No stored database models (session state in Redis via participant cache; WS subscriptions are in-memory in `WebSocketManager`).

---

# Database Models (Domain Layer)

## DriverLocation
```python
@dataclass
class DriverLocation:
    """Current live state of a driver — stored in Redis, not PostgreSQL.

    Mutable: status transitions and location refreshes happen in-place.
    """
    driver_id: UUID
    status: DriverStatus = DriverStatus.OFFLINE
    last_update: LocationUpdate | None = None
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    ride_id: UUID | None = None

    # ------------------------------------------------------------------
    # State transitions
    # ------------------------------------------------------------------

    def mark_online(self) -> None:
        """Driver went online (app opened, available for rides)."""
        self.status = DriverStatus.ONLINE
        self.ride_id = None
        self.updated_at = datetime.now(timezone.utc)

    def mark_offline(self) -> None:
        """Driver went offline (app closed, not accepting rides)."""
        self.status = DriverStatus.OFFLINE
        self.ride_id = None
        self.updated_at = datetime.now(timezone.utc)

    def mark_on_ride(self, ride_id: UUID) -> None:
        """Driver accepted a ride and is now in an active ride session."""
        self.status = DriverStatus.ON_RIDE
        self.ride_id = ride_id
        self.updated_at = datetime.now(timezone.utc)

    def apply_update(self, update: LocationUpdate) -> None:
        """Apply a validated GPS ping to this driver's live state."""
        self.last_update = update
        self.updated_at = datetime.now(timezone.utc)
        if update.ride_id and self.status != DriverStatus.ON_RIDE:
            self.mark_on_ride(update.ride_id)

    # ------------------------------------------------------------------
    # Queries
    # ------------------------------------------------------------------

    def is_stale(self, threshold_seconds: int = _STALE_THRESHOLD_SECONDS) -> bool:
        """True if the driver has not sent a ping within the threshold + grace.

        The 10-second grace period (_STALE_GRACE_SECONDS) absorbs network jitter
        so a delayed ping doesn't briefly show a driver as stale.
        """
        effective = threshold_seconds + _STALE_GRACE_SECONDS
        delta = (datetime.now(timezone.utc) - self.updated_at).total_seconds()
        return delta > effective

    @property
    def is_on_ride(self) -> bool:
        """True when the driver is currently in an active ride session."""
        return self.status == DriverStatus.ON_RIDE

    @property
    def coordinates(self) -> Coordinates | None:
        if self.last_update is None:
            return None
        return Coordinates(
            latitude=self.last_update.latitude,
            longitude=self.last_update.longitude,
        )
```
*Stored in Redis (hash `driver:location:{driver_id}` + Geo set `drivers:geo`).*

## PassengerLocation
```python
@dataclass
class PassengerLocation:
    """Current live state of a passenger — stored in Redis.

    Used for safety monitoring, fraud detection, and pickup optimisation.
    """
    user_id: UUID
    last_update: LocationUpdate | None = None
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    ride_id: UUID | None = None

    def apply_update(self, update: LocationUpdate) -> None:
        self.last_update = update
        self.ride_id = update.ride_id
        self.updated_at = datetime.now(timezone.utc)

    def is_stale(self, threshold_seconds: int = _STALE_THRESHOLD_SECONDS) -> bool:
        """True if the passenger has not sent a ping within the threshold + grace window."""
        effective = threshold_seconds + _STALE_GRACE_SECONDS
        delta = (datetime.now(timezone.utc) - self.updated_at).total_seconds()
        return delta > effective

    @property
    def coordinates(self) -> Coordinates | None:
        if self.last_update is None:
            return None
        return Coordinates(
            latitude=self.last_update.latitude,
            longitude=self.last_update.longitude,
        )
```
*Stored in Redis (hash `passenger:location:{user_id}`).*

## LocationUpdate (Value Object)
```python
@dataclass(frozen=True)
class LocationUpdate:
    """A single GPS ping from a driver or passenger.

    Constructed from the raw WebSocket / HTTP payload.  Call ``validate()``
    before persisting or broadcasting — it raises domain exceptions on bad data.
    """
    actor_id: UUID
    actor_type: ActorType
    latitude: float
    longitude: float
    accuracy_meters: float
    recorded_at: datetime
    speed_kmh: float | None = None
    heading_degrees: float | None = None
    ride_id: UUID | None = None

    # ------------------------------------------------------------------
    # Business-rule validation (pure — no I/O)
    # ------------------------------------------------------------------

    def validate(
        self,
        previous: "LocationUpdate | None" = None,
        *,
        max_speed_kmh: float = _MAX_SPEED_KMH,
        min_accuracy_meters: float = _MIN_ACCURACY_METERS,
    ) -> None:
        """Validate this ping against all fraud / sanity rules.

        Raises a ``LocationDomainError`` subclass on the first violation found.
        Callers (use cases) catch these and decide whether to discard silently
        or propagate to the client.
        """
```
*Validation rules: coordinate range [-90,90] / [-180,180], accuracy threshold (≤50m), speed cap (≤200 km/h), impossible jump detection via Haversine + time delta vs max_speed_kmh.*

## LocationHistory (Immutable PostGIS Record)
```python
@dataclass(frozen=True)
class LocationHistory:
    """A single persisted location record in PostGIS.

    Immutable — once written it is never updated.
    """
    id: UUID
    actor_type: ActorType
    actor_id: UUID
    latitude: float
    longitude: float
    accuracy_meters: float
    recorded_at: datetime
    ingested_at: datetime
    ride_id: UUID | None = None
    speed_kmh: float | None = None
    heading_degrees: float | None = None

    @property
    def coordinates(self) -> Coordinates:
        return Coordinates(latitude=self.latitude, longitude=self.longitude)
```

---

# Enums

## ActorType
```python
class ActorType(str, Enum):
    DRIVER = "DRIVER"
    PASSENGER = "PASSENGER"
```

## DriverStatus
```python
class DriverStatus(str, Enum):
    OFFLINE = "OFFLINE"
    ONLINE = "ONLINE"
    ON_RIDE = "ON_RIDE"
```

## LocationDomainError Hierarchy
```python
LocationDomainError (base)
├── InvalidCoordinatesError          → 422
├── GPSAccuracyTooLowError           → 422 (WS: silent discard)
├── SpeedValidationError            → 422 (logged + discarded in WS)
├── ImpossibleJumpError              → 422 (logged + discarded in WS)
├── ActorNotFoundError               → 404
├── StaleLocationError               → 404
├── UnauthorisedLocationAccessError  → 403
├── RideNotActiveError               → 409
└── RateLimitExceededError           → 429 (WS: ping discarded, connection kept)
```

---

# Routes Summary

### Location Service Routes

| Method | URL | Description |
|--------|-----|-------------|
| POST | `/drivers/{driver_id}/location` | HTTP fallback GPS update (validates, stores, broadcasts if on ride) |
| GET | `/drivers/{driver_id}/location` | Get current driver location (with staleness check) |
| POST | `/drivers/{driver_id}/status` | Set driver ONLINE or OFFLINE (Redis Geo set management) |
| GET | `/drivers/nearby` | [Internal] Nearby ONLINE drivers within radius (Geospatial Service) |
| GET | `/rides/{ride_id}/locations` | Driver + passenger live positions for active ride (participant check) |
| GET | `/actors/{actor_id}/history` | [Admin] Time-windowed PostGIS location history |
| POST | `/geocode` | Mapbox forward geocode (cache-first, graceful degradation) |
| POST | `/reverse` | Mapbox reverse geocode (cache-first) |
| WS | `/ws/drivers/location` | Driver GPS ping stream (heartbeat, validation, broadcast to passengers) |
| WS | `/ws/rides/{ride_id}/track` | Passenger subscription to live driver location for a ride |

### Security Notes

- **WebSocket Authentication**: All WebSocket endpoints use `?token=<JWT>` query parameter. This is an intentional exception to the platform security policy because mobile WebSocket clients (iOS/Android) cannot set Authorization headers on the HTTP upgrade handshake.

- **HTTP Authentication**: All HTTP endpoints use `Authorization: Bearer <token>` header exclusively.

- **ID Semantics**:
  - `driver_id`: The driver's profile ID (from `verification.drivers` table). Obtained by resolving the authenticated user's `user_id` through the drivers table lookup. Used when the actor is a driver.
  - `user_id`: The user's auth ID (from `users` table). Used when the actor is a passenger/user.
  - The `CurrentDriver` dependency (both HTTP and WS variants) performs this resolution automatically — it never uses `user_id` directly as `driver_id`.

- **Rate Limiting**: Context-aware (ON_RIDE: 3 pings/5s, ONLINE: 2 pings/5s). Exceeding limits returns 429 on HTTP and discards the ping on WS (connection remains open).

- **Data Retention**: Live locations stored in Redis (TTL-managed). Historical records persisted to PostGIS (append-only, never updated).

---

# Infrastructure Components

## 1. LocationEventPublisher

This is the concrete adapter that converts domain updates into Kafka events.

It wraps `EventPublisher`.

### Purpose

Your application/use cases speak in domain objects like:

* `LocationUpdate`
* `DriverStatus`

This publisher turns them into event payloads and sends them to Kafka.

---

### `publish_driver_location_updated(...)`

Builds a `DriverLocationUpdatedEvent`.

Payload fields:

* `driver_id`
* `lat`
* `lng`
* `speed_kmh`
* `heading_degrees`
* `accuracy_meters`
* `ride_id`
* `recorded_at`

If the underlying Kafka publisher is `None`, it returns immediately.
So this class is safe even when Kafka is disabled.

---

### `publish_driver_status_changed(...)`

Builds a `DriverStatusChangedEvent`.

Payload fields:

* `driver_id`
* `status`
* `ride_id` optional

---

### `publish_passenger_location_updated(...)`

Same pattern, but for passengers.

Payload fields:

* `user_id`
* `lat`
* `lng`
* `ride_id`
* `recorded_at`

---

## 2. MapboxClient

This is the geocoding adapter.

It talks to Mapbox and adds caching plus error isolation.

### Constructor

* `access_token`: Mapbox API token
* `cache`: `CacheManager`

It also creates:

* a shared `httpx.AsyncClient`
* connection pooling
* 5 second timeout

---

### `geocode(address)`

Turns text like `"Model Town, Lahore"` into coordinate candidates.

#### Cache key

It hashes the normalized address:

* lowercased
* stripped
* SHA-256

That avoids storing raw addresses as keys.

#### Cache-first logic

1. Check Redis cache.
2. If found, return cached `Coordinates`.
3. Otherwise call Mapbox.
4. Convert returned features into `Coordinates`.
5. Store them in cache for 24 hours.

#### Failure behavior

Any exception:

* is logged
* returns `[]`

So a Mapbox outage does not break the service.

---

### `reverse_geocode(latitude, longitude)`

Turns coordinates into a structured `Address`.

#### Cache key

Uses rounded coordinates:

```python
f"{latitude:.6f}:{longitude:.6f}"
```

#### Fallback

If Mapbox fails or returns no features:

* it returns an `Address` with formatted raw coordinates

That is important because callers always get something usable.

#### Response mapping

It tries to extract:

* `place_name` → formatted address
* `text` → street
* `place` → city
* `country` → country
* `postcode` → postal code

---

## 3. LocationHistoryORM

This is the SQLAlchemy model for persisted GPS history.

### Important design point

This table is **append-only**.

It stores historical pings in PostGIS-backed storage, while live state lives in Redis.

That separation is intentional:

* Redis = fast current state
* PostGIS = durable history and spatial analysis

---

### Columns

#### `id`

Primary key UUID.

#### `actor_type`

Either `"DRIVER"` or `"PASSENGER"`.

#### `actor_id`

The driver ID or passenger/user ID.

#### `ride_id`

Optional, present when the ping belongs to a ride.

#### `latitude`, `longitude`

Stored as numeric values for ORM friendliness.

#### `accuracy_meters`, `speed_kmh`, `heading_degrees`

Optional telemetry fields.

#### `recorded_at`

Device timestamp from the client.

#### `ingested_at`

Server-side DB timestamp, automatically set by the database.

---

### Indexes

* `ix_loc_hist_actor_time`: efficient actor/time-window queries
* `ix_loc_hist_ride`: efficient ride history queries

The spatial GIST index is created via Alembic migration, not directly in the ORM.

---

## 4. PostGISLocationRepository

This is the persistence and query adapter for location history.

### Main job

It writes validated pings into `location.location_history` and provides historical reads.

---

### `append(update)`

This is designed for fire-and-forget usage.

It should not block the live WebSocket loop.

#### What it writes

It inserts:

* actor type
* actor ID
* ride ID
* lat/lng
* accuracy
* speed
* heading
* recorded_at

#### Retry strategy

It retries only for `OperationalError`:

* attempt 1
* retry after 0.2s
* retry after 0.5s
* then give up

That is a pragmatic transient-failure policy.

#### Non-retryable errors

* `IntegrityError`
* `ProgrammingError`

These fail immediately and are logged.

#### Why this design matters

It protects the live tracking path from DB instability.

The user still gets real-time tracking even if history persistence is temporarily degraded.

---

### `get_ride_route(ride_id)`

Returns all driver history points for a specific ride, ordered by `recorded_at ASC`.

This is useful for:

* route replay
* auditing
* debugging ride paths

It filters:

* `ride_id = :ride_id`
* `actor_type = 'DRIVER'`

---

### `get_actor_history(actor_id, actor_type, since, until)`

Returns historical pings for one actor in a time window.

It also enforces:

* max 10,000 rows
* ascending time order

---

### `_row_to_history(row)`

Converts raw DB rows into domain `LocationHistory`.

This isolates SQL shape from domain shape.

---

## 5. LocationRateLimiter

This prevents GPS ping spam.

### Strategy

Redis fixed-window counter:

* `INCR`
* `EXPIRE`

Two different windows:

* `ONLINE`: max 2 pings / 5 seconds
* `ON_RIDE`: max 3 pings / 5 seconds

This allows jitter and retries while rejecting abusive floods.

---

### `allow(actor_id, is_on_ride=False)`

#### Choose namespace

* `loc_rate` for normal state
* `loc_rate_ride` for ride state

This separation is important because switching ride status resets the effective counter.

#### Increment counter

Uses `CacheManager.increment(...)`, assumed atomic.

#### Decision

If count exceeds limit:

* logs a warning
* returns `False`

Otherwise:

* returns `True`

---

## 6. RedisLocationStore

This is the live state store.

It holds the current location/status snapshot in Redis.

### Key idea

Redis stores:

* current driver state
* current passenger state
* ride participant authorization cache
* nearby-driver geo index

This is the real-time state layer.

---

### Key layout

#### Geo set

`driver:geo`
Used for nearby-driver queries.

#### Driver hash

`driver:<driver_id>`
Stores:

* status
* lat
* lng
* heading
* speed
* accuracy
* updated_at
* ride_id

#### Passenger hash

`passenger:<user_id>`
Stores:

* lat
* lng
* accuracy
* updated_at
* ride_id

#### Ride participant hash

`ride:<ride_id>`
Stores:

* driver_id
* passenger_user_id

This is a security cache for ride-related authorization.

---

### `_HSET_EXPIRE_SCRIPT`

A Lua script that:

1. HSETs all fields
2. EXPIREs the key
3. Does both atomically in one round-trip

This avoids race windows where a hash is written but TTL is not yet set.

---

### `set_driver_location(...)`

This is the most important live-state write.

#### Step 1: `geoadd`

Adds driver to geo index.

#### Step 2: atomic hash write

Stores all current fields in the driver hash and refreshes TTL.

#### Important note

The docstring says "ONLINE-only" for geo set, but the implementation currently always does `geoadd(...)` regardless of status.
The `status` field is later used to filter results, and offline cleanup removes the member when status becomes OFFLINE.

So the practical design is:

* geo index may contain members briefly,
* status filtering protects query results,
* cleanup removes stale/offline entries.

---

### `get_driver_location(driver_id)`

Returns the parsed `DriverLocation` from Redis or `None` if missing.

---

### `remove_driver(driver_id)`

Deletes:

* the geo member
* the driver hash

This is used when the driver goes OFFLINE.

---

### `set_driver_status(...)`

Updates status without changing coordinates.

If the status becomes OFFLINE:

* removes the driver from geo set too.

That prevents offline drivers from appearing in nearby search.

---

### Passenger equivalents

`set_passenger_location` and `get_passenger_location` are the same idea for passengers.

---

### `set_ride_participants(...)`

Writes the authoritative ride participant pair into Redis.

This is important for security because later services can verify:

* who the driver is
* who the passenger is

It uses the same atomic Lua write.

---

### `get_ride_participants(...)`

Reads and parses the cached pair.

If parsing fails:

* logs a warning
* returns `None`

---

### `delete_ride_participants(...)`

Removes the ride authorization cache when ride ends.

---

### `get_drivers_in_radius(...)`

This is the nearby-driver query.

#### Step 1: Redis geo query

Uses `GEORADIUS` to find members near a coordinate.

#### Step 2: parse driver IDs

It extracts driver UUIDs from the geo result.

#### Step 3: batch fetch hashes

Uses a pipeline so Redis is not hit one-by-one.

#### Step 4: filter

Only drivers with `status == ONLINE` are returned.

#### Step 5: cleanup stale geo members

If a geo member exists but the hash expired, it removes that stale member.

This keeps the geo index tidy.

---

### Parsing helpers

#### `_parse_driver(...)`

Builds a `DriverLocation` domain object from Redis hash data.

It reconstructs:

* `DriverStatus`
* coordinates
* timestamp
* optional ride_id
* nested `LocationUpdate`

#### `_parse_passenger(...)`

Same idea for passenger state.

---

## 7. WebSocketManager

This is the in-process socket hub.

It does not store state in Redis.
It keeps live WebSocket connections in memory.

### Three maps

#### `_driver_conns`

`driver_id -> set[WebSocket]`

#### `_passenger_conns`

`user_id -> set[WebSocket]`

#### `_ride_subs`

`ride_id -> set[user_id]`

This means:

* many sockets per driver are supported,
* many sockets per passenger are supported,
* many subscribers per ride are supported.

---

### Driver lifecycle

#### `connect_driver(driver_id, ws)`

* accepts socket
* stores connection in `_driver_conns`

#### `disconnect_driver(driver_id, ws)`

* removes socket from set
* deletes key if last socket disappears

---

### Passenger lifecycle

#### `connect_passenger(...)`

Same pattern as drivers.

#### `disconnect_passenger(...)`

Same pattern.

---

### Ride subscriptions

#### `subscribe_ride(ride_id, user_id)`

Registers a user to receive ride updates.

#### `unsubscribe_ride(...)`

Removes one user from one ride.

#### `unsubscribe_all_from_ride(...)`

Clears all ride subscribers after completion/cancellation.

#### `get_ride_subscribers(...)`

Returns a copy of the user set for safe iteration.

---

### Broadcasting

#### `broadcast_driver_location(...)`

Builds a `DRIVER_LOCATION_UPDATED` event, then:

1. gets all subscribers for that ride,
2. gathers all sockets for those subscribers,
3. sends the message to every socket concurrently.

Returns the number of successful deliveries.

---

### `send_to_passenger(...)` / `send_to_driver(...)`

Generic targeted messaging helpers.

---

### `_send_to_many(...)`

This is the fan-out engine.

It:

* checks socket state,
* sends text payload,
* prunes dead sockets on failure,
* never raises delivery exceptions outward.

This is critical for resilience.

---

### `_prune(...)`

Removes a dead WebSocket from all maps.

One note: it ignores `actor_id` and just scans all maps.
That is simple but slightly broad. It works, but it is not the most selective cleanup strategy.

---

### `stats`

Returns counts of:

* active driver sockets
* active passenger sockets
* active ride subscriptions

Useful for diagnostics.

---

## 8. dependencies.py

This wires FastAPI request state into the use cases.

### Why this exists

Instead of creating Redis, DB, Kafka, etc. inside route handlers, the app initializes them once at startup and stores them in `request.app.state`.

These provider functions:

* read those singletons,
* assemble use cases,
* inject them into routes.

That gives you:

* testability
* clean separation
* no global mutable service locators

---

### Singleton accessors

These just return objects from `request.app.state`:

* `get_cache`
* `get_redis_store`
* `get_history_repo`
* `get_rate_limiter`
* `get_ws_manager`
* `get_event_publisher`
* `get_mapbox`
* `get_metrics`

---

### Use case factories

These construct application services with the correct dependencies.

#### `get_update_driver_location_uc`

Builds the main driver update use case with:

* store
* history repo
* rate limiter
* websocket manager
* publisher
* metrics

#### `get_update_passenger_location_uc`

Passenger equivalent.

#### `get_current_driver_location_uc`

Reads current driver state from Redis.

#### `get_current_passenger_location_uc`

Reads current passenger state from Redis.

#### `get_ride_locations_uc`

Builds the ride composite lookup.

#### `get_nearby_drivers_uc`

Builds geospatial search use case.

#### `get_location_history_uc`

Builds historical query use case.

#### `get_set_driver_status_uc`

Builds status update use case.

#### `get_geocode_uc` / `get_reverse_geocode_uc`

Builds Mapbox-backed geocoding use cases.

---

## 9. schemas.py

This defines the API contract.

### Inbound request models

#### `LocationUpdateRequest`

Validates live GPS messages.

Fields:

* `lat`
* `lng`
* `accuracy`
* `speed`
* `heading`
* `ts`

This is what the WebSocket route validates before handing off to the use case.

---

#### `DriverStatusRequest`

Only allows:

* `"ONLINE"`
* `"OFFLINE"`

---

#### `NearbyDriversRequest`

Validates nearby search filters:

* latitude
* longitude
* radius
* max results

---

#### `LocationHistoryRequest`

Validates a time window.

The validator enforces:

* `until > since`
* max window of 7 days

That prevents expensive unbounded history queries.

---

### Outbound response models

These are the structured responses for HTTP APIs.

#### `DriverLocationResponse`

Represents a live driver snapshot.

#### `PassengerLocationResponse`

Represents a live passenger snapshot.

#### `RideLocationsResponse`

Contains driver + passenger for a ride.

#### `NearbyDriversResponse`

Returns nearby driver list plus summary metadata.

#### `LocationPointResponse`

Represents a single historical point.

#### `LocationHistoryResponse`

Represents all points for an actor over a time range.

#### `CoordinatesResponse`

Used by geocoding responses.

#### `AddressResponse`

Full reverse-geocoded address structure.

#### `GeocodeRequest`

Text address input.

#### `ReverseGeocodeRequest`

Latitude/longitude input.

#### `StatusResponse`

Generic success/message wrapper.

---

# End-to-end flow

Now the full pipeline, from socket to storage.

## A) Driver connects

1. The driver opens the WebSocket.
2. `get_current_driver_ws` authenticates and identifies the driver.
3. `ws_driver_location` calls `ws_manager.connect_driver(...)`.
4. The socket is accepted and tracked in memory.

---

## B) Driver sends a location ping

1. The route receives JSON.
2. `LocationUpdateRequest(**data)` validates raw fields.
3. If the message contains `ride_id`, it is converted to `UUID`.
4. The route calls `UpdateDriverLocationUseCase.execute(...)`.

---

## C) Use case processing

Although you did not paste `UpdateDriverLocationUseCase`, from the infrastructure it almost certainly orchestrates this order:

1. Validate semantics.
2. Rate limit via `LocationRateLimiter`.
3. Update current state in Redis via `RedisLocationStore`.
4. Append history via `PostGISLocationRepository` asynchronously.
5. Publish Kafka domain events via `LocationEventPublisher`.
6. Broadcast real-time updates through `WebSocketManager`.
7. Return success.

That is the intended architecture.

---

## D) Driver disconnects

1. WebSocket disconnects or heartbeat fails.
2. Route exits loop.
3. `finally` runs.
4. `ws_manager.disconnect_driver(...)` removes the socket from memory.
5. `SetDriverStatusUseCase.execute(... OFFLINE)` removes state from Redis and emits an offline event.

---

# The architectural roles, in one sentence each

* **Route**: receives the socket message.
* **Schemas**: validate shape and ranges.
* **Use cases**: hold business rules.
* **Redis store**: current live state.
* **PostGIS repo**: historical persistence.
* **Rate limiter**: protects the system from spam.
* **Event publisher**: sends domain events to Kafka.
* **WebSocket manager**: fans out live updates.
* **Mapbox client**: geocoding service adapter.
* **Dependencies**: assemble everything from app state.

---

# See also

* **CLAUDE.md** — Project overview, service descriptions, dev commands
* **`libs/platform/src/sp/infrastructure/messaging/events.py`** — base `EventPublisher` that `LocationEventPublisher` wraps
* **`libs/platform/src/sp/infrastructure/cache/manager.py`** — `CacheManager` used by `RedisLocationStore`
* **`services/location/location/main.py`** — FastAPI app initialization and startup wiring
