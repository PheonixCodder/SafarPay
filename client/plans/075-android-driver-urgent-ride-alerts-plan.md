# Android Driver Urgent Ride Alerts Plan

## Summary

Implement Android-first background ride request alerts for online drivers. Foreground requests still use WebSocket bottom sheets; background and locked-screen scenarios use high-priority FCM plus local urgent notifications.

## Implementation

- Enrich notification service ride-job dispatch payloads with a stable `driver_ride_request` kind and driver/ride ids.
- Upgrade FCM Android config for driver ride requests with max-priority alert settings, `ride_alerts` channel, short TTL, and per-ride collapse key.
- Update Flutter notification routing so data-only `driver_ride_request` payloads route to driver requests even without a deeplink.
- Show urgent local notifications from both foreground and background FCM handlers for driver ride requests.
- Re-register the current FCM token when the driver goes online so the backend token row includes `driver_id`.

## Verification

- Backend tests for internal ride-job metadata and FCM urgent Android payload.
- Flutter route parsing test for data-only driver ride request payloads.
- Analyzer over touched Flutter notification/navigation/driver files.
- Manual Android validation: foreground bottom sheet, background heads-up/full-screen notification, notification tap opens driver requests, denied permissions fall back to normal notification.
