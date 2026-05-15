# Prompt: Client Structure Cleanup

Refactor the SafarPay Flutter client without changing the current visual design, auth setup, navigation behavior, or feature behavior.

## Goal

Clean up the app structure so reusable widgets and constants are easier to maintain before the next ride-feature expansion.

## Requirements

- Read `client/AGENTS.md` and all files in `client/context` before editing code.
- Keep one primary widget class per Dart file where practical.
- Move widgets used across features into `client/lib/common/widgets`.
- Keep screen-specific widgets under the owning screen's `widgets/` folder.
- Move shared models or display data into `client/lib/data` or the owning feature model folder.
- Replace local static spacing, sizes, opacity values, strings, and colors with values from `client/lib/utils` where doing so does not alter the design.
- Use `SColors`, `SOpacities`, `SSizes`, `STexts`, `SImages`, and `SHelperFunctions` consistently.
- Remove obsolete compatibility aliases and stale `T*` names.
- Fix `client/lib/features/personalization/screens/settings/settings.dart` and split its components into focused files.
- Preserve the current home, navigation, authentication, category, notification, search-result, carousel, and settings designs.
- Remove incorrect or unused imports after the refactor.
- Update `client/context`, `client/plans`, and `client/plans/decisions-log.md` to document the cleanup.

## Acceptance Criteria

1. Multi-widget files are split where the widgets are reusable or independently meaningful.
2. Common widgets live under `client/lib/common/widgets`.
3. Settings screen compiles against the current `S*` utilities and no longer references old `T*` names.
4. Reusable styling values are centralized in `client/lib/utils`.
5. No intentional UI or setup behavior changes are introduced.
6. Formatting and analyzer verification are attempted, and any tooling limitations are reported.
