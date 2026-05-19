# Location Demo Data Mode Plan

## Summary

Enable offline UI testing for the passenger map-first booking flow by returning local demo data from Location, Geospatial, Ride, and Bidding repositories while backend services are unavailable.

## Implementation

- Add `lib/features/location/data/demo/location_demo_data.dart` as the single source of temporary booking fixtures.
- Return demo address/live-location data from `SLocationRepository` when `SAFARPAY_USE_LOCATION_DEMO_DATA=true`.
- Return demo route, pickup-validation, and surge data from `SGeospatialRepository` when demo mode is enabled.
- Return fake HYBRID ride create/fetch/cancel responses from `SRideRepository` when demo mode is enabled.
- Return fake HYBRID bidding session, bid accept, passenger-counter, and counter-offer data from `SBiddingRepository` when demo mode is enabled.
- Keep device GPS attempted for pickup, but fall back to demo pickup data when device location is unavailable.

## Verification

- Add demo data tests for geocode, reverse geocode, route preview, ride creation, and hybrid session lookup.
- Run `flutter test test/location/location_demo_data_test.dart`.
- Run `flutter test test/location/ride_repository_test.dart`.
- Run `flutter test test/location/ride_search_screen_compile_test.dart`.
- Run `flutter analyze --no-pub`.

## Restore Path

When backend services are available, run the app with `--dart-define=SAFARPAY_USE_LOCATION_DEMO_DATA=false` to exercise the real repository HTTP and WebSocket paths. Remove demo fixtures later only after backend-driven UI testing is stable.
