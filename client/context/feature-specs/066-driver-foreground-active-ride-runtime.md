# Driver Foreground Active Ride Runtime

## Prompt

Implement the missing background runtime for active driver trips. The app already supports push notifications for new ride requests and active ride alerts, but driver GPS updates currently depend on the foreground Flutter controller. We need a native foreground-service style runtime so accepted and in-progress rides keep sharing driver location when the driver locks the phone or backgrounds the app.

## Product Requirements

- Driver new ride popups remain push/notification driven while the app is backgrounded or killed.
- Driver active ride location must continue only after a ride is accepted and until it is completed, cancelled, the driver goes offline, or the user logs out.
- Passenger background behavior remains push-only; passengers do not need continuous background location tracking.
- The driver must see a persistent active-ride notification while background tracking is running.
- The app must request notification and location permissions before starting the runtime.
- Android should use a foreground service with `location` service type.
- iOS is best-effort and subject to platform background execution limits.

## Use Case Coverage

Full app use cases for this capability:

1. Driver receives a new ride request while on the requests page.
2. Driver receives a new ride request while app is open but on another page.
3. Driver receives a new ride request while app is backgrounded.
4. Driver receives a new ride request while app is killed.
5. Driver taps notification and opens the requests page.
6. Driver active ride GPS continues after screen lock.
7. Driver active ride GPS continues while app is backgrounded.
8. Passenger sees live driver movement after opening active ride tracking.
9. Passenger receives active ride status notification while backgrounded.
10. Passenger taps notification and opens ride tracking.
11. Driver gets persistent active-trip notification while tracking is running.
12. Driver can return to active trip from notification.
13. Communication message/call notifications during an active ride.
14. Logout unregisters device token and stops background runtime.
15. Permissions denied states explain what is unavailable and link to settings.

The previous two background prompts implemented the push-alert layer: device token registration, token cleanup, foreground local notification display, driver ride request push, and notification tap routing. This prompt completes the active-trip GPS runtime gap.

## Success Criteria

- Accepting a fixed ride or receiving an assigned hybrid ride starts the driver foreground runtime.
- Starting a trip keeps the same runtime running with active ride context.
- Completing/cancelling/going offline stops the runtime.
- The runtime posts driver GPS updates to the location service HTTP fallback route with `ride_id`.
- Passenger live tracking can receive updates from those backend writes.
- The implementation is testable without requiring the native foreground service plugin in controller unit tests.
