# Enterprise Client Lifecycle Platform

## Prompt

Analyze the full SafarPay client and move it toward an enterprise lifecycle-driven architecture where ride state, notification routing, communication recovery, and active runtime behavior are coordinated centrally instead of being re-decided inside unrelated screens and controllers.

## Required Behavior

- Passenger ride entry decisions must be derived from one shared lifecycle model instead of duplicated conditionals in Trips, ride tracking, and push routing.
- Driver active-ride state and passenger active-ride state must be publishable to a shared app-level coordinator.
- Push notification deeplink parsing must be centralized and reusable across message types.
- Ride routing must preserve the current product rules:
  - hybrid matching rides open the offers flow
  - fixed rides without a driver open the fixed waiting screen
  - active assigned rides open live ride tracking
  - terminal rides open ride details

## Constraints

- Keep the existing GetX app shell and feature-first folder structure.
- Do not break the current ride lifecycle, communication, or notification flows while extracting the shared policy layer.
- Preserve demo-vs-real repository behavior for now; this phase is about orchestration, not replacing every repository.
- Shared routing logic should live in reusable ride/lifecycle modules rather than being embedded in UI widgets.
