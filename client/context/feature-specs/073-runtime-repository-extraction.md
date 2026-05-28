# Runtime Repository Extraction

## Prompt

Complete the repository-level runtime isolation that was intentionally split out of `072`. Demo and real implementations should move behind factories/adapters so feature controllers consume one repository contract without knowing which runtime mode is active.

## Required Behavior

- Preserve the current `SAFARPAY_USE_LOCATION_DEMO_DATA` behavior.
- Keep real backend repositories and socket repositories functionally unchanged.
- Move demo behavior behind explicit demo adapters/factories instead of inline branching inside every method.
- Keep HTTP snapshots authoritative and realtime orchestration unchanged.

## Constraints

- Do not rewrite all ride flows at once.
- Extract one repository family at a time: Location/Geospatial first, Ride second, Bidding third, sockets last.
- Every extraction must have regression tests proving demo and real mode still select the expected implementation.

## Implementation Status

- Completed runtime delegate extraction for Location, Geospatial, Bidding, Ride, and live socket repository families.
- Preserved the public repository APIs and constructor injection hooks.
- Public repositories now select demo/real delegates once through `SRuntimeModeConfig` and expose `runtimeDataSource` for diagnostics and tests.
