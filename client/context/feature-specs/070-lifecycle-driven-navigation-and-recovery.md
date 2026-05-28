# Lifecycle-Driven Navigation And Recovery

## Prompt

Move the remaining ride-entry and recovery behavior onto the shared lifecycle platform so passenger ride opening, notification routing, and ride communication entry stop depending on screen-local branching.

## Required Behavior

- Trips, ride-search acceptance flows, pending matching recovery, and notification taps must all open ride surfaces through shared ride destinations.
- The shared destination layer must support:
  - ride details
  - fixed waiting
  - hybrid offers/matching
  - live ride tracking
  - ride communication
  - driver requests
- Notification routing must stay intent-based and open the same destination surfaces as normal in-app flows.
- Communication entry from ride surfaces must use the same shared destination layer instead of direct screen pushes.

## Constraints

- Keep the existing screen widgets and route transition style.
- Do not break current ride lifecycle behavior while moving route construction out of feature widgets.
- Preserve the split between lifecycle policy decisions and actual widget/screen instantiation.
