# Ride Repository Runtime Extraction

## Prompt

Finish the runtime repository extraction for `SRideRepository`. The repository currently owns the widest ride lifecycle surface, so extract it separately from the smaller repository families.

## Required Behavior

- Preserve all public `SRideRepository` methods and static request builders.
- Move demo ride behavior and real HTTP ride behavior into separate delegates.
- Keep existing controller/test constructor injection working.
- Preserve demo mode behavior for booking, trips, active ride lifecycle, proofs, verification codes, recent destinations, and nearby drivers.

## Constraints

- Do not change Ride API paths or request payloads.
- Do not change the booking draft builders.
- Do not combine this with UI work.
- Add focused regression tests before moving each lifecycle method group.

## Implementation Status

- Completed. `SRideRepository` now acts as a public facade with demo and HTTP delegates.
- Static booking request builders remain on `SRideRepository`.
- Existing demo ride, trips, route-recovery, and ride tracking tests pass after extraction.
