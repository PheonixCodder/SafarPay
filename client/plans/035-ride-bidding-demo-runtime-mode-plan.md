# Ride And Bidding Demo Runtime Mode Plan

## Summary

Make every passenger ride, bidding, location, geospatial, and socket integration usable without backend services by returning deterministic demo data while keeping the real fetch/connect code commented in place for later restoration.

## Implementation

- Expand `lib/features/location/data/demo/location_demo_data.dart` with demo responses for Ride routes, Bidding routes, proof upload flow, nearby drivers, and WebSocket event streams.
- Update `SLocationRepository` and `SGeospatialRepository` to return demo data directly, with real HTTP blocks commented below each return.
- Update `SRideRepository` to return demo data for create, list, fetch, cancel, accept, start, complete, stops, verification codes, proofs, and nearby drivers.
- Update `SBiddingRepository` to return demo data for session fetch, ride-session lookup, place bid, accept bid, withdraw bid, passenger counter, counter acceptance, and counter-offer listing.
- Update `SLiveRideSocketRepository`, `SRideSocketRepository`, and `SBiddingSocketRepository` to emit demo stream events and keep real WebSocket connection blocks commented.
- Allow matching and tracking controllers to consume demo socket streams so UI can be tested end to end without running backend services.

## Verification

- Run focused location tests for demo data, ride payloads, contract parsing, socket event parsing, and ride search construction.
- Run `flutter analyze --no-pub`.

## Restore Path

When backend services are available, remove the demo return blocks in the affected repositories and restore the commented `SHttpClient` and `WebSocketChannel` code. Keep the demo fixture file until real-device backend testing is stable.
