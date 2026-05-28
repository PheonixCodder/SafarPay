# Android Driver Urgent Ride Alerts

## Prompt

When a passenger creates a new ride and a nearby driver is online, the driver should receive an InDrive-style alert even if the Flutter app is backgrounded or the phone is locked. The foreground requests page keeps the existing WebSocket bottom-sheet popup, but background delivery must use push notifications and Android urgent alert capabilities.

## Requirements

- Treat WebSocket as foreground-only realtime UI.
- Treat FCM push as the background wake/alert path for online drivers.
- Send driver ride jobs with a dedicated `driver_ride_request` notification kind.
- Register device tokens with the current `driver_id` when driver mode goes online.
- Use Android high-priority, max-importance ride alert notifications with short TTL and per-ride collapse keys.
- Route notification taps to the driver requests page and hydrate the ride from backend state.
- Fall back to normal notification behavior when Android full-screen/battery permissions are denied.

## Implementation Status

Implemented initial Android-first path:

- Notification service enriches ride-job metadata with `driver_ride_request`, `driver_id`, `ride_id`, and `present_as_driver_alert`.
- FCM v1 payloads for driver ride requests use high priority, max notification priority, `ride_alerts` channel, short TTL, and per-ride collapse key.
- Flutter background and foreground FCM handlers recognize driver ride requests and show an urgent local notification.
- Driver online flow re-registers the FCM token after driver id resolution so driver-targeted dispatch can find the device token.
