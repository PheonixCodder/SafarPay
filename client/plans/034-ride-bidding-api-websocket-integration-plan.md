# Ride And Bidding API/WebSocket Integration Plan

## Summary

Connect the map-first passenger booking flow to real backend Ride and Bidding contracts while keeping deterministic demo data available for backend-offline UI testing.

## Implementation

- Add `SAFARPAY_USE_LOCATION_DEMO_DATA` as the single switch for demo-vs-real location flow behavior.
- Restore real HTTP calls in Location, Geospatial, Ride, and Bidding repositories behind the demo switch.
- Expand `SRideRepository` to cover Ride service routes for create, list, fetch, cancel, fixed-driver accept, start, complete, stops, verification codes, proofs, and nearby-driver matching.
- Expand `SBiddingRepository` to cover Bidding service routes for session lookup, session fetch, driver bid placement, passenger bid acceptance, bid withdrawal, passenger counter-offer, driver counter acceptance, and counter-offer listing.
- Add typed Bidding contract models for sessions, bids, and counter-offers.
- Extend shared Ride models with proof upload URL, proof view URL, and nearby-driver responses.
- Add Ride WebSocket event parsing and repository connections for `/ws/passengers` and `/ws/drivers`.
- Add Bidding WebSocket event parsing and repository connections for `/ws/passengers` and `/ws/drivers`, including session subscription payloads.
- Connect the passenger matching controller to real bidding-session lookup, live passenger bidding socket updates, bid acceptance, and passenger counter-offer submission.
- Connect ride tracking to both Location live-location WebSocket and Ride lifecycle WebSocket when demo mode is disabled.

## Verification

- Add parser tests for Ride response and Bidding session contracts.
- Add parser tests for Ride and Bidding WebSocket events.
- Run focused location tests:
  - `flutter test test/location/ride_bidding_contract_models_test.dart test/location/ride_bidding_socket_event_test.dart test/location/ride_repository_test.dart test/location/location_demo_data_test.dart --no-pub`
- Run `flutter analyze --no-pub`.

## Backend Runtime Notes

- Default behavior remains demo mode so the UI can be tested while backend services are unavailable.
- To test against real backend services, run Flutter with:
  - `--dart-define=SAFARPAY_USE_LOCATION_DEMO_DATA=false`
- Real integration requires Auth, Ride, Bidding, Location, Geospatial, and supporting infrastructure to be running.
