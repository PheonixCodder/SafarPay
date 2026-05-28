# Ride Repository Runtime Extraction Plan

## Summary

Extract `SRideRepository` into a public facade plus demo and HTTP delegates while preserving all public APIs.

## Method Groups

1. Ride creation and ride fetch/cancel/list/recent destinations.
2. Driver acceptance and trip lifecycle: accept, start, complete.
3. Stops and verification codes.
4. Proof upload/register/view APIs.
5. Nearby drivers.

## Verification

- Add tests for demo mode behavior for each method group before extraction.
- Keep `ride_repository_test.dart`, trips pending navigation, ride tracking, and active ride runtime tests passing.
- Analyze `ride_repository.dart` after each method group extraction.

## Defaults

- Static request builders stay on `SRideRepository`.
- Public constructor remains `const SRideRepository({bool? useDemoData})`.
- Runtime selection remains based on `SRuntimeModeConfig.useLocationDemoData`.

## Implementation Notes

- Completed. Runtime selection now happens once in the `SRideRepository` constructor.
- Demo lifecycle behavior is isolated in `_DemoRideRepositoryDelegate`.
- Real Ride HTTP behavior is isolated in `_HttpRideRepositoryDelegate`.
- The public facade still owns request-builder static methods and delegates instance methods.
