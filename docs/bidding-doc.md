# Bidding Service Documentation

## Overview

The Bidding service owns competitive driver bids, passenger bid acceptance, HYBRID counter-offers, Redis coordination, WebSocket updates, idempotency, and outbox-driven assignment events for non-FIXED ride pricing modes.

Base path:

```text
/api/v1/bidding
```

Identity rule:

- Driver actions use `CurrentDriver`, which resolves verification `driver_id`.
- Passenger actions use `CurrentUser.user_id`, which is auth user ID.
- `driver_id` and `passenger_user_id` must never be treated as interchangeable.

---

## Pricing Mode Responsibilities

| Pricing mode | Bidding service behavior |
|---|---|
| `FIXED` | No bidding session; direct acceptance happens in Ride service |
| `BID_BASED` | Drivers submit bids; passenger accepts one bid |
| `HYBRID` | Drivers submit bids; passenger can counter; drivers can accept counters |

`CreateBiddingSessionUseCase` skips FIXED rides and raises `BiddingClosedError`.

---

## Session Creation From Ride Events

Bidding sessions are normally created by the Kafka consumer when Ride publishes `service.request.created`.

Flow:

1. Consumer receives ride-created payload.
2. Pricing mode is read from `pricing_mode`.
3. If pricing mode is `FIXED`, session creation is skipped.
4. For `BID_BASED` and `HYBRID`, `BiddingSession` is created with:
   - `service_request_id`
   - `passenger_user_id`
   - `pricing_mode`
   - `baseline_price` from `baseline_price`, `baseline_min_price`, or `baseline_max_price`.
5. Session is saved as `OPEN`.
6. Bidding opportunity can be dispatched to drivers.

---

## Place Bid

Route:

```text
POST /api/v1/bidding/sessions/{session_id}/bids
```

Schema:

```python
class PlaceBidRequest(BaseModel):
    driver_vehicle_id: UUID | None = None
    bid_amount: float = Field(..., gt=0)
    eta_minutes: int | None = Field(None, gt=0)
    message: str | None = None
```

Flow:

1. `CurrentDriver` resolves acting verification `driver_id`.
2. Idempotency key is checked if supplied.
3. Per-driver bid rate limit is enforced through Redis.
4. Session is loaded and must be `OPEN`.
5. Session must not be FIXED mode.
6. Existing lowest bid is loaded from Redis, hydrating from DB if needed.
7. New bid must beat current lowest bid rules.
8. If the same driver has an existing bid, this acts as a rebid/update.
9. Bid is saved and higher bids are marked `OUTBID` transactionally.
10. `BID_PLACED` or `BID_UPDATED` outbox event is saved.
11. If ride auto-accept qualifies, `AUTO_ACCEPT_REQUESTED` outbox event is saved.
12. Redis sorted set is updated.
13. `NEW_BID` is broadcast to session subscribers.
14. `BID_LEADER_UPDATED` is broadcast when leadership changes.
15. Successful response is cached for idempotency.

Response:

```json
{
  "id": "UUID",
  "bidding_session_id": "UUID",
  "driver_id": "UUID",
  "driver_vehicle_id": "UUID | null",
  "bid_amount": 450.0,
  "currency": "PKR",
  "eta_minutes": 15,
  "message": "string | null",
  "status": "ACTIVE",
  "placed_at": "datetime"
}
```

Outbox payload:

```json
{
  "bid_id": "UUID",
  "session_id": "UUID",
  "driver_id": "UUID",
  "amount": 450.0
}
```

Auto-accept payload:

```json
{
  "session_id": "UUID",
  "passenger_id": "UUID",
  "bid_id": "UUID"
}
```

Failure mapping:

| Error | HTTP |
|---|---:|
| Bid too low | 409 |
| Session closed/fixed mode | 422 |
| Session missing | 404 |
| Unauthorized/rate-limited | 403 |

---

