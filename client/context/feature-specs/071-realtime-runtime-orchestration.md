# Realtime Runtime Orchestration

## Prompt

Centralize the rules that decide when SafarPay connects ride, bidding, location, and communication realtime channels and when driver foreground runtime should start or stop.

## Required Behavior

- HTTP snapshots remain authoritative and load first.
- WebSocket connections attach only when lifecycle state requires them.
- Driver foreground runtime remains active-ride-only.
- Driver request visibility, active ride suppression, and passive recovery after app resume must all derive from shared lifecycle state.

## Constraints

- Do not change backend service ownership.
- Do not merge ride, bidding, location, and communication socket repositories together.
- Keep orchestration decisions above feature-local controller code.

## Implementation Status

- Added shared lifecycle-stage orchestration through `SRideRealtimeOrchestrator`.
- Added app resume recovery through `SAppLifecycleController`.
- Passenger tracking, passenger hybrid matching, driver requests, ride communication, and driver foreground runtime now defer eligibility decisions to the shared orchestrator.
