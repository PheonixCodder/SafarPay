# Safe Branch Split And PR Series Plan

## Plan

1. Inventory all modified and untracked files and identify feature boundaries.
2. Create a full safety preservation point for the current dirty worktree.
3. Exclude oversized local-only artifacts from normal PR branches.
4. Create sequential branches from the current base, restore only each branch's file set from the preserved state, commit, push, open PR, merge, and update local base.
5. Run focused verification for each PR before pushing where feasible.
6. Continue until every tracked code/doc/test change is merged or explicitly left local-only with a reason.

## Branch Sequence

1. `feature/062-ride-lifecycle-backend`
2. `feature/062-location-geospatial-infra`
3. `feature/062-passenger-ride-client`
4. `feature/062-driver-ops-client`
5. `feature/062-communication-chat-calls`
6. `feature/062-docs-config-cleanup`

## Verification

- Backend service branches: focused `uv run pytest` targets for touched services where available.
- Client branches: `flutter analyze` and focused `flutter test` targets.
- Final branch: `git status`, PR status, and merge confirmation.
