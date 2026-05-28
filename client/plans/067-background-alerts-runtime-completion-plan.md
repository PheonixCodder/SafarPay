# Background Alerts Runtime Completion Plan

## Summary

Finish the missing push notification and active ride runtime gaps so ride requests, ride status updates, communication alerts, and active driver GPS tracking behave correctly across foreground, background, and killed app states.

## Implementation

- Persist internal driver ride-job notifications before push fan-out, using idempotency to prevent duplicates.
- Route bidding opportunity webhooks to the notification service instead of verification.
- Register passenger FCM tokens even when no driver profile exists; attach `driver_id` only when available.
- Standardize notification deeplinks for driver requests, driver active rides, passenger ride tracking, and ride communication.
- Expand notification event mapping for bid, ride status, message, and call events.
- Update push tap routing to open the correct Flutter screen for every supported deeplink.
- Update active ride runtime sync so same-ride status changes refresh the foreground service config and persistent notification text.
- Add permission-denied recovery UX for notification, location, background location, and battery optimization states.

## Verification

- Backend tests for ride-job persistence, FCM v1 push dispatch, notification event mapping, and bidding webhook URL wiring.
- Flutter tests for passenger token registration, notification deeplink parsing/routing, and active runtime same-ride status updates.
- Manual Android QA: foreground request popup, background push, killed-app push, tap routing, active ride GPS after screen lock, passenger live tracking, communication notification tap, logout cleanup.

## Defaults

- FCM HTTP v1 with `FCM_SERVICE_ACCOUNT_JSON_BASE64` is the preferred credential path.
- Foreground GPS remains driver-only and active-ride-only.
- Killed-app push delivery is complete only after real-device validation with OEM battery optimization considered.
