# Kafka & WebSocket Event Registry

This document is the runtime event registry for SafarPay. It covers every
Kafka publisher, Kafka consumer, WebSocket endpoint, WebSocket event, and
defined-only event found across the current services.

## Conventions

- Kafka events use the platform `BaseEvent` envelope:

```json
{
  "event_id": "UUID",
  "event_type": "event.name",
  "version": 1,
  "timestamp": "2026-01-01T00:00:00Z",
  "idempotency_key": "UUID",
  "correlation_id": "UUID | null",
  "payload": {}
}
```

- `passenger_user_id` is always an Auth user id.
- `driver_id` is always a Verification driver id.
- `driver_user_id`, when present, is the Auth user id behind a driver profile.
- WebSocket envelopes are service-specific but consistently include an event name and payload/data.

---

# Kafka Topics

## `ride-events`

**Publisher:** Ride service, via `EventPublisher(topic="ride-events")`.

**Consumers:**

| Consumer | Consumed Events | Runtime Effect |
|---|---|---|
| Bidding service | `service.request.created`, `service.request.cancelled` | Opens/cancels bidding sessions for `BID_BASED` and `HYBRID` rides. |
| Geospatial service | `service.request.created` | Finds the best nearby driver and publishes `driver.matching.completed`. |
| Location service | `service.request.accepted`, `service.request.completed`, `service.request.cancelled` | Caches ride participants, changes driver ride status, and clears tracking state. |
| Communication service | `service.request.accepted`, `service.request.completed`, `service.request.cancelled` | Opens or closes ride-scoped conversations. |

### Active Ride Events

| Event Type | Trigger | Important Payload |
|---|---|---|
| `service.request.created` | Passenger creates a ride. | `ride_id`, `passenger_id`, `passenger_user_id`, `service_type`, `category`, `pricing_mode`, `baseline_min_price`, `baseline_max_price`, `auto_accept_driver`, pickup/dropoff coordinates, `vehicle_type`, `matching_radius_km` |
| `service.request.cancelled` | Passenger cancels a ride. | `ride_id`, `passenger_user_id`, `assigned_driver_id`, `driver_id`, `reason` |
| `service.request.accepted` | Fixed ride is accepted by a driver, or ride service assigns a driver from bidding/geospatial. | `ride_id`, `passenger_user_id`, `driver_id`, `pricing_mode`, `final_price` |
| `service.request.started` | Assigned driver starts the ride. | `ride_id` |
| `service.request.completed` | Assigned driver completes the ride. | `ride_id`, `passenger_user_id`, `assigned_driver_id`, `driver_id`, `final_price` |
| `service.stop.arrived` | Driver marks a stop arrived. | `ride_id`, `stop_id` |
| `service.stop.completed` | Driver marks a stop completed. | `ride_id`, `stop_id` |
| `service.verification.generated` | Ride OTP/proof verification code is generated. | `ride_id`, `code_id` |
| `service.verification.verified` | Ride OTP/proof verification code is verified. | `ride_id`, `code_id` |
| `service.proof.uploaded` | Ride proof metadata is registered after S3 upload. | `ride_id`, `proof_id`, `proof_type` |
| `driver.matching.requested` | Ride service manually requests nearby drivers. | `ride_id`, `candidate_count` |
| `driver.matching.completed` | Ride service broadcasts a ride to candidate drivers. | `ride_id`, `dispatched_to` |

### Defined But Not Currently Emitted

| Event Type | Location |
|---|---|
| `service.request.updated` | Platform event registry only. |
| `driver.availability.updated` | Platform event registry only. |

---

## `bidding-events`

**Publisher:** Bidding service outbox worker, via `EventPublisher(topic="bidding-events")`.

**Consumers:**

| Consumer | Consumed Events | Runtime Effect |
|---|---|---|
| Ride service | `BID_ACCEPTED` | Assigns the accepted driver to the ride and republishes `service.request.accepted`. |
| Bidding service | `AUTO_ACCEPT_REQUESTED` | Runs passenger-side bid acceptance internally when auto-accept criteria pass. |

### Active Bidding Events

Bidding stores events in `bidding.bid_events` and republishes the enum value as `event_type`.

