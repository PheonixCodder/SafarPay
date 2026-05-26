# Safe Branch Split And PR Series

## Prompt

Analyze the entire dirty repository state, split the current work into professional feature branches, push each branch, open a PR, merge it, and then continue to the next branch without losing or corrupting any code.

## Requirements

- Preserve the full current workspace before splitting.
- Group changes by coherent feature boundaries instead of one giant PR.
- Commit only the files that belong to each branch.
- Push branches to GitHub, open PRs, merge them, and proceed sequentially.
- Keep unmergeable local-only artifacts safe, especially large binaries that cannot be pushed to GitHub.
- Avoid destructive git operations unless every path is backed up and verified.

## Proposed Branch Groups

1. Ride lifecycle backend and service contracts.
2. Location/geospatial place and routing infrastructure.
3. Passenger ride booking, tracking, pending matching, and Trips UX.
4. Driver requests and earnings client/backend support.
5. Ride communication chat/call backend and client UI.
6. Documentation, context, workflow plans, and residual config cleanup.

## Safety Notes

- `services/location/location/maps/pakistan.osm.pbf` is roughly 166 MB and should not be committed to normal GitHub git history.
- The split should use a backup branch/commit or equivalent full-state preservation before any branch reset or path restoration.
