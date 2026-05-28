# Background Alerts Runtime Completion

## Prompt

Complete the missing background notification and active ride runtime behavior across SafarPay. The app should use WebSocket for live in-app updates, FCM push notifications for background or killed-app alerts, and the driver foreground service only for active ride GPS tracking.

## Required Behavior

- Driver receives new ride request alerts while on requests page, elsewhere in the app, backgrounded, or killed.
- Driver taps a ride request notification and lands on the requests page.
- Driver active ride GPS keeps updating after lock/background while the foreground service notification is visible.
- Passenger can open active ride tracking from ride status notifications.
- Communication message and call notifications open ride communication.
- Logout unregisters the FCM token and stops any active driver runtime.
- Permission denial states explain unavailable behavior and provide a settings recovery path.

## Constraints

- Do not store Firebase admin credentials in the Flutter app or tracked repo files.
- Use `FCM_PROJECT_ID` with `FCM_SERVICE_ACCOUNT_JSON_BASE64`, `FCM_SERVICE_ACCOUNT_JSON`, or `FCM_SERVICE_ACCOUNT_FILE`; keep `FCM_SERVER_KEY` only as legacy fallback.
- Keep idle online drivers out of foreground GPS tracking. Waiting drivers receive requests through WebSocket when open and push notifications when backgrounded.
- Android is the reliable foreground-service target; iOS background behavior is best-effort and must be verified on device.
