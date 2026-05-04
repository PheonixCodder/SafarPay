# Bidding Service Documentation

## Place Bid
```python
class PlaceBidRequest(BaseModel):
    driver_vehicle_id: UUID | None = None
    bid_amount: float = Field(..., gt=0, description="Bid amount must be positive")
    eta_minutes: int | None = Field(None, gt=0)
    message: str | None = None
```

Routes to be used:
```
1. POST /sessions/{session_id}/bids
```

Flow:

1. **Idempotency & Rate Limiting**: Check for cached response using `idempotency_key`; if duplicate request in progress, raise `LockAcquisitionError`. Enforce 10 bids/minute rate limit per driver.
2. **Session Validation**: Retrieve bidding session from repository; raise 404 if not found or not OPEN.
3. **Price Validation**: Compare new bid against current lowest bid in Redis sorted set (hydrate from DB if empty); reject if not lower than current lowest.
4. **Bid Creation**: Create Bid domain object with ACTIVE status, persist via repository.
5. **Auto-Accept Logic**: Query ride service to check if bid amount qualifies for auto-accept (<= baseline_min); if so, prepare AUTO_ACCEPT_REQUESTED outbox event.
6. **Atomic Transaction**: Save bid, mark higher bids as OUTBID, persist BID_PLACED (and AUTO_ACCEPT_REQUESTED if applicable) outbox events within DB transaction.
7. **Cache Update**: Add bid to Redis sorted set for session; update lowest bid cache.
8. **WebSocket Broadcast**: Emit `NEW_BID` event to all session participants; emit `BID_LEADER_UPDATED` if this bid is now the lowest.
9. **Idempotency Finalize**: Cache successful response for 24 hours; record metrics.

Kafka Event payloads:
```json
BID_PLACED:
    {
        "bid_id": "UUID",
        "session_id": "UUID",
        "driver_id": "UUID",
        "amount": 450.0
    }
```

```json
AUTO_ACCEPT_REQUESTED:
    {
        "session_id": "UUID",
        "passenger_id": "UUID",
        "bid_id": "UUID"
    }
```

Websocket payloads:
```json
NEW_BID:
    {
        "bid_id": "UUID",
        "session_id": "UUID",
        "driver_id": "UUID",
        "amount": 450.0
    }
```

```json
BID_LEADER_UPDATED:
    {
        "bid_id": "UUID",
        "session_id": "UUID",
        "driver_id": "UUID",
        "amount": 450.0
    }
```


## Accept Bid
```python
class AcceptBidRequest(BaseModel):
    bid_id: UUID
```

Routes to be used:
```
1. POST /sessions/{session_id}/accept
```

Flow:

1. **Idempotency & Lock**: Check cached response; acquire Redis lock on session (30s TTL) to prevent concurrent accepts.
2. **Validation**: Fetch session and bid; ensure session is OPEN, bid belongs to session, and bid is ACTIVE.
3. **State Transition**: Close session (CLOSED), accept bid (ACCEPTED), record `accepted_at`.
4. **Atomic Persistence**: Update session status, bid status, and persist BID_ACCEPTED outbox event in single DB transaction.
5. **WebSocket Broadcast**: Emit `BID_ACCEPTED` and `SESSION_CLOSED` to all session participants.
6. **Driver Notification**: Trigger webhook to notify winning driver.
7. **Finalize**: Cache response for 24h; release Redis lock.

Kafka Event payloads:
```json
BID_ACCEPTED:
    {
        "session_id": "UUID",
        "bid_id": "UUID",
        "ride_id": "UUID"
    }
```

Websocket payloads:
```json
BID_ACCEPTED:
    {
        "session_id": "UUID",
        "bid_id": "UUID",
        "ride_id": "UUID"
    }
```

```json
SESSION_CLOSED:
    {
        "session_id": "UUID",
        "bid_id": "UUID",
        "ride_id": "UUID"
    }
```


