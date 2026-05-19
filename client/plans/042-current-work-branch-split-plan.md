# Current Work Branch Split And PR Merge Plan

## Goal

Split the current mixed dirty tree into feature-sized PRs, merge each PR sequentially, and avoid code loss by preserving the full current state in a local safety branch first.

## Safety Snapshot

1. Commit all current tracked and untracked changes to `codex/current-work-safety-snapshot`.
2. Use this branch only as a recovery source.
3. Rebuild each feature branch from the latest merged `main`.

## PR Order

1. `codex/map-first-passenger-booking`
   - Map-first passenger booking UI, map interaction helpers, booking models/catalog, route/vehicle/fare sheet, and focused tests.

2. `codex/ride-bidding-api-sockets`
   - Ride/Bidding repositories, request/response models, socket event parsing, socket repositories, Bidding session lookup by ride, and focused tests.

3. `codex/location-ride-demo-runtime`
   - Centralized demo data and backend-offline runtime responses for Location, Geospatial, Ride, Bidding, and socket repositories.

4. `codex/home-category-booking-entry`
   - Home category tiles and Home search opening Ride Search through the right-slide route with selected category propagation.

5. `codex/help-support-terms`
   - Terms & Conditions page, local typed policy data, detail screen, widgets, and tests.

6. `codex/help-support-faq`
   - FAQ page, local typed FAQ data, category/search interactions, detail screen, widgets, and tests.

7. `codex/help-support-ticket`
   - Something Else ticket form, typed request/response models, demo repository, controller, success screens, widgets, and tests.

8. `codex/help-support-contact`
   - Contact Us page, support phone/email constants, contact widgets, action rows, and tests.

## Branch Execution Steps

For each PR:

1. Start from updated `main`.
2. Create or switch to the target branch.
3. Restore only the feature's files or hunks from `codex/current-work-safety-snapshot`.
4. Add the matching prompt/plan/context entries.
5. Run focused tests and analyzer.
6. Commit with a concise feature message.
7. Push the branch.
8. Open a PR with `gh pr create`.
9. Merge with `gh pr merge --squash --delete-branch`.
10. Update local `main` before continuing.

## Verification Defaults

- Use focused `flutter test ... --no-pub` and focused `flutter analyze ... --no-pub` for client PRs.
- Use `pytest tests/bidding/test_session_lookup.py` for the backend Bidding route PR.
- Attempt `dart format` on touched client files only; if it times out, record it and continue with analyzer/test evidence.

## Notes

- Do not use `git reset --hard` for cleanup.
- Do not stage unrelated files silently.
- Treat `codex/current-work-safety-snapshot` as the source of truth if any feature branch needs reconstruction.
