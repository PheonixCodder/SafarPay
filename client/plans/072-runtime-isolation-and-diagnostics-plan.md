# Runtime Isolation And Diagnostics Plan

## Summary

Cleanly separate demo-vs-real runtime selection and add diagnostics to make lifecycle, push, socket, and active-runtime state observable.

## Implementation

- Replace mixed demo/real branches in feature repositories with runtime-selected providers or factories.
- Add diagnostics models and a developer-facing diagnostics surface for lifecycle, push, websocket, and foreground runtime state.
- Use the diagnostics layer to close stale-state and stale-subscription recovery bugs.

## Verification

- Tests for runtime selection boundaries and diagnostics state.
- Regression tests proving demo mode and real mode still preserve current feature behavior.
- Manual diagnostics checks during ride lifecycle transitions.

## Defaults

- Diagnostics are internal tooling for development and QA.
- Runtime isolation should reduce branching in feature repositories, not introduce a second source of truth.

## Implementation Notes

- Completed Phase 4A with `SRuntimeModeConfig` and `SRuntimeDiagnosticsController`.
- Diagnostics now expose app lifecycle state, location runtime mode, active passenger/driver ride lifecycle, realtime channel connection flags, and driver foreground runtime state.
- Full repository implementation extraction is intentionally split into `073-runtime-repository-extraction-plan.md`.
