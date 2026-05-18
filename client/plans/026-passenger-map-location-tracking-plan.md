# Passenger Map Location Tracking Plan

## Summary

Implement the passenger map foundation with backend-mediated geocoding/routing and native Mapbox rendering. Keep the client focused on UI, GPS, state, and WebSocket consumption while backend services remain authoritative for Mapbox Geocoding, Directions, Matrix, ride lifecycle, and authorization.

## Key Changes

- Add dependencies: `mapbox_maps_flutter`, `geolocator`, `web_socket_channel`, and `connectivity_plus`.
- Extend `SApiConstants` and `SHttpClient` with service-specific base URL routing while preserving existing auth calls.
- Add typed location domain models and pure parsing tests.
- Add repositories for location, geospatial, ride, bidding, and ride tracking WebSocket entry points.
- Add `SDeviceLocationService` for foreground GPS access.
- Add `SMapView` and map marker models under `lib/common/widgets/maps`.
- Add `RideSearchScreen`, `RidePreviewScreen`, and `RideTrackingScreen`; wire Home search to the new ride search screen.
- Initialize Mapbox token setup in `main.dart` using `MAPBOX_ACCESS_TOKEN` from compile-time environment.

## Test Plan

- Run targeted Flutter tests:
  - `flutter test test/location/location_models_test.dart test/location/live_ride_socket_event_test.dart test/utils/api_constants_test.dart`
- Run analyzer:
  - `flutter analyze`
- Manually verify on Android/iOS after providing a restricted Mapbox public token:
  - Home search opens ride search.
  - Location permission can derive pickup.
  - Dropoff search calls backend geocode.
  - Preview map renders.
  - Tracking screen handles WebSocket updates.

## Assumptions

- Passenger map rendering targets Android/iOS for v1.
- Backend remains responsible for Geocoding, Directions, Matrix, ride creation semantics, and protected service auth.
- Passenger v1 uses foreground location only.
- The current ride confirmation uses a placeholder ride id until ride creation payload details are finalized in a later ride lifecycle unit.
