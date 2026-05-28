# Foreground Overlay Suppression (078)

## Prompt

Implement a targeted check inside the foreground notification handler to prevent displaying the native system overlay if the driver requests screen is active. This eliminates duplicate notification overlay and in-app sheet display when the driver is on the Requests screen.

## Requirements

- Add a check using GetX inside `SPushNotificationController`'s foreground messaging handler.
- If `SDriverRequestsController` is registered (indicating the screen is active), suppress the native overlay launch.
- Do not modify or affect background FCM handlers, call notifications, or chat message alerts.
- Keep the code modifications isolated and minimal to prevent regression.
