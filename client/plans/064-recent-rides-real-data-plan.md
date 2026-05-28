# Recent Ride Destinations With Live ETA Plan

## Backend

- Add `GET /api/v1/rides/recent-destinations?limit=5` to the ride service.
- Scope results to the authenticated passenger and completed rides only.
- Return newest unique dropoff destinations with pickup/dropoff stop snapshots and ride metadata.
- Reuse existing ride repository reads and keep live ETA outside the ride service.

## Client

- Add `RecentRideDestinationResponse` and `SRideRepository.listRecentDestinations`.
- Add a shared recent-destinations widget that fetches recent destinations, calculates live ETA through `SGeospatialRepository.calculateRoute`, and hides itself on empty/error states.
- Use the shared widget in the home search container and booking sheet compose content.
- Add `RideSearchScreen.initialDropoff` and controller support so home taps prefill dropoff; booking-sheet taps update the current draft directly.

## Verification

- Backend tests cover completed-only filtering, destination dedupe, route registration, and passenger scoping through existing auth dependency.
- Flutter tests cover model parsing and repository demo parsing.
- Run focused ride service tests and Flutter analyzer/tests for changed client areas.