| Event Type | Trigger | Important Payload |
|---|---|---|
| `BID_PLACED` | Driver submits first bid in a session. | `bid_id`, `session_id`, `driver_id`, `amount` |
| `BID_UPDATED` | Driver lowers an existing active bid. | `bid_id`, `session_id`, `driver_id`, `amount` |
| `AUTO_ACCEPT_REQUESTED` | Bid is at or below the ride auto-accept threshold. | `session_id`, `passenger_id`, `bid_id` |
| `BID_ACCEPTED` | Passenger accepts a bid, or driver accepts a passenger counter-offer. | `session_id`, `bid_id`, `ride_id`, `passenger_user_id`, `driver_id`, `amount`, optional `counter_offer_id`, optional `pricing_mode` |
| `BID_WITHDRAWN` | Driver withdraws an active bid. | `bid_id`, `session_id`, `driver_id` |
| `COUNTER_OFFER_RESPONDED` | Driver accepts a passenger counter-offer in `HYBRID` mode. | `session_id`, `bid_id`, `counter_offer_id`, `driver_id`, `ride_id`, `passenger_user_id`, `amount`, `pricing_mode` |

### Defined But Not Currently Emitted

| Event Type | Location |
|---|---|
| `BID_REJECTED` | Bidding outbox enum only. |
| `COUNTER_OFFER_CREATED` | Bidding outbox enum only; passenger counters currently broadcast via WebSocket but are not saved to the outbox. |
| `bid.placed`, `bid.accepted` | Local/platform event classes; current outbox emits uppercase enum values. |

---

## `geospatial-events`

**Publisher:** Geospatial service, via `EventPublisher(topic="geospatial-events")`.

**Consumers:**

| Consumer | Consumed Events | Runtime Effect |
|---|---|---|
| Ride service | `driver.matching.completed` | Assigns fixed-price rides to the selected driver; ignores `BID_BASED` and `HYBRID` final assignment. |
| Bidding service | `driver.matching.completed` | Sends bidding opportunities to selected drivers for `BID_BASED` and `HYBRID` rides. |

### Active Geospatial Events

| Event Type | Trigger | Important Payload |
|---|---|---|
| `driver.matching.completed` | Geospatial consumes `service.request.created`, finds a selected driver, and publishes the result. | `ride_id`, `pricing_mode`, `selected_driver.driver_id`, `distance_km`, `estimated_arrival_minutes`, `vehicle_type`, `composite_score`, `h3_cell`, `latitude`, `longitude`, `surge_multiplier`, `matching_duration_ms`, `candidates_evaluated` |

### Defined But Not Currently Emitted

| Event Type | Location |
|---|---|
| `geofence.violation` | Platform event registry only. |

---

## `location-events`

**Publisher:** Location service, via `LocationEventPublisher` wrapping `EventPublisher(topic="location-events")`.

**Consumers:** No in-repo service consumer currently subscribes to `location-events`.

### Active Location Events

| Event Type | Trigger | Important Payload |
|---|---|---|
| `driver.location.updated` | Driver sends a valid GPS ping over HTTP or WebSocket. | `driver_id`, `lat`, `lng`, `speed_kmh`, `heading_degrees`, `accuracy_meters`, `ride_id`, `recorded_at` |
| `driver.status.changed` | Driver goes online/offline, or status is changed through location use cases. | `driver_id`, `status`, `ride_id` |

### Publisher-Supported But Not Currently Emitted

| Event Type | Location |
|---|---|
| `passenger.location.updated` | Implemented in `LocationEventPublisher`, but `UpdatePassengerLocationUseCase` currently stores/history-tracks passenger pings without publishing this event. |

---

## `communication-events`

**Publisher:** Communication service outbox worker, via `EventPublisher(topic="communication-events")`.

**Consumers:** No in-repo service consumer currently subscribes to `communication-events`.

### Active Communication Events

The outbox publishes `communication.{event_type.lower()}`.

| Event Type | Trigger | Important Payload |
|---|---|---|
| `communication.conversation_opened` | `service.request.accepted` opens a ride conversation. | `conversation_id`, `ride_id`, `passenger_user_id`, `driver_id` |
| `communication.conversation_closed` | `service.request.completed` or `service.request.cancelled` closes a ride conversation. | `conversation_id`, `ride_id` |
| `communication.message_sent` | Participant sends a text message. | `conversation_id`, `message_id`, `message_type` |
| `communication.media_message_sent` | Participant attaches uploaded image or voice note media to a message. | `message_id`, `media_id` |
| `communication.call_started` | Participant starts a voice call. | `conversation_id`, `call_id`, `status` |
| `communication.call_updated` | Call status changes, including accepted, ended, missed, rejected, or failed. | `conversation_id`, `call_id`, `status` |

