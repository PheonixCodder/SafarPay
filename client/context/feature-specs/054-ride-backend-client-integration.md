# Ride Backend Client Integration

## Prompt

Connect the passenger ride booking and HYBRID bidding flow to the real Ride, Bidding, Location, and Geospatial backend services while keeping the existing demo mode available.

## Requirements

- Preserve `SAFARPAY_USE_LOCATION_DEMO_DATA=true` as the offline/demo path.
- When `SAFARPAY_USE_LOCATION_DEMO_DATA=false`, repositories must call real backend HTTP APIs instead of returning fixtures.
- Keep Mapbox usage limited to map rendering; geocoding, reverse geocoding, route preview, pickup validation, and live ride locations remain backend-mediated.
- Ride lifecycle WebSocket, Location tracking WebSocket, and Bidding WebSocket remain separate repositories.
- Bidding WebSocket parsing must support backend `{event, payload}` envelopes.
- Ride WebSocket parsing must support backend ride lifecycle events and `DRIVER_LOCATION_UPDATED`.

## Client Contract

- Ride API service: `SAFARPAY_RIDE_BASE_URL`, default `/api/v1`.
- Bidding API service: `SAFARPAY_BIDDING_BASE_URL`, default `/api/v1/bidding`.
- Location API service: `SAFARPAY_LOCATION_BASE_URL`.
- Geospatial API service: `SAFARPAY_GEOSPATIAL_BASE_URL`.
- Physical-device testing must use laptop LAN URLs rather than localhost or `10.0.2.2`.

## Scope

- In scope: passenger create/list/get/cancel ride, route/geospatial reads, live ride tracking, HYBRID bidding session lookup, counter-offer, bid acceptance, and socket parsing.
- Out of scope: full driver lifecycle UI, proof upload UX expansion, ride OTP UX expansion, and backend ride-domain rule changes.
