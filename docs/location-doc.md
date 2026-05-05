# Location Service Documentation

## Overview

The Location service owns real-time GPS ingestion, driver online/offline status, live ride location lookup, nearby-driver reads for Geospatial service, Mapbox geocoding, PostGIS location history, and WebSocket ride tracking.

Base path:

```text
/api/v1/location
```

Storage model:

- Redis stores live driver/passenger state and ride participant cache.
- PostGIS stores append-only historical pings.
- WebSocket connections are in-memory only.

Identity rule:

- Driver actor ID is `verification.drivers.id`.
- Passenger actor ID is auth `users.id`.
- HTTP `CurrentDriver` and WS `get_current_driver_ws` resolve driver profile ID from the authenticated auth user.
- `OptionalDriverId` returns the driver's profile ID when the current auth user has one, otherwise `None`.

---

## Update Driver Location (HTTP Fallback)

Route:

```text
POST /api/v1/location/drivers/{driver_id}/location
```

Schema:

```python
class LocationUpdateRequest(BaseModel):
    lat: float = Field(..., ge=-90.0, le=90.0)
    lng: float = Field(..., ge=-180.0, le=180.0)
    accuracy: float = Field(..., ge=0.0)
    speed: float | None = Field(None, ge=0.0)
    heading: float | None = Field(None, ge=0.0, le=360.0)
    ts: int
```

Flow:

1. `CurrentDriver` resolves acting `driver_id`.
2. Caller must match path `driver_id` unless current user role is `admin`.
3. Rate limiter checks driver context:
   - ONLINE: 2 pings / 5 seconds.
   - ON_RIDE: 3 pings / 5 seconds.
4. Previous Redis location is loaded for impossible-jump validation.
5. Request converts to domain `LocationUpdate(actor_type=DRIVER)`.
6. Domain validation checks coordinates, accuracy, speed, and jump distance.
7. Redis current state is updated.
8. PostGIS append is scheduled in background.
9. If `ride_id` is present, WebSocket manager broadcasts `DRIVER_LOCATION_UPDATED`.
10. Kafka `driver.location.updated` is published best-effort if configured.

Response:

```text
204 No Content
```

Failure mapping:

| Error | HTTP |
|---|---:|
| Invalid coordinates/accuracy/speed/jump | 422 |
| Rate limit exceeded | 429 |
| Actor not authorized | 403 |

---

## Get Current Driver Location

Route:

```text
GET /api/v1/location/drivers/{driver_id}/location
```

Current implementation behavior:

- The route authenticates `CurrentDriver`.
- The use case is called with the authenticated/resolved driver ID.
- The path `driver_id` is not used for lookup in the current route implementation.

Flow:

1. Resolve current driver's verification `driver_id`.
2. Fetch driver location from Redis.
3. Reject if location is missing or stale.
4. Return `DriverLocationResponse`.

Response:

```json
{
  "driver_id": "UUID",
  "status": "ONLINE|ON_RIDE|OFFLINE",
  "lat": 31.52,
  "lng": 74.35,
  "heading": 180,
  "speed": 42.1,
  "accuracy": 8.5,
  "updated_at": "datetime",
  "ride_id": "UUID | null"
}
```

---

## Set Driver Status

Route:

```text
POST /api/v1/location/drivers/{driver_id}/status
```

Schema:

```python
class DriverStatusRequest(BaseModel):
    status: Literal["ONLINE", "OFFLINE"]
```

Flow:

1. `CurrentDriver` resolves acting `driver_id`.
2. Caller must match path `driver_id` unless current user role is `admin`.
3. `ONLINE` stores status in Redis.
4. `OFFLINE` removes driver from Redis geo set and clears live location hash.
5. Kafka `driver.status.changed` is published best-effort if configured.

Response:

```json
{
  "success": true,
  "message": "string"
}
```

---

## Get Nearby Drivers

Route:

```text
GET /api/v1/location/drivers/nearby?lat=31.52&lng=74.35&radius_km=5&max_results=50
```

Purpose:

- Internal endpoint used by Geospatial service and trusted services.
- Requires normal auth through `CurrentUser`.

Flow:

1. Query parameters are validated.
2. Redis geo query finds nearby driver IDs.
3. Driver hashes are batch-loaded.
4. Stale/offline drivers are excluded.
5. Stale geo members are cleaned up.
6. Response returns live driver snapshots.

Response:

```json
{
  "drivers": [
    {
      "driver_id": "UUID",
      "status": "ONLINE",
      "lat": 31.52,
      "lng": 74.35,
      "heading": 180,
      "speed": 42.1,
      "accuracy": 8.5,
      "updated_at": "datetime",
      "ride_id": null
    }
  ],
  "radius_km": 5.0,
  "count": 1
}
```

---

## Get Ride Live Locations

Route:

```text
GET /api/v1/location/rides/{ride_id}/locations
```

Flow:

1. `CurrentUser.user_id` is read from JWT.
2. `OptionalDriverId` resolves verification `driver_id` if the current auth user is also a driver.
3. Redis participant cache is loaded for the ride:

