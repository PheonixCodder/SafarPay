# 060 - Ride Communication Chat And Calls

## Prompt

After a ride is accepted and before the ride starts, both the passenger and driver need a professional communication entry point from their active ride screens. The screen should let them discuss pickup/destination details, send text messages, send image attachments, send voice notes, and place real in-app voice calls.

The implementation must deeply integrate with `services/communication`, which already owns ride-scoped conversations, messages, media upload registration, WebSocket events, and WebRTC signaling. Conversations are created by backend Kafka events after `service.request.accepted`; the client must fetch the conversation by ride and subscribe to realtime updates.

## Backend Capabilities Found

- Conversations are opened from `service.request.accepted`.
- Conversations are closed from completed/cancelled ride events.
- Supported message types: `TEXT`, `IMAGE`, `VOICE_NOTE`, `SYSTEM`.
- Supported media types: `IMAGE`, `VOICE_NOTE`.
- Supported realtime events: message sent, media message sent, typing, call ringing, call accepted, call ended, WebRTC offer/answer/ICE.
- Supported call flow: create call, relay WebRTC offer/answer/candidates over WebSocket, end call.
- Added missing by-ride lookup route so the mobile app can resolve a ride conversation directly.

## Product Behavior

- Passenger sees a chat button on the Live Ride map while the ride is not `IN_PROGRESS`.
- Driver sees a chat button on the active ride map while the ride is not `IN_PROGRESS`.
- The chat screen retries conversation lookup briefly because Kafka may create the conversation just after ride acceptance.
- The call button starts a real WebRTC audio call.
- Incoming call signaling is handled inside the communication controller and call screen.

## Design Direction

- The chat UI is focused, dense, and ride-specific: appbar, message history, attachment controls, voice note control, and call action.
- The call UI uses a dark focused surface with clear call status, mute, accept/decline, and end-call actions.
- Image and voice-note attachments use the communication service S3 presigned upload flow.
