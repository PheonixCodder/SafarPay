# Branch Split And PR Merge

## Prompt

Analyze all changed client code in the repository and split it into clean, reviewable Git branches without losing or corrupting any work. The first feature branch should use the already-created local branch name `codex/passenger-map-client`.

For each branch, restore only the code that belongs to that branch, commit it, push it, open a pull request, merge it, then move to the next branch. Create the branch-split prompt under `client/context/feature-specs`, create the execution plan under `client/plans`, and update the client context where needed.

## Requirements

- Preserve all current work before splitting branches.
- Do not use blanket staging for feature PRs after the safety snapshot.
- Keep each PR scoped to one coherent feature or refactor.
- Merge each PR before creating the next branch so later branches build on the latest `master`.
- Use `codex/passenger-map-client` for the passenger map branch.
- Keep generated plugin and dependency changes with the feature that needs them.
- Stop and inspect manually if a conflict, failed validation, or unexpected staged file appears.

## Branch Groups

- Branch split workflow docs.
- Passenger Mapbox, GPS, backend route/search, and live ride tracking client foundation.
- Shared settings/UI/client foundation changes.
- Settings content pages and trips history.
- Driver registration entry, vehicle selection, verification status, demo states, and submit-review CTA.
- Driver registration step submission forms, presigned uploads, realtime selfie capture, and related tests.
- Final client screen-folder and widget-ownership normalization.