```text
(driver_id, passenger_user_id)
```

4. Caller is authorized if:
   - `caller_user_id == passenger_user_id`, or
   - `caller_driver_id == driver_id`.
5. Driver and passenger live locations are fetched concurrently.
6. Response returns either or both positions when available.

Response:

```json
{
  "ride_id": "UUID",
  "driver": {
    "driver_id": "UUID",
    "status": "ON_RIDE",
    "lat": 31.52,
    "lng": 74.35,
    "updated_at": "datetime",
    "ride_id": "UUID"
  },
  "passenger": {
    "user_id": "UUID",
    "lat": 31.521,
    "lng": 74.351,
    "updated_at": "datetime",
    "ride_id": "UUID"
  }
}
```

Important:

- The caller cannot supply participant IDs.
- Authorization is based on Redis participant cache populated from ride accepted events.
- Driver auth user ID is never compared directly against ride `driver_id`.

---

## Get Location History

Route:

```text
GET /api/v1/location/actors/{actor_id}/history?since=<datetime>&until=<datetime>&actor_type=DRIVER
```

Query:

```python
since: datetime
until: datetime
actor_type: "DRIVER" | "PASSENGER" = "DRIVER"
```

Flow:

1. `CurrentUser` is authenticated.
2. Caller role must be `admin` or `support`.
3. Actor type is normalized to uppercase.
4. PostGIS history is queried by actor/time window.
5. Response returns ordered points and total count.

Response:

```json
{
  "actor_id": "UUID",
  "actor_type": "DRIVER",
  "ride_id": null,
  "points": [
    {
      "lat": 31.52,
      "lng": 74.35,
      "speed": 42.1,
      "heading": 180,
      "accuracy": 8.5,
      "recorded_at": "datetime"
    }
  ],
  "total": 1
}
```

---

## Geocode

Route:

```text
POST /api/v1/location/geocode
```

Schema:

```python
class GeocodeRequest(BaseModel):
    address: str = Field(..., min_length=3)
```

Flow:

1. Authenticated user calls route.
2. Cache is checked for normalized address.
3. Mapbox forward geocoding is called on miss.
4. Result is cached.
5. A structured address is returned.

Response:

```json
{
  "formatted": "Model Town, Lahore, Pakistan",
  "coordinates": {
    "latitude": 31.5204,
    "longitude": 74.3587
  },
  "street": null,
  "city": "Lahore",
  "country": "Pakistan",
  "postal_code": null
}
```

---

## Reverse Geocode

Route:

```text
POST /api/v1/location/reverse
```

Schema:

```python
class ReverseGeocodeRequest(BaseModel):
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
```

Flow:

1. Authenticated user calls route.
2. Cache is checked for rounded coordinate key.
3. Mapbox reverse geocoding is called on miss.
4. Fallback address is returned if Mapbox fails.

Response model is the same `AddressResponse` used by forward geocode.

---

## Driver GPS WebSocket

Route:

```text
WS /api/v1/location/ws/drivers/location?token=<JWT>
```

Auth:

- Uses `get_current_driver_ws`.
- JWT auth user ID is resolved to verification `driver_id`.
- Plain passenger users cannot connect.

Client message:

```json
{
  "lat": 31.52,
  "lng": 74.35,
  "accuracy": 8.5,
  "speed": 42.1,
  "heading": 180,
  "ts": 1714300000000,
  "ride_id": "UUID"
}
```

Flow:

1. Driver socket is registered by verification `driver_id`.
2. Server waits up to 30 seconds for messages.
3. On idle timeout, server sends `{"event":"ping"}`.
4. Client must reply with `{"event":"pong"}` within 10 seconds.
5. Normal GPS messages are validated as `LocationUpdateRequest`.
6. Optional `ride_id` is parsed from the message.
7. `UpdateDriverLocationUseCase` processes the ping.
8. Validation/rate errors are sent as `{"event":"error"}` and connection stays open.
9. On disconnect, socket is removed and driver is marked `OFFLINE`.

Error messages:

```json
{ "event": "error", "detail": "invalid_message_format" }
{ "event": "error", "detail": "rate_limit_exceeded" }
{ "event": "error", "detail": "invalid_location" }
{ "event": "error", "detail": "invalid_coordinates" }
```

---

## Ride Tracking WebSocket

Route:

```text
WS /api/v1/location/ws/rides/{ride_id}/track?token=<JWT>
```

Auth:

- Token is verified from query parameter.
- If current auth user has a driver profile, route resolves `driver_id`.
- Authorization reuses `GetRideLocationsUseCase` with `(caller_user_id, caller_driver_id)`.

Flow:

1. Token is verified.
2. Optional driver profile is resolved from `verification.drivers`.
3. Ride participant authorization is checked from Redis.
4. Passenger socket is registered by auth `user_id`.
5. User subscribes to the ride.
6. Server heartbeat sends text `{"event":"ping"}` after 30 seconds idle.
7. Client replies `pong` or `{"event":"pong"}`.
8. Driver GPS updates are pushed as `DRIVER_LOCATION_UPDATED`.
9. On disconnect, user is unsubscribed and socket removed.

