# Background Ride Alerts And Active Ride Runtime

## Prompt

Implement background-capable ride alerts so drivers can receive new ride request popups/notifications when the app is not on the requests page, and passengers receive active ride updates when their ride is accepted, started, cancelled, or completed.

The system should use WebSockets when the app is foregrounded and push notifications when the app is backgrounded or terminated. Drivers should associate their device push token with both the authenticated user and driver id so new ride request webhooks can target the correct device. Active ride notifications must deep link back into the appropriate ride screen.

## Acceptance Criteria

- Notification service can store active push device tokens per user/device and optional driver id.
- Flutter app requests notification permission and registers its FCM token after authentication.
- Ride job webhooks can trigger push delivery to driver devices.
- Foreground push messages are displayed as local notifications.
- Notification taps route drivers to requests and passengers to active ride tracking.
- Logout unregisters the current push token.
- Existing foreground WebSocket behavior remains unchanged.
