# 076 Enterprise Notification Delivery Matrix Plan

## Goal

Make notification behavior explicit and production-oriented across push delivery, foreground/background device alerts, Android overlays, and active ride runtime.

## Plan

1. Add Android overlay capability for urgent driver ride requests.
   - Add `SYSTEM_ALERT_WINDOW`.
   - Add a native overlay service with Open and Dismiss actions.
   - Add a Flutter method-channel bridge.
   - Request overlay permission when a driver goes online.

2. Keep ride request overlay behavior bounded.
   - Show overlay only for `driver_ride_request`.
   - Use overlay as an entry point into Driver Requests.
   - Keep accept/offer operations inside Flutter after backend hydration.

3. Add ride call notification actions.
   - Use the `ride_calls` channel.
   - Show full-screen call notifications when allowed.
   - Add Accept and Reject actions.
   - Accept opens the call screen.
   - Reject calls the communication service end-call route.

4. Add ride message notification actions.
   - Keep messages on normal notification delivery.
   - Add Android inline Reply when the payload contains `conversation_id`.
   - Send the reply through the Communication service messages route.

5. Harden notification routing.
   - Route data-only `communication_call` payloads to communication with call mode.
   - Route data-only `communication_message` payloads to communication.
   - Preserve existing passenger ride and driver request routing.

6. Upgrade backend FCM metadata.
   - Keep driver ride requests high priority with short TTL and `ride_alerts`.
   - Mark communication calls high priority with short TTL and `ride_calls`.

7. Verify the behavior.
   - Run notification push-client tests.
   - Run ride navigation policy tests.
   - Run Dart analysis on touched client notification/driver/navigation files.