## Withdraw Bid
```python
# Note: bid_id and session_id are URL path parameters
# No request body required
```

Routes to be used:
```
1. POST /sessions/{session_id}/bids/{bid_id}/withdraw
```

Flow:

1. **Validation**: Fetch session (must be OPEN) and bid (must belong to requesting driver and be ACTIVE).
2. **State Transition**: Mark bid as WITHDRAWN, record `withdrawn_at`.
3. **Atomic Persistence**: Update bid status and persist BID_WITHDRAWN outbox event.
4. **Cache Update**: Remove bid from Redis sorted set for session.
5. **WebSocket Broadcast**: Emit `BID_WITHDRAWN` to all session participants.
6. **Leader Recalculation**: Fetch new lowest bid from Redis; if exists, emit `BID_LEADER_UPDATED` with new leader details.
7. **Logging**: Record withdrawal event; return updated bid details.

Kafka Event payloads:
```json
BID_WITHDRAWN:
    {
        "bid_id": "UUID",
        "session_id": "UUID",
        "driver_id": "UUID"
    }
```

Websocket payloads:
```json
BID_WITHDRAWN:
    {
        "bid_id": "UUID",
        "session_id": "UUID",
        "driver_id": "UUID"
    }
```

```json
BID_LEADER_UPDATED:
    {
        "bid_id": "UUID",
        "session_id": "UUID",
        "driver_id": "UUID",
        "amount": 400.0
    }
```


## Get Session Bids
```python
# No request body - session_id is URL path parameter
```

Routes to be used:
```
1. GET /sessions/{session_id}
```

Flow:

1. **Session Retrieval**: Fetch bidding session by ID; raise 404 if not found.
2. **Fetch Bids**: Query repository for all bids associated with session.
3. **Cache Lookup**: Retrieve current lowest bid amount from Redis sorted set for session.
4. **Counter-Offers**: Query repository for all ACTIVE counter-offers for session.
5. **Response Construction**: Compile session details, bids, counter-offers, and lowest bid into unified `ItemBidsResponse`.

No Kafka events (read-only operation).

No WebSocket events (read-only operation).

Response includes:
- Session metadata (id, status, timestamps, baseline_price if HYBRID)
- List of all bids with full details
- Current lowest bid amount
- List of active counter-offers (for HYBRID mode)


## Passenger Counter Offer
```python
class PassengerCounterOfferRequest(BaseModel):
    counter_price: float = Field(..., gt=0, description="Passenger's counter price must be positive")
    counter_eta_minutes: int | None = Field(None, gt=0, description="Counter ETA in minutes")
```

Routes to be used:
```
1. POST /sessions/{session_id}/passenger-counter
```

Flow:

1. **Session Validation**: Fetch session; ensure OPEN and belongs to requesting passenger.
2. **Bid Creation**: Create placeholder Bid object with driver_id=0 (system placeholder), status=ACTIVE, message="Passenger counter-offer".
3. **Counter-Offer Creation**: Create CounterOffer domain object linking to bid, with PENDING status.
4. **Persistence**: Save bid and counter-offer via respective repositories.
5. **WebSocket Broadcast**: Emit `PASSENGER_COUNTER_BID` event to all drivers in session with price, ETA, bid_id.
6. **Outbox Event**: Persist COUNTER_OFFER_CREATED event to bid_events table for Kafka publishing.
7. **Logging & Response**: Record passenger counter-offer; return bid details.

Kafka Event payloads:
```json
COUNTER_OFFER_CREATED:
    {
        "session_id": "UUID",
        "bid_id": "UUID",
        "counter_offer_id": "UUID",
        "passenger_id": "UUID",
        "price": 380.0,
        "eta_minutes": 25
    }
```

Websocket payloads:
```json
PASSENGER_COUNTER_BID:
    {
        "session_id": "UUID",
        "passenger_id": "UUID",
        "bid_id": "UUID",
        "counter_price": 380.0,
        "counter_eta_minutes": 25,
        "event": "passenger_counter_bid"
    }
```


