# Branch Split And PR Merge Plan

## Summary

Split the current mixed client work into scoped PR branches and merge them into `master` one by one. Preserve the full dirty tree first with a local-only safety snapshot branch, then restore explicit path groups from that snapshot into each PR branch.

## Branches

- `codex/branch-split-plan`: docs-only workflow plan and context updates.
- `codex/passenger-map-client`: passenger Mapbox map rendering, foreground GPS, backend search/route repositories, live ride WebSocket parsing, map widgets, ride search/preview/tracking screens, and related tests.
- `codex/client-settings-ui-foundation`: shared app UI, settings/profile navigation, common widgets, style tokens, utility cleanup, and auth UI polish.
- `codex/settings-content-and-trips`: Settings Privacy Policy, Notifications, Help & Support, Trips history UI, typed ride demo models, and related content/model moves.
- `codex/driver-registration-status-flow`: Settings-launched driver registration entry, category selection, vehicle selection, verification status, demo status states, submit-review CTA, and driver registration docs.
- `codex/driver-registration-step-submissions`: CNIC, license, selfie, and vehicle submission screens, controllers, presigned uploads, realtime selfie capture, upload widgets, validators, and tests.
- `codex/client-screen-structure-normalization`: final screen-folder and widget-file normalization after feature branches have landed.

## Safety Rules

- Create `codex/safety-unsplit-client-work` and commit the complete current client dirty tree before splitting.
- Restore only explicit paths from the safety snapshot for each PR branch.
- Never use `git add -A` for feature PRs unless the staged path list has already been scoped and inspected.
- Verify staged files before each commit.
- Push and merge each PR before starting the next branch.
- Pull latest `master` before creating each new branch.
- Stop and inspect manually if any merge conflict appears.

## Verification

- Use `git status --short --branch --untracked-files=all` before and after each branch.
- Use `git diff --cached --name-only` before each commit.
- Run targeted Flutter tests for the feature branch where available.
- Run `flutter analyze` from `client/` before each feature PR when practical.
- Use `gh pr create`, `gh pr merge`, and normal pushes only; do not force push.

## Execution Order

1. Commit the local safety snapshot.
2. Merge the docs-only workflow PR.
3. Merge passenger map client.
4. Merge settings UI foundation.
5. Merge settings content and trips.
6. Merge driver registration status flow.
7. Merge driver registration step submissions.
8. Merge final screen structure normalization.