---

## `verification.events`

**Publisher:** Verification service, via `EventPublisher("verification.events")`.

**Consumer:** Verification service background subscriber, registered for `verification.review_requested`.

### Active Verification Events

| Event Type | Trigger | Important Payload | Runtime Effect |
|---|---|---|---|
| `verification.review_requested` | Driver submits verification for review. | `user_id`, `driver_id` | Background handler runs `execute_verification_review`, including OCR/face matching and persistence. |

---

## `notification-events`

**Publisher:** Notification service, via `EventPublisher(topic="notification-events")`.

**Consumers:** No in-repo delivery consumer currently exists.

### Active Notification Events

| Event Type | Trigger | Important Payload |
|---|---|---|
| `notification.requested` | Notification API queues a notification. | `notification_id`, `user_id`, `message`, `channel` |

---

## `bidding-webhook-dlq.v1`

**Publisher:** Bidding webhook client, via `publish_to_topic`.

**Consumers:** No in-repo DLQ processor currently exists.

| Event Type | Trigger | Important Payload |
|---|---|---|
| `webhook.failed` | Driver bidding webhook fails after retry attempts. | `event_type`, `original_payload`, `error`, `retry_count` |

---

## `auth-events`

**Publisher:** Auth service wires `EventPublisher(topic="auth-events")` at startup when Kafka is configured.

**Consumers:** None in repo.

**Current runtime status:** no auth use case currently calls `publish`, so `user.registered` and `user.logged_in` are platform-defined events, not active emitted events.

---

# WebSocket Channels

## Ride Service

Base route prefix: `/api/v1`

### Driver Channel: `/ws/drivers`

Driver authenticates through the WebSocket auth dependency. Client may send plain `ping`; server replies with `{"event":"pong"}`.

| Event | Direction | Payload | Trigger |
|---|---|---|---|
| `NEW_JOB` | Server to driver | `ride_id` plus ride payload | Ride service broadcasts a matched job to candidate drivers. |
| `JOB_CANCELLED` | Server to driver | `ride_id` | Passenger cancels an assigned ride. |
| `JOB_ASSIGNED` | Server to driver | `ride_id` | Driver is assigned through fixed accept, bidding accept, or geospatial assignment. |
| `JOB_UPDATED` | Server to driver | Ride update payload | Defined manager event; no active emission found. |

### Passenger Channel: `/ws/passengers`

Passenger authenticates through the WebSocket auth dependency and can optionally subscribe to a `ride_id`.

| Event | Direction | Payload | Trigger |
|---|---|---|---|
| `RIDE_CREATED` | Server to passenger | `ride_id`, `status` | Passenger creates a ride. |
| `DRIVER_ASSIGNED` | Server to passenger | `ride_id`, `driver_id` | Driver is assigned. |
| `RIDE_STARTED` | Server to passenger | `ride_id` | Driver starts the ride. |
| `RIDE_COMPLETED` | Server to passenger | `ride_id`, `final_price` | Driver completes the ride. |
| `RIDE_CANCELLED` | Server to passenger | `ride_id`, `reason` | Passenger cancels the ride. |
| `STOP_UPDATED` | Server to passenger | `ride_id`, `stop_id`, `action` | Stop added/arrived/completed. |
| `DRIVER_MATCHED` | Server to passenger | Matching payload | Defined manager event; no active emission found. |
| `DRIVER_LOCATION_UPDATED` | Server to passenger | Location payload | Defined for forwarding from location; no active ride-service emission found. |

---

## Bidding Service

Base route prefix: `/api/v1/bidding`

### Driver Channel: `/ws/drivers`

Driver authenticates as a driver and can send:

```json
{"action": "subscribe", "session_id": "UUID"}
```

Drivers can subscribe to open sessions. The service also sends direct driver notifications for bidding opportunities.

### Passenger Channel: `/ws/passengers`

Passenger authenticates as an Auth user and can send:

```json
{"action": "subscribe", "session_id": "UUID"}
```

Passengers can subscribe only to sessions owned by their `passenger_user_id`.

### Outbound Events

