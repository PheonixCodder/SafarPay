# Current Work Branch Split Prompt

Analyze all changed code in the repository and split it into safe, reviewable branches. The first branch already exists as `codex/map-first-passenger-booking`.

## Source Request

The current dirty tree contains multiple completed features and backend/client integration work. Identify how many branches should be made, then safely commit, push, open a PR, merge it, and proceed to the next branch without losing or corrupting code.

## Requirements

- Create a safety snapshot before any branch cleanup.
- Use `codex/map-first-passenger-booking` for the first PR.
- Split changes by feature, not by arbitrary file location.
- Avoid code loss by restoring scoped files or hunks from the snapshot branch.
- Do not merge unrelated work into a feature PR.
- Create a plan inside `client/plans`.
- Keep client context updated with the branch split workflow.
- Verify each PR with the most relevant focused tests/analyzer checks before push.

## Intended Branch Groups

- Map-first passenger booking.
- Ride/Bidding API and WebSocket integration.
- Location/Ride/Bidding demo runtime mode.
- Home category booking entry.
- Help & Support Terms & Conditions.
- Help & Support FAQ.
- Help & Support Something Else support ticket.
- Help & Support Contact Us.