## Driver Accept Counter Offer
```python
class DriverAcceptCounterRequest(BaseModel):
    counter_offer_id: UUID
```

Routes to be used:
```
1. POST /sessions/{session_id}/counter/{counter_offer_id}/accept
```

Flow:

1. **Redis Lock**: Acquire distributed lock on session (30s TTL) to prevent race conditions; raise 409 if locked.
2. **Session Validation**: Fetch session; ensure OPEN.
3. **Counter-Offer Validation**: Fetch counter-offer by ID; ensure PENDING status and belongs to session.
4. **Bid Creation**: Create actual Bid object with driver_id, counter_price, counter_ETA; status=ACTIVE.
5. **State Updates**: Mark counter-offer as ACCEPTED, session as CLOSED, bid as ACCEPTED.
6. **Atomic Persistence**: Update all entities and persist BID_ACCEPTED outbox event in single DB transaction.
7. **WebSocket Broadcast**: Emit `BID_ACCEPTED` and `SESSION_CLOSED` to all session participants.
8. **Kafka Event**: BID_ACCEPTED published via outbox processor triggers ride assignment.
9. **Cleanup**: Release Redis lock.

Kafka Event payloads:
```json
BID_ACCEPTED:
    {
        "session_id": "UUID",
        "bid_id": "UUID",
        "driver_id": "UUID",
        "ride_id": "UUID"
    }
```

```json
COUNTER_OFFER_RESPONDED:
    {
        "session_id": "UUID",
        "bid_id": "UUID",
        "counter_offer_id": "UUID",
        "driver_id": "UUID",
        "status": "ACCEPTED"
    }
```

Websocket payloads:
```json
BID_ACCEPTED:
    {
        "bid_id": "UUID",
        "session_id": "UUID",
        "driver_id": "UUID"
    }
```

```json
SESSION_CLOSED:
    {
        "session_id": "UUID",
        "bid_id": "UUID",
        "driver_id": "UUID"
    }
```


## Get Counter Offers for Session
```python
# No request body - session_id is URL path parameter
```

Routes to be used:
```
1. GET /sessions/{session_id}/counter-offers
```

Flow:

1. **Query Counter-Offers**: Fetch all counter-offers (all statuses) for session from repository.
2. **Domain Conversion**: Convert ORM objects to domain CounterOffer objects.
3. **Response Construction**: Build CounterOfferResponse list with full details including bid_id links.

No Kafka events (read-only).

No WebSocket events (read-only).

Response: Array of counter-offer objects with full details (id, price, ETA, user/driver IDs, bid_id, status, timestamps).


---

# Database Models (Domain Layer)

## Bid
```python
@dataclass
class Bid:
    id: UUID
    service_request_id: UUID
    bidding_session_id: UUID
    driver_id: UUID
    bid_amount: float
    currency: str
    status: BidStatus
    driver_vehicle_id: UUID | None = None
    eta_minutes: int | None = None
    message: str | None = None
    expires_at: datetime | None = None
    placed_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @classmethod
    def create(cls, service_request_id, bidding_session_id, driver_id, bid_amount, currency="PKR", ...)
    def withdraw(self)
    def accept(self)
    def reject(self)
    def mark_outbid(self)
    def expire(self)
```

## BiddingSession
```python
@dataclass
class BiddingSession:
    id: UUID
    service_request_id: UUID
    status: BiddingSessionStatus
    opened_at: datetime
    expires_at: datetime | None = None
    closed_at: datetime | None = None
    max_bids_allowed: int | None = None
    min_driver_rating: float | None = None
    baseline_price: float | None = None

    @classmethod
    def create(cls, service_request_id, expires_at=None, max_bids_allowed=None, min_driver_rating=None)
    def close(self)
    def expire(self)
```