| Event | Direction | Payload | Trigger |
|---|---|---|---|
| `NEW_BID` | Server to session or driver | `bid_id`, `session_id`, `driver_id`, `amount`, or opportunity payload | Driver places/updates a bid, or bidding opportunity is sent to driver. |
| `BID_LEADER_UPDATED` | Server to session | New lowest bid payload | New lowest bid exists after bid placement or withdrawal. |
| `BID_ACCEPTED` | Server to session | `session_id`, `bid_id`, `ride_id`, `passenger_user_id`, `driver_id`, `amount` | Passenger accepts bid, or driver accepts passenger counter-offer. |
| `BID_WITHDRAWN` | Server to session | `bid_id`, `session_id`, `driver_id` | Driver withdraws a bid. |
| `SESSION_CLOSED` | Server to session | Accepted/closed session payload | Bid accepted, counter accepted, or session expires. |
| `SESSION_CANCELLED` | Server to session | `session_id` | Ride cancellation closes the bidding session. |
| `PASSENGER_COUNTER_BID` | Server to session | `session_id`, `passenger_id`, `counter_offer_id`, `counter_price`, `counter_eta_minutes`, `event` | Passenger creates a counter-offer in `HYBRID` mode. |

---

## Location Service

Base route prefix: `/api/v1/location`

### Driver GPS Stream: `/ws/drivers/location`

Driver authenticates as a driver and sends GPS pings:

```json
{
  "lat": 31.52,
  "lng": 74.35,
  "accuracy": 8.5,
  "speed": 42.1,
  "heading": 180,
  "ts": 1714300000000,
  "ride_id": "UUID | optional"
}
```

| Event | Direction | Payload | Trigger |
|---|---|---|---|
| `ping` | Server or client | Empty or heartbeat payload | Idle heartbeat. |
| `pong` | Server or client | Empty or heartbeat payload | Heartbeat response. |
| `error` | Server to driver | `detail` | Invalid message, rate limit, validation failure, or invalid coordinates. |

On disconnect, the driver is marked `OFFLINE`, removed from Redis Geo state, and `driver.status.changed` is published if Kafka is configured.

### Passenger Ride Tracking: `/ws/rides/{ride_id}/track`

Passenger or assigned driver authenticates by query token. Authorization uses cached ride participants from `service.request.accepted`.

| Event | Direction | Payload | Trigger |
|---|---|---|---|
| `DRIVER_LOCATION_UPDATED` | Server to passenger subscribers | `driver_id`, `lat`, `lng`, `heading`, `speed` | Assigned driver sends a valid GPS ping with `ride_id`. |
| `ping` | Server or client | Empty or heartbeat payload | Idle heartbeat. |
| `pong` | Server or client | Empty or heartbeat payload | Heartbeat response. |

### Defined But Not Currently Sent By Manager

`PASSENGER_LOCATION_UPDATED`, `DRIVER_ONLINE`, and `DRIVER_OFFLINE` are constants in the location WebSocket manager but have no active send/broadcast call in the current code.

---

## Communication Service

Base route prefix: `/api/v1/communication`

### Conversation Channel: `/ws`

User authenticates through the WebSocket auth dependency. The service resolves an optional driver profile from the Auth user id so passenger and driver participants remain separate.

Client actions:

| Action | Required Fields | Runtime Effect |
|---|---|---|
| `subscribe` | `conversation_id` | Authorizes participant and subscribes socket to the conversation. |
| `typing_started` | `conversation_id` | Broadcasts typing start to the conversation. |
| `typing_stopped` | `conversation_id` | Broadcasts typing stop to the conversation. |
| `webrtc_offer` | `conversation_id`, `call_id`, `payload` | Persists and relays WebRTC offer. |
| `webrtc_answer` | `conversation_id`, `call_id`, `payload` | Accepts ringing call if needed, persists and relays answer. |
| `webrtc_ice_candidate` | `conversation_id`, `call_id`, `payload` | Persists and relays ICE candidate. |

Outbound events:

| Event | Direction | Payload | Trigger |
|---|---|---|---|
| `SUBSCRIBED` | Server to socket | `conversation_id` | Successful subscription. |
| `CONVERSATION_OPENED` | Server to conversation | `conversation_id`, `ride_id` | Ride accepted opens conversation. |
| `CONVERSATION_CLOSED` | Server to conversation | `conversation_id`, `ride_id` | Ride completed/cancelled closes conversation. |
| `MESSAGE_SENT` | Server to conversation | Message response payload | Text message sent. |
| `MEDIA_MESSAGE_SENT` | Server to conversation | Message payload and `media_id` | Image or voice note is registered as a message. |
| `TYPING_STARTED` | Server to conversation | `conversation_id`, `user_id` | Participant starts typing. |
| `TYPING_STOPPED` | Server to conversation | `conversation_id`, `user_id` | Participant stops typing. |
| `CALL_RINGING` | Server to conversation | Call response, optional `initial_offer` | Participant starts a voice call. |
| `CALL_ACCEPTED` | Server to conversation | Call response | WebRTC answer accepts a ringing call. |
| `CALL_ENDED` | Server to conversation | Call response | Call is ended, missed, rejected, or failed. |
| `WEBRTC_OFFER` | Server to conversation | `call_id`, `sender_participant_id`, `payload` | Offer relayed. |
| `WEBRTC_ANSWER` | Server to conversation | `call_id`, `sender_participant_id`, `payload` | Answer relayed. |
| `WEBRTC_ICE_CANDIDATE` | Server to conversation | `call_id`, `sender_participant_id`, `payload` | ICE candidate relayed. |
| `ERROR` | Server to socket | `detail` | Invalid action order or exception. |

