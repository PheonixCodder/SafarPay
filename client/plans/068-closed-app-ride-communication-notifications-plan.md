# Closed-App Ride Communication Notifications Plan

## Summary

Complete the missing communication notification path so ride chat messages and incoming voice calls survive app backgrounding and cold starts for both passengers and drivers.

## Implementation

- Enrich communication outbox events at the communication service boundary with explicit ride and recipient metadata instead of emitting anonymous message/call events.
- Keep websocket broadcasting unchanged for live in-app chat/call behavior.
- Add call lookup support so a notification-driven app launch can recover the ringing call offer and rebuild the communication state.
- Extend Flutter push routing so communication notifications open the ride communication screen and incoming call pushes reopen the pending call flow.
- Present incoming ride calls more prominently on Android while preserving the existing generic push behavior as fallback.

## Verification

- Communication use-case tests for text, media, and call event payload enrichment.
- Communication route/use-case tests for retrieving a call by id and recovering the stored offer payload.
- Notification mapping tests proving communication events still resolve to communication deeplinks.
- Flutter tests for communication notification helper parsing and deeplink extraction.

## Defaults

- Persisted notification inbox plus FCM push remains the canonical closed-app delivery path.
- Websocket remains the canonical open-app delivery path.
- Communication call recovery is keyed by `call_id` from the notification payload rather than by scanning all rides for active calls.
