# Realtime Runtime Orchestration Plan

## Summary

Move websocket and active-runtime start/stop rules into a shared orchestration layer driven by the lifecycle coordinator.

## Implementation

- Define lifecycle-stage-based subscription rules for ride, bidding, location, and communication sockets.
- Move driver request suppression and active ride recovery decisions out of controller-local heuristics and into the orchestration layer.
- Make resume/reconnect flows rehydrate from HTTP snapshot first, then reattach the required live channels.

## Verification

- Tests for subscription start/stop rules per lifecycle stage.
- Regression tests for driver active ride runtime, passenger live ride tracking, and push-to-recovery flows.
- Manual resume/background scenarios for passenger and driver flows.

## Defaults

- Socket repositories stay separate.
- Orchestration owns *when* they run, not *how* they talk to their backend.

## Implementation Notes

- `SRideRealtimeOrchestrator` now owns lifecycle-stage rules for passenger ride lifecycle sockets, passenger live location sockets, passenger hybrid bidding sockets, ride communication sockets, driver request suppression, and driver foreground runtime.
- `SAppLifecycleController` exposes app resume state so feature controllers can recover from background by refreshing HTTP snapshots before reconnecting live channels.
- Passenger tracking, passenger hybrid matching, driver requests, ride communication, and driver active runtime now call the shared orchestration rules instead of keeping independent status checks.