## CounterOffer
```python
@dataclass
class CounterOffer:
    id: UUID
    session_id: UUID
    price: float
    eta_minutes: int | None = None
    user_id: UUID | None = None
    driver_id: UUID | None = None
    bid_id: UUID | None = None
    status: CounterOfferStatus = CounterOfferStatus.PENDING
    responded_at: datetime | None = None
    reason: str | None = None

    @classmethod
    def create(cls, session_id, price, eta_minutes=None, user_id=None, driver_id=None, bid_id=None)
    def accept(self)
    def reject(self)
    def expire(self)
```


# Enums

## BiddingSessionStatus
```python
class BiddingSessionStatus(enum.Enum):
    OPEN = "OPEN"
    CLOSED = "CLOSED"
    EXPIRED = "EXPIRED"
    PAUSED = "PAUSED"
```

## BidStatus
```python
class BidStatus(enum.Enum):
    ACTIVE = "ACTIVE"
    OUTBID = "OUTBID"
    WITHDRAWN = "WITHDRAWN"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"
    EXPIRED = "EXPIRED"
```

## CounterOfferStatus
```python
class CounterOfferStatus(enum.Enum):
    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"
    EXPIRED = "EXPIRED"
```

## BidEventType
```python
class BidEventType(enum.Enum):
    BID_PLACED = "BID_PLACED"
    AUTO_ACCEPT_REQUESTED = "AUTO_ACCEPT_REQUESTED"
    BID_UPDATED = "BID_UPDATED"
    BID_WITHDRAWN = "BID_WITHDRAWN"
    BID_ACCEPTED = "BID_ACCEPTED"
    BID_REJECTED = "BID_REJECTED"
    COUNTER_OFFER_CREATED = "COUNTER_OFFER_CREATED"
    COUNTER_OFFER_RESPONDED = "COUNTER_OFFER_RESPONDED"
```

## BiddingEvent (WebSocket)
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


# Routes Summary

### Bidding Service Routes

| Method | URL | Description |
|--------|-----|-------------|
| POST | `/sessions/{session_id}/bids` | Submit a bid for a bidding session (BID_BASED or HYBRID modes) |
| POST | `/sessions/{session_id}/accept` | Accept a bid as passenger (BID_BASED mode) |
| GET | `/sessions/{session_id}` | Get all bids and counter-offers for a bidding session |
| POST | `/sessions/{session_id}/bids/{bid_id}/withdraw` | Withdraw a previously submitted bid |
| POST | `/sessions/{session_id}/passenger-counter` | Submit a counter-offer as passenger (HYBRID mode) |
| POST | `/sessions/{session_id}/counter/{counter_offer_id}/accept` | Accept a passenger counter-offer as driver (HYBRID mode) |
| GET | `/sessions/{session_id}/counter-offers` | List all counter-offers for a bidding session |
| WS | `/ws/drivers` | WebSocket endpoint for driver real-time updates |
| WS | `/ws/passengers` | WebSocket endpoint for passenger real-time updates |

### Ride Service Routes (referenced)

| Method | URL | Description |
|--------|-----|-------------|
| POST | `/rides` | Create a new ride (FIXED, BID_BASED, or HYBRID pricing) |
| POST | `/rides/{ride_id}/accept` | Accept a FIXED-price ride as driver |

**Note**: `/rides/{ride_id}/accept` only works for FIXED pricing mode. BID_BASED and HYBRID rides must be accepted through the Bidding Service endpoints.

---

# Infrastructure Components

## 1. WebSocketManager

Manages real-time WebSocket connections for drivers and passengers, broadcasting bidding events to all session participants.

### Purpose

Provides low-latency updates for bid placement, acceptance, withdrawal, and counter-offers without requiring clients to poll.

### Key Methods