---

# End-to-End Event Flows

## Fixed Price Ride

1. Passenger creates `FIXED` ride.
2. Ride publishes `service.request.created`.
3. Geospatial consumes it and publishes `driver.matching.completed`.
4. Ride consumes `driver.matching.completed`, assigns the selected driver, and publishes `service.request.accepted`.
5. Ride sends `DRIVER_ASSIGNED` to passenger and `JOB_ASSIGNED` to driver.
6. Location consumes `service.request.accepted`, caches participants, and marks driver `ON_RIDE`.
7. Communication consumes `service.request.accepted`, opens a conversation, and publishes `communication.conversation_opened`.

## Bid-Based Ride

1. Passenger creates `BID_BASED` ride.
2. Ride publishes `service.request.created`.
3. Bidding consumes it and opens a bidding session.
4. Geospatial publishes `driver.matching.completed`; bidding consumes it and sends bidding opportunities to selected drivers.
5. Drivers submit bids; bidding broadcasts `NEW_BID` and publishes `BID_PLACED` or `BID_UPDATED` through the outbox.
6. Passenger accepts a bid; bidding publishes `BID_ACCEPTED` and broadcasts `BID_ACCEPTED` plus `SESSION_CLOSED`.
7. Ride consumes `BID_ACCEPTED`, assigns the driver, and publishes `service.request.accepted`.
8. Location and communication react to `service.request.accepted`.

## Hybrid Negotiation Ride

1. Passenger creates `HYBRID` ride with baseline pricing.
2. Bidding opens a session and drivers can bid.
3. Passenger creates a counter-offer; bidding broadcasts `PASSENGER_COUNTER_BID`.
4. First driver to accept the counter wins under the Redis lock.
5. Bidding publishes `COUNTER_OFFER_RESPONDED` and `BID_ACCEPTED`, then broadcasts `BID_ACCEPTED` and `SESSION_CLOSED`.
6. Ride consumes `BID_ACCEPTED`, assigns the driver, and publishes `service.request.accepted`.

## Ride Completion or Cancellation

1. Ride publishes `service.request.completed` or `service.request.cancelled`.
2. Location consumes it, clears ride subscriptions, deletes participant cache, and returns driver to `ONLINE` when a driver id is present.
3. Communication consumes it, closes the conversation, and publishes `communication.conversation_closed`.
4. Bidding consumes cancellation events and sends `SESSION_CANCELLED` when an open bidding session exists.

## Live Location

1. Driver sends GPS over `/api/v1/location/ws/drivers/location`.
2. Location validates, rate-limits, stores Redis state, appends history, and publishes `driver.location.updated`.
3. If `ride_id` is present, location broadcasts `DRIVER_LOCATION_UPDATED` to subscribed ride-tracking passengers.

## Communication Media and Calls

1. Communication opens a conversation after `service.request.accepted`.
2. Text messages broadcast `MESSAGE_SENT` and publish `communication.message_sent`.
3. Image and voice note uploads use S3 presigned URLs, then registration broadcasts `MEDIA_MESSAGE_SENT` and publishes `communication.media_message_sent`.
4. Voice calls use HTTP to start/end calls and WebSocket actions to relay WebRTC offers, answers, and ICE candidates.

---

# Services Without Direct WebSocket/Kafka Consumers

| Service | Current Event Surface |
|---|---|
| Gateway | No direct Kafka publisher/consumer or WebSocket endpoint found. It remains an HTTP gateway concern. |
| Auth | Kafka publisher is wired, but no active publish calls were found. |
| Notification | Publishes `notification.requested`; no in-repo consumer or WebSocket endpoint found. |
