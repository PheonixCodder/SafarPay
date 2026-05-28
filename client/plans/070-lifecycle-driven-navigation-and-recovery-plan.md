# Lifecycle-Driven Navigation And Recovery Plan

## Summary

Build a shared ride destination layer on top of the lifecycle policy and migrate ride entry and notification recovery flows onto it.

## Implementation

- Add shared ride destinations that build the correct ride, communication, and driver request surfaces from lifecycle policy or notification intents.
- Centralize legacy pricing hydration for old ride summaries so routing decisions do not stay embedded in the Trips list.
- Move Trips, booking acceptance, pending matching recovery, ride preview completion, ride communication button entry, and notification routing onto the shared destination helpers.

## Verification

- Destination mapping tests for passenger ride surfaces and notification-driven destinations.
- Existing Trips, ride tracking, and notification parsing regressions remain green.
- Analyzer passes on all touched navigation files.

## Defaults

- Shared lifecycle policy chooses *what* surface is needed.
- Shared destination helpers choose *which screen object and route style* present that surface.