- `connect_driver(websocket, driver_id)` / `connect_passenger(websocket, passenger_id)`: Accept WebSocket connection and register in connection maps.
- `subscribe_to_session(websocket, session_id)`: Add a connection to the set of listeners for a specific bidding session.
- `broadcast_to_session(session_id, event, payload)`: Send JSON message to all connections watching a session (drivers + passengers).
- `send_to_driver(driver_id, event, payload)` / `send_to_passenger(...)`: Targeted messages to specific user.
- `disconnect_*`: Clean up connection maps and session subscriptions on disconnect.

### Design Decisions

- **In-memory connection state**: No persistence - connections are ephemeral. Reconnect on client side if dropped.
- **Session-based broadcasting**: Uses session_id as key to fan-out to all interested parties efficiently.
- **Stale connection cleanup**: Failed sends automatically remove the connection from all tracking.
- **Per-user connection sets**: Supports multiple tabs/devices per user (multiple WebSockets per user_id).

---

## 2. Bidding ORM Models

SQLAlchemy models in the `bidding` schema covering sessions, bids, counter-offers, events, and status history.

### Models

- **RideBiddingSessionORM**: Tracks bidding session state (OPEN/CLOSED/EXPIRED/PAUSED). One session per ride. Enforces max_bids, min_rating, baseline_price for HYBRID.
- **RideBidORM**: Individual bids with amount, driver, ETA, status (ACTIVE/OUTBID/WITHDRAWN/ACCEPTED/REJECTED/EXPIRED). Unique constraint: (service_request_id, driver_id).
- **RideBidCounterOfferORM**: Passenger ↔ driver negotiation records with price, ETA, status (PENDING/ACCEPTED/REJECTED/EXPIRED).
- **RideBidStatusHistoryORM**: Audit trail of every status change (who changed it, old/new status, reason).
- **RideBidAcceptanceORM**: Immutable record of final bid acceptance (who accepted, final_price, when). Separated from bid status for auditability.
- **RideBidEventORM**: Outbox pattern table for reliable event publishing to Kafka/websockets.

### Design Decisions

- **Multiple schema (`bidding`)**: Isolates bidding tables from other service schemas.
- **Status history table**: Full audit trail for compliance and debugging, not just latest state.
- **Separate acceptance table**: Immutable record of who accepted what and when, distinct from mutable bid status.
- **Event outbox**: `bid_events` table ensures reliable delivery even if publisher crashes mid-transaction.
- **Unique bid constraint**: One active bid per driver per session prevents duplicate bids.

---

## 3. Bidding Repositories

Concrete repository implementations extending `BaseRepository` with bidding-specific queries.

### Repositories

- **BidRepository**: 
  - `find_by_session` (ordered by amount asc for lowest-bid queries)
  - `find_lowest_by_session` with status filter
  - `mark_outbid_transactional` - atomic update of higher bids to OUTBID status
  - `save_outbox_event` - creates RideBidEventORM for async publishing
  - Domain mapping with `_to_domain()`
- **BiddingSessionRepository**: CRUD + `find_active_sessions` for background cleanup.
- **CounterOfferRepository**: Active offer queries, acceptance workflow with status transition.

### Design Decisions

- **Transactional mark_outbid**: Uses single SQL UPDATE with compound WHERE clause (amount > new_lowest OR tie-breaker) for atomicity.
- **Outbox pattern**: Events saved in same DB transaction as bid state changes - guarantees eventual consistency.
- **Session factory pattern**: Repositories receive AsyncSession, keeping them request-scoped and testable.

---

## 4. Bidding Dependencies

FastAPI dependency injection for wiring infrastructure to use cases.

### Components

- **Repository providers**: Session-scoped instances of BidRepo, SessionRepo, CounterOfferRepo.
- **WebSocketManager**: Singleton (app.state) for connection tracking across requests.
- **CacheManager**: Redis client for idempotency keys and lowest-bid caching via sorted sets.
- **EventPublisher**: Kafka publisher from app state.
- **External clients**: `RideServiceClient` (ride validation) and `DriverEligibilityClient` with circuit breakers.

### Design Decisions

