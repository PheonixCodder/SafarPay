# Driver Foreground Active Ride Runtime Plan

## Summary

Add a driver-only foreground runtime for active rides. Push notifications continue to handle new ride alerts in background and killed-app states. The new runtime handles the separate problem of keeping active trip GPS updates alive after acceptance.

## Implementation

- Add a foreground task dependency and platform declarations for Android foreground location service and iOS best-effort background task support.
- Add a testable `SActiveRideRuntimeController` that starts, restarts, or stops the runtime based on driver id, ride id, and ride status.
- Add `SActiveRideForegroundService` as the plugin-backed implementation.
- Store runtime config in foreground-task storage: driver id, ride id, location service base URL, access token, and ride status.
- On each foreground-service repeat event, read GPS via `geolocator` and POST to `/drivers/{driver_id}/location` with `ride_id`.
- Wire the runtime into `SDriverRequestsController` when active rides are fetched, accepted, started, completed, cleared, or the driver goes offline.
- Initialize foreground-task communication and service options from `main.dart`.

## Lifecycle Rules

- Start for `ACCEPTED`, `DRIVER_ASSIGNED`, `ARRIVING`, `ARRIVED`, and `IN_PROGRESS`.
- Stop for no ride, terminal ride statuses, driver offline, completion, and controller close.
- Do not start if driver id, ride id, location base URL, or access token is missing.
- Stop if the background HTTP location update receives `401` or `403`.

## Verification

- Run `flutter test test/features/drivers/active_ride_runtime_controller_test.dart`.
- Run `flutter analyze` for changed client files.
- Run `flutter pub get` after adding the foreground task dependency.
- Manual Android QA:
  - accept a ride,
  - confirm persistent active ride notification appears,
  - lock/background the phone,
  - confirm passenger live tracking receives driver movement,
  - complete/cancel/offline,
  - confirm notification disappears.

## Notes

- Android provides the reliable foreground-service behavior.
- iOS remains best-effort because the OS restricts long-running background work.
- Idle online drivers should not be continuously background-tracked; new ride requests are handled by push notifications.
