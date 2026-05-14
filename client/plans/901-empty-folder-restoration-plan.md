# Empty Folder Restoration Plan

## Summary

Restore intentional empty project folders by adding placeholder `.gitkeep` files. Git does not track empty directories, so placeholders are required for any empty source folder that must survive branch switching, cloning, and merging.

## Key Changes

- Create `restore-empty-folders` from `master`.
- Add `client/lib/data/.gitkeep`.
- Avoid restoring generated or cache directories such as `build/`, `.dart_tool/`, `.gradle/`, `.pytest_cache/`, `.mypy_cache/`, or `.uv-cache/`.
- Do not touch excluded files like `code.md`, `PAYMENT_SERVICE_FLOW.md`, or `SafarPay.iml`.

## Verification

- Confirm only `.gitkeep` is staged.
- Confirm `git ls-files client/lib/data/.gitkeep` returns the path.
- Merge to `master` and push normally.

## Outcome

`client/lib/data/.gitkeep` was added, merged into `master`, and pushed.