## Accept Bid

Route:

```text
POST /api/v1/bidding/sessions/{session_id}/accept
```

Schema:

```python
class AcceptBidRequest(BaseModel):
    bid_id: UUID
```

Flow:

1. `CurrentUser.user_id` is used as passenger auth user ID.
2. Redis session lock is acquired to prevent concurrent accepts.
3. Session is loaded and must be `OPEN`.
4. Passenger must own the session when `passenger_user_id` is present.
5. Bid must exist, belong to the session, and be `ACTIVE`.
6. Session closes.
7. Bid is marked `ACCEPTED`.
8. `BID_ACCEPTED` outbox event is saved.
9. `BID_ACCEPTED` and `SESSION_CLOSED` WebSocket events are broadcast.
10. Winning driver is notified through webhook.
11. Response is cached for idempotency.
12. Redis lock is released.

Outbox/WebSocket payload:

```json
{
  "session_id": "UUID",
  "bid_id": "UUID",
  "ride_id": "UUID",
  "passenger_user_id": "UUID",
  "driver_id": "UUID",
  "amount": 450.0
}
```

Failure mapping:

| Error | HTTP |
|---|---:|
| Lock unavailable | 409 |
| Session/bid invalid | 422 |
| Unauthorized passenger | 403 |

---

## Withdraw Bid

Route:

```text
POST /api/v1/bidding/sessions/{session_id}/bids/{bid_id}/withdraw
```

Flow:

1. `CurrentDriver` resolves acting driver.
2. Session must be `OPEN`.
3. Bid must exist, belong to session, be `ACTIVE`, and belong to the acting driver.
4. Bid is marked `WITHDRAWN`.
5. `BID_WITHDRAWN` outbox event is saved.
6. Bid is removed from Redis sorted set.
7. `BID_WITHDRAWN` is broadcast.
8. New lowest bid is calculated and `BID_LEADER_UPDATED` is broadcast if present.

Payload:

```json
{
  "bid_id": "UUID",
  "session_id": "UUID",
  "driver_id": "UUID"
}
```

---

## Get Session Bids

Route:

```text
GET /api/v1/bidding/sessions/{session_id}
```

Flow:

1. Session is loaded by ID.
2. All bids for the session are loaded.
3. Lowest bid is read from Redis sorted set.
4. Counter-offers are loaded from repository.
5. Unified response is returned.

Response:

```json
{
  "session_id": "UUID",
  "service_request_id": "UUID",
  "status": "OPEN",
  "pricing_mode": "BID_BASED|HYBRID",
  "passenger_user_id": "UUID",
  "baseline_price": 400.0,
  "bids": [],
  "lowest_bid": 380.0,
  "counter_offers": []
}
```

No Kafka or WebSocket events; read-only route.

---

## Passenger Counter Offer

Route:

```text
POST /api/v1/bidding/sessions/{session_id}/passenger-counter
```

Schema:

```python
class PassengerCounterOfferRequest(BaseModel):
    counter_price: float = Field(..., gt=0)
    counter_eta_minutes: int | None = Field(None, gt=0)
```

Flow:

1. `CurrentUser.user_id` is used as passenger ID.
2. Session must exist and be `OPEN`.
3. Passenger must own the session.
4. Session must be `HYBRID`.
5. `CounterOffer` is created with:
   - `status=PENDING`
   - `user_id=passenger_user_id`
   - `driver_id=None`
   - `bid_id=None`
6. No placeholder bid and no fake driver ID are created.
7. `PASSENGER_COUNTER_BID` is broadcast to session subscribers.
8. Counter-offer response is returned.

WebSocket payload:

```json
{
  "session_id": "UUID",
  "passenger_id": "UUID",
  "counter_offer_id": "UUID",
  "counter_price": 380.0,
  "counter_eta_minutes": 25,
  "event": "passenger_counter_bid"
}
```

---

