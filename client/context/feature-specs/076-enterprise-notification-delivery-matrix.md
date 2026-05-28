# 076 Enterprise Notification Delivery Matrix

## Prompt

Implement an enterprise notification strategy for SafarPay that clearly separates server delivery, device alerts, foreground runtime, and Android overlays.

Driver marketplace ride requests must behave like ride-hailing apps: if the app is backgrounded and the driver is online, the driver should receive a high-priority alert and, when Android overlay permission is granted, an overlay card that can bring the driver directly to the requests screen. The overlay must not accept rides or submit bids by itself; backend mutations still happen after the app is opened and hydrated.

Ride communication calls must behave like calling apps: incoming ride calls should use the ride calls notification channel, full-screen intent when allowed, and Android notification actions for Accept and Reject. Accept opens the communication call screen. Reject should end the call from the notification action when the user session is available.

Communication messages should remain normal push/in-app notifications and route to the ride communication screen. Android message notifications should support inline reply when the payload contains `conversation_id`. Passenger ride lifecycle updates, payment, safety, and earnings events should remain push/inbox notifications unless they require an active foreground runtime.

## Scope

- Add Android `SYSTEM_ALERT_WINDOW` support for driver ride request overlays only.
- Add a native overlay service and Flutter method-channel bridge.
- Ask driver users for overlay permission when they go online.
- Add communication call notification actions.
- Add communication message inline reply actions where Android supplies reply input.
- Harden data-only notification routing for communication call/message payloads.
- Mark communication call FCM payloads as high priority on the `ride_calls` channel.
- Keep notification service as the central push/inbox dispatcher.
