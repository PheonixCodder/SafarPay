# Safe Branch Split And Sequential PR Merge Plan

## Summary

Split the current dirty tree into seven reviewable branches. Preserve everything first in a safety snapshot, then create and merge PRs one at a time from latest `master`.

## Branches

1. `codex/safe-branch-split-workflow`
   - Adds branch split prompt/plan/context updates only.

2. `codex/auth-profile-google-otp-flow`
   - Auth backend OTP, Google, account merge, demographics, migrations, docs, tests, and matching client auth/profile integration.

3. `codex/client-driver-mode-navigation`
   - Client app mode, driver/passenger navigation switching, settings controls, local storage, and related UI/test updates.

4. `codex/driver-vehicle-service-registration`
   - Verification backend vehicle/service taxonomy plus client driver registration summary, service attach, reuse consent, and related docs/tests.

5. `codex/verification-ocr-local-review`
   - Verification OCR/DeepFace runtime fixes, Docker verification dependency support, local review harness, sample data, and committed fixture assets.

6. `codex/ride-bidding-contract-alignment`
   - Ride and bidding backend contract updates, docs, and focused tests.

7. `codex/docker-migration-platform-hardening`
   - Remaining Docker, migration idempotency, DB session/config, compose, lockfile, and platform hardening.

## Execution Rules

- Create `codex/full-working-tree-safety-snapshot` and commit the current real source tree first.
- Exclude generated files under `verification_test/model_cache/**` and `verification_test/__pycache__/**`.
- Restore `verification_test/assets/img.png` from `master` unless its deletion is intentionally assigned to a branch.
- Before each commit, inspect `git diff --cached --name-only`.
- Push each branch, open a PR against `master`, squash merge, delete the remote branch, and pull latest `master`.
- Stop immediately on merge conflicts, out-of-scope staged files, or meaningful verification failures.

## Verification

- Auth branch: `uv run pytest tests/auth`, focused Flutter auth tests, and `flutter analyze --no-pub`.
- Driver/verification branches: `uv run pytest tests/verification`, focused Flutter driver registration tests, and local review command when Docker is available.
- Ride/bidding branch: focused ride, bidding, and geospatial tests.
- Infrastructure branch: `docker compose build auth verification migrate` and `docker compose up --force-recreate migrate`.

## Assumptions

- Base branch is `master`.
- PRs are ready to merge, not drafts.
- All merges use squash merge.
- Generated ML weights stay out of git.