## Driver Accepts Passenger Counter

Route:

```text
POST /api/v1/bidding/sessions/{session_id}/counter/{counter_offer_id}/accept
```

Flow:

1. `CurrentDriver` resolves acting verification `driver_id`.
2. Redis lock is acquired for the session.
3. Session must be `OPEN`.
4. Session must be `HYBRID`.
5. Counter-offer must exist, belong to the session, and be `PENDING`.
6. A real `Bid` is created from counter price and ETA for the accepting driver.
7. Existing driver bid may be reused/updated depending on repository state.
8. Counter-offer is marked `ACCEPTED`.
9. Session is marked `CLOSED`.
10. Bid is marked `ACCEPTED`.
11. `COUNTER_OFFER_RESPONDED` and `BID_ACCEPTED` outbox events are saved.
12. `BID_ACCEPTED` and `SESSION_CLOSED` are broadcast.
13. Redis lock is released.

Payload:

```json
{
  "session_id": "UUID",
  "bid_id": "UUID",
  "counter_offer_id": "UUID",
  "driver_id": "UUID",
  "ride_id": "UUID",
  "passenger_user_id": "UUID",
  "amount": 380.0,
  "pricing_mode": "HYBRID"
}
```

Race behavior:

- First driver to acquire lock and accept the pending counter wins.
- Later attempts see closed session, non-pending counter, or lock conflict.

---

## Get Counter Offers

Route:

```text
GET /api/v1/bidding/sessions/{session_id}/counter-offers
```

Flow:

1. Counter offers are loaded by `session_id`.
2. All statuses are returned: `PENDING`, `ACCEPTED`, `REJECTED`, `EXPIRED`.
3. Response includes `bid_id` if a counter resulted in a real bid.

Response:

```json
[
  {
    "id": "UUID",
    "session_id": "UUID",
    "price": 380.0,
    "eta_minutes": 25,
    "user_id": "UUID | null",
    "driver_id": "UUID | null",
    "bid_id": "UUID | null",
    "status": "PENDING|ACCEPTED|REJECTED|EXPIRED",
    "responded_at": "datetime | null",
    "reason": "string | null",
    "created_at": "datetime"
  }
]
```

---

## WebSocket Endpoints

### Driver WebSocket

Route:

```text
WS /api/v1/bidding/ws/drivers?token=<JWT>
```

Flow:

1. Token is verified by `get_current_driver_ws`.
2. Driver profile ID is resolved from verification service tables.
3. Connection is registered by `driver_id`.
4. Client sends:

```json
{
  "action": "subscribe",
  "session_id": "UUID"
}
```

5. Driver subscribes only if session exists and is `OPEN`.

### Passenger WebSocket

Route:

```text
WS /api/v1/bidding/ws/passengers?token=<JWT>
```

Flow:

1. Token is verified by `get_current_user_ws`.
2. Passenger ID is `token_payload.user_id`.
3. Connection is registered by passenger auth user ID.
4. Client sends:

```json
{
  "action": "subscribe",
  "session_id": "UUID"
}
```

5. Passenger subscribes only if session belongs to `passenger_user_id`.

### Events

```python
class BiddingEvent(str, Enum):
    NEW_BID = "NEW_BID"
    BID_LEADER_UPDATED = "BID_LEADER_UPDATED"
    BID_ACCEPTED = "BID_ACCEPTED"
    BID_WITHDRAWN = "BID_WITHDRAWN"
    SESSION_CLOSED = "SESSION_CLOSED"
    SESSION_CANCELLED = "SESSION_CANCELLED"
    PASSENGER_COUNTER_BID = "PASSENGER_COUNTER_BID"
```

---

## Domain Models

### BiddingSession

```python
class BiddingSession:
    id: UUID
    service_request_id: UUID
    status: BiddingSessionStatus
    passenger_user_id: UUID | None
    pricing_mode: PricingMode | None
    baseline_price: float | None
    opened_at: datetime
    expires_at: datetime | None
    closed_at: datetime | None
```

