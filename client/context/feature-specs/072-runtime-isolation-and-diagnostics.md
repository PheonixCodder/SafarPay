# Runtime Isolation And Diagnostics

## Prompt

Separate demo-vs-real runtime selection from feature repositories and add diagnostics so lifecycle, push, websocket, and active-runtime state can be inspected and debugged consistently.

## Required Behavior

- Demo and real repositories should be selected through a clear runtime boundary instead of mixed inline branching.
- The app should expose enough diagnostics to inspect active ride lifecycle, current runtime mode, socket state, push registration state, and active foreground runtime state.
- Stale navigation or stale subscription bugs should be traceable through these diagnostics.

## Constraints

- Preserve current demo behavior while introducing cleaner runtime selection boundaries.
- Diagnostics should be app-internal and developer-focused, not a user-facing production surface.

## Implementation Status

- Implemented as Phase 4A: runtime mode config boundary plus diagnostics.
- Added lifecycle, runtime mode, active ride, realtime channel, and foreground runtime diagnostics.
- Repository-by-repository demo extraction was split into `073-runtime-repository-extraction` to keep the change safe.
