# Code Standards

## General

- Keep changes scoped to the feature or boundary being modified.
- Read `client/AGENTS.md` and context files before implementing.
- Prefer existing app utilities before adding new helpers.
- Fix root causes instead of layering UI or state workarounds.
- Do not mix unrelated concerns in one commit or implementation unit.
- Keep user-facing strings in `STexts`.
- Keep shared constants in `SColors`, `SSizes`, and other files under `lib/utils/constants`.

## Dart And Flutter

- Use `dart format` on touched Dart files.
- Prefer `const` constructors and widgets where possible.
- Dispose `TextEditingController`, `PageController`, timers, focus nodes, and similar resources.
- Use `StatefulWidget` for local ephemeral UI state and GetX controllers for flow or screen state that must coordinate behavior.
- Do not leave debug `print` calls in committed code.
- Avoid raw `Colors.*` in feature UI; use `SColors`.
- Prefer theme text styles instead of ad hoc `TextStyle` trees.

## GetX

- Use GetX controllers for authentication flow state, OTP timers, permission state, and form submission state where the flow benefits from reactive UI.
- Use `Obx` only around widgets that need to update.
- Use tags when putting multiple instances of the same controller type into the GetX dependency graph.
- Avoid global controller state for screen-local one-off forms unless it is reused across screens.

## Authentication

- Auth API calls belong in `SAuthRepository`.
- Secure token writes belong in `STokenStorage`.
- Auth navigation should use `SAuthNavigation` unless the transition is internal to `AuthFlowScreen`.
- Phone registration, Google verification, Google phone linking, profile completion, and permissions must remain separate steps unless a plan explicitly changes the flow.

## Styling

- Follow `ui-context.md`.
- Use `SSizes` for spacing and dimensions.
- Use `iconsax` where icons are needed.
- Preserve mobile ergonomics: full-width primary buttons, clear form labels, and readable helper text.

## File Organization

- `lib/common/` - reusable widgets and style helpers not owned by one feature.
- `lib/data/` - future shared data providers and DTOs.
- `lib/features/<feature>/controllers/` - GetX controllers and flow state.
- `lib/features/<feature>/models/` - feature-specific data models.
- `lib/features/<feature>/repositories/` - API/repository boundary for a feature.
- `lib/features/<feature>/screens/` - screen widgets and screen-local widgets.
- `lib/features/<feature>/utils/` - feature-specific navigation and helpers.
- `lib/utils/` - app-wide constants, helpers, HTTP, storage, logging, theme, and validators.

## Verification

- Run `dart format` on touched Dart files.
- Run `flutter analyze --no-pub` when Flutter tooling is available.
- If analyzer reports only unrelated existing info-level issues, note that clearly.
- For documentation-only changes, verify expected files exist and `git status --short` shows the intended documentation paths.

## Documentation Traceability

- Every major feature should have a reconstructed prompt in `context/feature-specs`.
- Every major feature should have an implementation plan in `plans`.
- Product, architecture, UI, workflow, and progress docs should stay in sync with code behavior.
- Operational Git plans belong late in the plan sequence, currently `900-*`.
