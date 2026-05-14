# Branch Split And Merge Plan

## Summary

Split existing work into scoped Git branches and merge them into `master` with normal non-fast-forward merges. Avoid hard resets, force pushes, blanket staging, and accidental commits of excluded files.

## Branches

- `Payments`: backend payment service integration, libs, migrations, and root dependency/config changes.
- `client-scaffold`: Flutter project scaffold and platform folders.
- `client-shared-foundation`: shared Flutter utilities under `client/lib/common`, `client/lib/utils`, and `client/lib/data`.
- `client-auth-setup`: client authentication setup, app wiring, Firebase/Google config, assets, and auth screens.

## Safety Rules

- Create a safety stash before splitting work.
- Restore only explicit paths for each branch.
- Never commit `code.md`, `PAYMENT_SERVICE_FLOW.md`, or `SafarPay.iml`.
- Verify staged files before each commit.
- Merge each branch into `master` one at a time with `--no-ff`.
- Stop and inspect manually if any merge conflict appears.

## Verification

- Use `git status --short --branch` before and after each branch.
- Use `git diff --cached --name-only` before each commit.
- Use `git log --oneline --graph --decorate` after all merges.
- Push branches and `master` normally, without force pushing.

## Outcome

The four branches were created, committed, merged into `master`, and pushed normally.
