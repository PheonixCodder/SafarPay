# Background Ride Alerts And Active Ride Runtime Plan

## Backend

- Extend notification persistence with `notification.device_tokens`.
- Add authenticated device-token register/unregister endpoints.
- Add FCM push client support controlled by `FCM_SERVER_KEY` and `FCM_SEND_URL`.
- Dispatch driver ride-job webhook pushes through the notification service.
- Keep Kafka notification inbox creation intact and add push fan-out for active tokens.

## Client

- Add Firebase Messaging and local notification packages.
- Initialize background message handling in `main.dart`.
- Register FCM tokens after authenticated user bootstrap and unregister on logout.
- Associate driver devices with current `driver_id` when available.
- Show foreground push messages as local notifications.
- Route tapped push payloads to driver requests or passenger ride tracking.

## Platform

- Add Android notification, background location, and foreground service permissions.
- Add iOS remote-notification and location background mode declarations.
- Keep long-running location work limited to driver active ride use cases.

## Verification

- Compile notification service modules.
- Run focused Flutter analysis after dependency resolution.
- Manually verify FCM credentials and push delivery on real Android/iOS devices after rebuild and migration.