Server update payload:

```json
{
  "event": "DRIVER_LOCATION_UPDATED",
  "timestamp": "datetime",
  "data": {
    "driver_id": "UUID",
    "lat": 31.52,
    "lng": 74.35,
    "heading": 180,
    "speed": 42.1
  }
}
```

---

## Ride Event Consumer

The Location service consumes `ride-events`.

Accepted ride:

```json
{
  "event_type": "service.request.accepted",
  "payload": {
    "ride_id": "UUID",
    "driver_id": "UUID",
    "passenger_user_id": "UUID"
  }
}
```

Effects:

1. Store ride participants in Redis.
2. Mark driver `ON_RIDE`.
3. Subscribe passenger to ride updates where applicable.

Completed/cancelled ride:

```json
{
  "event_type": "service.request.completed|service.request.cancelled",
  "payload": {
    "ride_id": "UUID",
    "driver_id": "UUID"
  }
}
```

Effects:

1. Remove ride participant cache.
2. Clear ride WebSocket subscriptions.
3. Mark driver `ONLINE` if driver ID is present.

---

## Domain Models

### LocationUpdate

```python
class LocationUpdate:
    actor_id: UUID
    actor_type: ActorType
    latitude: float
    longitude: float
    accuracy_meters: float
    speed_kmh: float | None
    heading_degrees: float | None
    recorded_at: datetime
    ride_id: UUID | None
```

### DriverLocation

```python
class DriverLocation:
    driver_id: UUID
    status: DriverStatus
    last_update: LocationUpdate | None
    updated_at: datetime
    ride_id: UUID | None
```

### PassengerLocation

```python
class PassengerLocation:
    user_id: UUID
    last_update: LocationUpdate | None
    updated_at: datetime
    ride_id: UUID | None
```

### LocationHistory

```python
class LocationHistory:
    id: UUID
    actor_type: ActorType
    actor_id: UUID
    latitude: float
    longitude: float
    accuracy_meters: float | None
    speed_kmh: float | None
    heading_degrees: float | None
    recorded_at: datetime
    ingested_at: datetime
    ride_id: UUID | None
```

---

## Routes Summary

| Method | URL | Description |
|---|---|---|
| POST | `/api/v1/location/drivers/{driver_id}/location` | Driver GPS HTTP fallback |
| GET | `/api/v1/location/drivers/{driver_id}/location` | Get authenticated driver's current location |
| POST | `/api/v1/location/drivers/{driver_id}/status` | Set driver ONLINE/OFFLINE |
| GET | `/api/v1/location/drivers/nearby` | Internal nearby live drivers query |
| GET | `/api/v1/location/rides/{ride_id}/locations` | Driver/passenger live positions with participant check |
| GET | `/api/v1/location/actors/{actor_id}/history` | Admin/support PostGIS history |
| POST | `/api/v1/location/geocode` | Mapbox forward geocode |
| POST | `/api/v1/location/reverse` | Mapbox reverse geocode |
| WS | `/api/v1/location/ws/drivers/location` | Driver GPS stream |
| WS | `/api/v1/location/ws/rides/{ride_id}/track` | Ride tracking subscription |

No public passenger-location HTTP update route is currently registered in `location.api.router`.

---

## Infrastructure Components

### RedisLocationStore

Stores live state:

- driver geo set,
- driver hashes,
- passenger hashes,
- ride participant cache.

### PostGISLocationRepository

Append-only historical location persistence. Provides actor history and ride route reads.

### LocationRateLimiter

Redis fixed-window limiter:

- normal/ONLINE: 2 pings per 5 seconds,
- ON_RIDE: 3 pings per 5 seconds.

Keys include actor type so driver and passenger counters stay separate.

### LocationEventPublisher

Wraps platform `EventPublisher` and publishes:

- `driver.location.updated`,
- `driver.status.changed`,
- passenger location events where configured.

No-ops when Kafka is disabled.

### WebSocketManager

In-memory socket hub for:

- driver sockets,
- passenger sockets,
- ride subscriptions,
- fan-out of `DRIVER_LOCATION_UPDATED`.

### MapboxClient

Cache-first geocoding adapter with fallback behavior when Mapbox is unavailable.

### LocationKafkaConsumer

Consumes ride lifecycle events to maintain Redis participant cache and driver ON_RIDE/ONLINE status.

### History Cleanup

`location.main` starts a daily cleanup task deleting `location.location_history` rows older than `LOCATION_HISTORY_RETENTION_DAYS`.

---

## Health And Metrics

Health route:

```text
GET /health
```

Returns service status, PostGIS probe status, and WebSocket stats.

Metrics route:

```text
GET /metrics
```

Returns Prometheus metrics from `MetricsCollector`.

---

## See Also

- `services/location/location/api/router.py`
- `services/location/location/application/use_cases.py`
- `services/location/location/infrastructure/redis_store.py`
- `services/location/location/infrastructure/kafka_consumer.py`
- `services/location/location/infrastructure/websocket_manager.py`
