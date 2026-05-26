# 056 Driver Requests Real-Time Plan

## Summary

Build the driver Requests tab as the real-time marketplace and active-trip surface. Use the light SafarPay operational design direction selected during visual planning.

## Backend

- Add Ride driver endpoints:
  - `GET /api/v1/driver/requests`
  - `GET /api/v1/driver/rides/active`
- Add driver request and active ride response schemas with stops, fares, payment, route summaries, and OTP flags.
- Add Ride repository support for verified driver service-capability filtering.
- Add Geospatial route calculation to the Ride service adapter.
- Permit drivers to resolve a Bidding session by ride id for HYBRID/BID flows.

## Client

- Add driver request models, repository, GPS socket repository, GetX controller, screen, and widgets.
- Replace the Requests placeholder in driver navigation.
- Connect online/offline status to Location, request list to Ride, HYBRID offers to Bidding, and maps to existing `SMapView`.
- Suppress request list/popups during an active ride and switch to active trip map.

## Verification

- Run Python compile checks for Ride/Bidding.
- Run `flutter analyze`.
- Run targeted tests where available.

