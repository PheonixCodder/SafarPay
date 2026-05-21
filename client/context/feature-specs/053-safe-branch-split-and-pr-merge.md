# Safe Branch Split And PR Merge Prompt

Analyze the full SafarPay dirty tree and split the completed work into safe, reviewable PR branches. Preserve the current state first, then merge each branch into `master` one by one.

## Source Request

The repository contains a large mixed set of completed client, backend, Docker, migration, documentation, and test changes. The work must be split professionally into feature branches without code loss or corruption.

## Requirements

- Create a local safety snapshot branch before any cleanup or branch switching.
- Split changes by feature and service boundary, not by arbitrary file location.
- Restore only scoped files or hunks from the safety snapshot into each PR branch.
- Push each branch, open a PR, merge it, then update local `master` before starting the next branch.
- Do not stage generated ML model cache files, Python `__pycache__`, or accidental binary deletion artifacts.
- Verify each branch with targeted tests/builds where practical.
- Update branch workflow context and plans inside `client/context` and `client/plans`.

## Intended Branch Groups

- Branch split workflow documentation.
- Auth/profile/Google/OTP backend and client integration.
- Client app mode and driver/passenger navigation.
- Driver vehicle service registration and reuse consent.
- Verification OCR local review harness and runtime fixes.
- Ride/bidding contract alignment.
- Docker, migration, and shared platform hardening.
