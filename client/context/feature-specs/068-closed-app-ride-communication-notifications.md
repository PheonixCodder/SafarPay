# Closed-App Ride Communication Notifications

## Prompt

Implement the missing closed-app and background notification path for ride communication so passengers and drivers receive ride chat message notifications and incoming call notifications even when the app is not open.

## Required Behavior

- Ride chat messages must create persisted notification inbox entries and FCM push notifications for the conversation recipient.
- Ride voice call starts must create persisted notification inbox entries and FCM push notifications for the call recipient.
- Communication push payloads must carry enough context to recover the ride conversation from a cold start:
  - `ride_id`
  - `conversation_id`
  - `recipient_id`
  - `sender_user_id`
  - `call_id` for call notifications
- Tapping a ride communication push must open the ride communication flow instead of a generic ride screen.
- Tapping an incoming call push must restore the ringing call state instead of landing on a chat page with no call context.

## Constraints

- Preserve the existing websocket-based in-app chat and WebRTC signaling flow.
- Do not break the accepted-ride communication screen or ongoing active ride notifications.
- Keep notification routing aligned with the existing notification service and FCM pipeline instead of inventing a parallel delivery system.
- Android may use a stronger local presentation for foreground incoming calls; iOS may remain a standard push fallback unless a dedicated CallKit integration is added later.