- **App state singletons**: WebSocketManager, CacheManager, EventPublisher live for app lifetime.
- **Resilient HTTP clients**: 300ms timeout for ride service, 200ms for eligibility, exponential backoff retry.
- **Circuit breaker**: Opens after 5 consecutive failures, prevents cascade failure.

---

## 5. Bidding Use Cases

Business logic for bid placement, acceptance, withdrawal, and counter-offer negotiation.

### Key Methods

- **PlaceBidUseCase**: 
  - Idempotency key check (Redis) prevents duplicate processing
  - Rate limit (10/min per driver) via Redis
  - Price validation against current lowest (Redis sorted set)
  - Auto-accept if bid <= baseline_min (HYBRID) → creates AUTO_ACCEPT_REQUESTED outbox event
  - Atomic: save bid + mark higher bids OUTBID + events in single transaction
  - Update Redis sorted set, broadcast NEW_BID / BID_LEADER_UPDATED via WebSocket
- **AcceptBidUseCase**: 
  - Redis lock on session (30s TTL) prevents concurrent accepts
  - Validates session OPEN, bid ACTIVE and belongs to session
  - State transition: CLOSE session, ACCEPT bid, create BID_ACCEPTED outbox event
  - Broadcast BID_ACCEPTED + SESSION_CLOSED via WebSocket
  - Driver webhook notification
- **WithdrawBidUseCase**: 
  - Mark bid WITHDRAWN, remove from Redis sorted set
  - Recalculate lowest bid, broadcast new leader if exists
- **PassengerCounterOffer**: 
  - Creates placeholder Bid (driver_id=0) + CounterOffer (PENDING)
  - Broadcast PASSENGER_COUNTER_BID to all drivers
  - Persists COUNTER_OFFER_CREATED outbox event
- **DriverAcceptCounterOffer**: 
  - Redis lock prevents race conditions
  - Creates actual Bid from counter-offer, closes session
  - State: CounterOffer ACCEPTED, Session CLOSED, Bid ACCEPTED
  - BID_ACCEPTED event triggers ride assignment

### Design Decisions

- **Redis for coordination**: Sorted sets for O(1) lowest-bid lookup, atomic increments for idempotency, distributed locks for concurrency control.
- **Outbox pattern**: All state changes include corresponding events in same transaction - no lost updates.
- **WebSocket for real-time**: Sub-millisecond broadcast to session participants vs. polling.
- **Idempotency everywhere**: Every write operation accepts idempotency_key, cached response for 24h.

---

# End-to-end Flow

## 1. Bid Placement (BID_BASED Mode)

1. **Client** → POST `/sessions/{session_id}/bids` with {driver_vehicle_id, bid_amount, eta_minutes, message}
2. **Route** → `place_bid` calls `PlaceBidUseCase.execute()`
3. **Idempotency** → Check Redis for `idempotency_key:{key}` - return cached response if duplicate
4. **Rate Limit** → Redis counter `rate_limit:bid:{driver_id}` - reject if >10/min
5. **Session Validation** → Repository loads session; error if not OPEN
6. **Price Check** → `ZSCORE` on `bids:session:{id}:lowest` in Redis - reject if not lower than current
7. **Auto-Accept Check** → If bid_amount <= baseline_min: prepare AUTO_ACCEPT_REQUESTED outbox event
8. **Atomic Transaction**:
   - INSERT bid record (ACTIVE)
   - UPDATE higher bids → OUTBID (WHERE amount > new OR tie-breaker on created_at)
   - INSERT BID_PLACED (and possibly AUTO_ACCEPT_REQUESTED) into bid_events
9. **Post-Commit**:
   - `ZADD` bid to Redis sorted set
   - `PUBLISH` NEW_BID via WebSocket to session
   - If new lowest: `PUBLISH` BID_LEADER_UPDATED
   - Cache response with idempotency_key (24h TTL)
10. **Kafka** → Outbox processor reads bid_events → publishes BID_PLACED to `bidding-events` topic

## 2. Bid Acceptance

