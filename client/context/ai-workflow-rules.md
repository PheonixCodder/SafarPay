# AI Workflow Rules

## Approach

Build this Flutter client incrementally using a spec-driven workflow. The context files define what the app is, how it is structured, what UI rules apply, and what has already changed. Implement against these files instead of inferring product behavior from scratch.

Before modifying feature code, locate the matching prompt in `context/feature-specs` and plan in `plans`. If none exists, create or update them as part of the same scoped change.

## Scoping Rules

- Work on one feature unit at a time.
- Prefer small, verifiable increments over broad speculative changes.
- Do not combine unrelated UI, auth, platform, generated, and documentation work unless explicitly requested.
- Preserve the user's existing uncommitted changes.
- Do not use destructive Git commands or force pushes unless the user explicitly asks.

## When To Split Work

Split an implementation step if it combines:

- Auth flow changes and unrelated visual redesign.
- Platform-generated file changes and feature UI work.
- Backend contract changes and client-only screen composition.
- Documentation updates and code changes that can be safely delivered separately.
- Multiple unrelated screens or feature folders.
- Feature history reconstruction and actual app behavior changes.
- Reusable-widget extraction and feature behavior changes.

If a change cannot be verified quickly, narrow the scope.

## Handling Missing Requirements

- Do not invent product behavior not defined in context files or the user's request.
- If a requirement is ambiguous, record it in `context/progress-tracker.md` before continuing.
- If the decision affects architecture, scope, storage, security, or auth behavior, update `plans/decisions-log.md`.

## Protected Files

Do not modify these unless the task explicitly requires it:

- `build/`, `.dart_tool/`, platform ephemeral plugin folders, and other generated output.
- Flutter platform generated plugin registrant files.
- Firebase generated config files: `lib/firebase_options.dart`, `android/app/google-services.json`, and Apple `GoogleService-Info.plist` files.
- Root-level files excluded by the user, including `code.md`, `PAYMENT_SERVICE_FLOW.md`, and `SafarPay.iml`.
- Third-party package internals.

## Keeping Docs In Sync

Update the relevant context file whenever implementation changes:

- Product scope or user flows.
- System architecture or feature boundaries.
- Auth, token, permission, or storage behavior.
- UI rules, theme usage, or component conventions.
- Code standards or workflow expectations.
- Widget ownership or file-organization rules.

Update `context/progress-tracker.md` after each meaningful implementation change.
Update the matching `context/feature-specs/*.prompt.md` and `plans/*.md` when a feature changes materially.

## Before Moving To The Next Unit

1. The current unit works within its defined scope.
2. No invariant in `architecture.md` was violated.
3. `context/progress-tracker.md` reflects the completed work.
4. Relevant decisions are captured in `plans/decisions-log.md`.
5. Formatting and analysis have been attempted when code changed.
