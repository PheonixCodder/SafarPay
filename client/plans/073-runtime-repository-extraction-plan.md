# Runtime Repository Extraction Plan

## Summary

Follow up Phase 4A by moving demo-vs-real branching out of repository methods and into runtime-selected providers.

## Implementation

- Add repository factory/provider interfaces for Location, Geospatial, Ride, Bidding, and socket families.
- Extract demo implementations that wrap existing `SLocationDemoData` behavior.
- Keep production implementations focused on HTTP/WebSocket behavior only.
- Migrate controllers to request repositories/sockets through factories instead of manually constructing concrete classes.

## Sequence

1. Location and Geospatial repositories.
2. Ride repository.
3. Bidding repository.
4. Live socket repositories.
5. Controller constructor cleanup.

## Verification

- Unit tests for each factory selecting demo vs real implementation.
- Regression tests for passenger booking, hybrid matching, passenger tracking, and driver request flows in demo mode.
- Existing real-backend HTTP/WebSocket tests must keep passing.

## Defaults

- Keep `SRuntimeModeConfig` as the single runtime flag boundary.
- Keep `SRideRealtimeOrchestrator` as the single lifecycle eligibility boundary.
- Do not remove existing constructor injection hooks; tests still need them.

## Implementation Notes

- Completed for Location, Geospatial, Bidding, Ride, Bidding socket, Ride lifecycle socket, and Live Ride socket repositories.
- Public repository classes now select demo/real delegates once and expose `runtimeDataSource` for diagnostics/tests.
- `SRideRepository` keeps its static request builders on the public facade while lifecycle/network methods delegate to demo or HTTP runtime implementations.
