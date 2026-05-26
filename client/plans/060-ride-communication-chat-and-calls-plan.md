# 060 - Ride Communication Chat And Calls Plan

## Summary

Implement ride-scoped passenger-driver communication after ride acceptance and before trip start. Use the existing communication service for conversations, messages, media, realtime WebSockets, and WebRTC signaling.

## Backend

- Add `GetConversationByRideUseCase`.
- Add `GET /api/v1/communication/conversations/by-ride/{ride_id}` before the generic conversation id route.
- Authorize by passenger user id, driver user id, or driver id.
- Verify communication tests pass.

## Flutter Data Layer

- Add `SApiService.communication` and communication base URL.
- Add dependencies for `flutter_webrtc`, `record`, and `audioplayers`.
- Add communication models, repository, WebSocket repository, and socket event parser.
- Support:
  - conversation lookup by ride
  - message history
  - text send
  - media upload URL
  - S3 PUT upload
  - media message registration
  - media view URL
  - ICE server lookup
  - call start/end
  - WebRTC signaling events

## Flutter UI

- Add `SRideCommunicationButton`.
- Add it to passenger `RideTrackingScreen` when status is not `IN_PROGRESS`.
- Add it to driver `SActiveRideView` when ride is not in progress.
- Add `SRideCommunicationScreen` for chat.
- Add `SRideCallScreen` for real in-app voice call.
- Keep helper widgets in `screens/widgets` with one primary widget per file.

## Verification

- Run communication backend tests.
- Run Flutter analyzer on the communication feature and touched ride screens.
- Manually verify on two phones:
  - accepted ride creates conversation
  - both users can open chat
  - text messages appear live
  - image upload registers and displays
  - voice notes upload and play
  - voice call rings, accepts, connects, mutes, and ends