### Bid

```python
class Bid:
    id: UUID
    service_request_id: UUID
    bidding_session_id: UUID
    driver_id: UUID
    driver_vehicle_id: UUID | None
    bid_amount: float
    currency: str
    eta_minutes: int | None
    message: str | None
    status: BidStatus
    placed_at: datetime
```

### CounterOffer

```python
class CounterOffer:
    id: UUID
    session_id: UUID
    price: float
    eta_minutes: int | None
    user_id: UUID | None
    driver_id: UUID | None
    bid_id: UUID | None
    status: CounterOfferStatus
    responded_at: datetime | None
    reason: str | None
```

---

## Enums

```python
class BiddingSessionStatus(Enum):
    OPEN = "OPEN"
    CLOSED = "CLOSED"
    EXPIRED = "EXPIRED"
    PAUSED = "PAUSED"

class BidStatus(Enum):
    ACTIVE = "ACTIVE"
    OUTBID = "OUTBID"
    WITHDRAWN = "WITHDRAWN"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"
    EXPIRED = "EXPIRED"

class CounterOfferStatus(Enum):
    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"
    EXPIRED = "EXPIRED"
```

---

## Routes Summary

| Method | URL | Description |
|---|---|---|
| POST | `/api/v1/bidding/sessions/{session_id}/bids` | Driver places or updates a bid |
| POST | `/api/v1/bidding/sessions/{session_id}/accept` | Passenger accepts active bid |
| GET | `/api/v1/bidding/sessions/{session_id}` | Get session bids and counter-offers |
| POST | `/api/v1/bidding/sessions/{session_id}/bids/{bid_id}/withdraw` | Driver withdraws active bid |
| POST | `/api/v1/bidding/sessions/{session_id}/passenger-counter` | Passenger creates HYBRID counter-offer |
| POST | `/api/v1/bidding/sessions/{session_id}/counter/{counter_offer_id}/accept` | Driver accepts passenger counter |
| GET | `/api/v1/bidding/sessions/{session_id}/counter-offers` | List counter-offer history |
| WS | `/api/v1/bidding/ws/drivers` | Driver real-time bidding channel |
| WS | `/api/v1/bidding/ws/passengers` | Passenger real-time bidding channel |

---

## Infrastructure Components

### WebSocketManager

Maintains driver/passenger connections and session subscriptions. Broadcasts bid and counter-offer events to subscribers.

### Redis Cache

Used for:

- idempotency keys,
- bid rate limiting,
- lowest-bid sorted sets,
- session/counter acceptance locks.

### Outbox Worker

Reads bid event rows and publishes them to `bidding-events`. This keeps DB state and emitted events transactionally aligned.

### Kafka Consumer

Consumes ride events to create non-FIXED bidding sessions and drive session lifecycle.

### External Clients

- `RideServiceClient`: validates ride and auto-accept rules.
- `DriverEligibilityClient`: driver eligibility checks where used.
- `WebhookClient`: notifies winning drivers and handles downstream dispatch.

---

## End-to-End Flows

### BID_BASED

```text
Ride created -> Bidding session OPEN -> drivers bid -> passenger accepts bid -> session CLOSED -> BID_ACCEPTED -> Ride assigns driver
```

### HYBRID

```text
Ride created with baseline -> Bidding session OPEN -> drivers bid -> passenger counters -> first driver accepts counter -> real bid created/accepted -> session CLOSED -> BID_ACCEPTED -> Ride assigns driver
```

### FIXED

```text
Ride created -> no bidding session -> driver accepts directly in Ride service
```

---

## See Also

- `services/bidding/bidding/api/router.py`
- `services/bidding/bidding/application/use_cases.py`
- `services/bidding/bidding/application/schemas.py`
- `services/ride/ride/application/use_cases.py`
