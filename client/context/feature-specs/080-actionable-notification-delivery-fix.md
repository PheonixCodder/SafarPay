# Actionable Notification Delivery Fix (080)

## Prompt

Analyze and resolve the push notification delivery failures for incoming calls (driver to passenger) and chat messages (both directions) when the app is in the background or closed.

## Core Issue Analysis

1. **The Native Advantage for Driver Alerts**: 
   - New ride request alerts (`driver_ride_request`) work reliably because they are intercepted and processed **entirely in native Kotlin** (`SafarPayFirebaseMessagingService.kt`). Android allows native services to execute immediately on FCM reception, enabling the overlay to draw or show a native fallback notification.
2. **The Dart Background Limitation**:
   - Chat messages (`communication_message`) and voice calls (`communication_call`) are passed to Dart's background messaging handler.
   - However, modern Android OS heavily restricts background Dart execution when the app is closed/terminated.
3. **The Data-Only Push Trap**:
   - In `push_client.py`, both calls and messages are classified as `actionable_notifications`, causing the backend to **pop the visual `notification` block** and send them as **data-only / silent pushes**.
   - Because silent pushes do not contain a visual `notification` block, the Android OS completely suppresses or drops them if the app is backgrounded or terminated. Thus, the passenger's phone never wakes up or alerts for incoming calls or chat messages.

## Resolution Strategy

Modify the notification backend to retain the visual `"notification"` payload block for calls and messages, while keeping it popped *only* for native-handled `driver_ride_request` pushes. This ensures the OS automatically renders the push alert tray notification, waking up the device and allowing the user to tap it to launch the app and open the chat/call screen.