1. **Client** → POST `/sessions/{session_id}/accept` with {bid_id}
2. **Route** → `accept_bid` calls `AcceptBidUseCase.execute()`
3. **Redis Lock** → `SET lock:session:{id} {token} NX PX 30000` - reject 409 if locked
4. **Validation** → Session OPEN, bid ACTIVE, bid belongs to session
5. **Atomic Transaction**:
   - UPDATE session → CLOSED, set closed_at
   - UPDATE bid → ACCEPTED, set accepted_at
   - INSERT BID_ACCEPTED into bid_events
6. **Post-Commit**:
   - `DEL` session from Redis sorted set
   - Broadcast BID_ACCEPTED + SESSION_CLOSED via WebSocket
   - Trigger driver webhook (async)
   - Release Redis lock
7. **Kafka** → Outbox processor publishes BID_ACCEPTED → ride service creates ServiceRequest

## 3. Passenger Counter-Offer

1. **Client** → POST `/sessions/{session_id}/passenger-counter` with {counter_price, counter_eta_minutes}
2. **Route** → Creates placeholder Bid (driver_id=0, status=ACTIVE, message="Passenger counter-offer")
3. **Persist** → CounterOffer (PENDING) linked to placeholder bid
4. **Broadcast** → PASSENGER_COUNTER_BID WebSocket event to all drivers in session
5. **Outbox** → COUNTER_OFFER_CREATED event queued

## 4. Driver Accepts Counter-Offer

1. **Client** → POST `/sessions/{session_id}/counter/{counter_offer_id}/accept`
2. **Redis Lock** → Acquire lock on session
3. **Convert** → Delete placeholder bid, create actual Bid with driver_id, counter_price
4. **Update** → CounterOffer → ACCEPTED, Session → CLOSED, Bid → ACCEPTED
5. **Outbox** → BID_ACCEPTED event (triggers ride assignment via Kafka)
6. **Broadcast** → BID_ACCEPTED + SESSION_CLOSED to all participants

## 5. Bid Withdrawal

1. **Client** → POST `/sessions/{session_id}/bids/{bid_id}/withdraw`
2. **Validation** → Bid ACTIVE, session OPEN, belongs to driver
3. **Update** → Bid → WITHDRAWN, record withdrawn_at
4. **Redis** → `ZREM` from sorted set
5. **Recalc** → Fetch new lowest via `ZRANGE ... LIMIT 1`, broadcast BID_LEADER_UPDATED if exists
6. **Outbox** → BID_WITHDRAWN event

---

# Architectural Roles

- **WebSocketManager**: Maintains real-time connections for bidding participants, broadcasting state changes (NEW_BID, BID_ACCEPTED, etc.) with sub-second latency.
- **Bidding ORM Models**: Define the bidding domain schema (sessions, bids, counter-offers, events) with auditability via status history and immutable acceptance records.
- **Bidding Repositories**: Implement atomic bid operations including outbox event creation, transactional outbid marking, and sorted-set integration for lowest-bid tracking.
- **Bidding Dependencies**: Wire Redis (idempotency, rate limiting, sorted sets), WebSocketManager (real-time), and resilient HTTP clients (ride/driver eligibility) into use cases.
- **Bidding Use Cases**: Orchestrate competitive bidding with distributed locking (Redis), idempotency, auto-accept for HYBRID mode, and counter-offer negotiation flows.

---

# See also

* **CLAUDE.md** — Project overview, service descriptions, dev commands
* **auth-doc.md**, **verification-doc.md**, **ride-doc.md**, **location-doc.md** — Other service documentation
* **`libs/platform/src/sp/infrastructure/messaging/publisher.py`** — EventPublisher for Kafka outbox events
* **`libs/platform/src/sp/infrastructure/cache/manager.py`** — CacheManager for Redis locks and idempotency
* **`services/bidding/bidding/main.py`** — FastAPI app with WebSocket routes and startup tasks