# Map-First Passenger Booking Flow Plan

## Summary

Replace the existing passenger ride search screen with a map-first booking flow. The screen uses a full-screen Mapbox map, a draggable bottom sheet, backend-powered pickup/dropoff search, map-pin location selection, backend route preview, passenger category/vehicle selection, and hybrid offer ride creation.

## Implementation

- Upgrade `SMapView` so it can render full-bleed, hide default status/recenter controls, show a center pin, and expose the current map camera center through `SMapController`.
- Replace `RideSearchScreen` with a `Stack` layout: full-screen map, top map controls, and `DraggableScrollableSheet`.
- Expand `SRideSearchController` into the booking state owner for pickup/dropoff, search target, map-pin selection, category, vehicle, route preview, passenger fare, auto-accept, ride creation, and controlled matching state.
- Add a passenger booking catalog under the Location domain with the five service categories and backend-aligned vehicle/ride payload metadata.
- Generalize `SRideRepository` with a hybrid ride request builder while preserving the existing fixed city ride builder.
- Extend `SBiddingRepository` with passenger counter-offer support for the later live bidding screen.
- Add screen-local ride search widgets for map controls, location bars, category strip, search results, vehicle list, fare offer panel, and the draggable sheet.
- Document the backend contract that non-fixed rides need a `bidding_session_id` from ride creation or passenger WebSocket before true live offer tracking can be enabled.

## Verification

- Add tests for passenger booking catalog category/vehicle behavior.
- Add tests for hybrid ride payload construction.
- Run `flutter analyze`.
- Run `flutter test`.

## Constraints

- Keep direct Mapbox use limited to native map rendering.
- Do not add new external packages unless Flutter's built-in draggable sheet is insufficient.
- Keep grocery visible but blocked from real ride creation until store selection provides backend `store_id`.
- Keep existing `RidePreviewScreen` and `RideTrackingScreen` available for older route paths while the new search screen becomes the primary booking entry.
