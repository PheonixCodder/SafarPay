# Code Standards

## General

- Keep changes scoped to the feature or boundary being modified.
- Read `client/AGENTS.md` and context files before implementing.
- Prefer existing app utilities before adding new helpers.
- Fix root causes instead of layering UI or state workarounds.
- Do not mix unrelated concerns in one commit or implementation unit.
- Keep user-facing strings in `STexts`.
- Keep shared constants in `SColors`, `SSizes`, and other files under `lib/utils/constants`.
- Keep reusable opacity values in `SOpacities` and apply them through `SHelperFunctions.withOpacity`.
- Keep each Dart source file focused on one primary widget class.
- Move widgets shared by multiple screens or features into `lib/common/widgets`.
- Put reusable route transitions under `lib/common/navigation`.
- Read `client/.agents/skills/shadcn-ui-flutter/SKILL.md` before introducing or changing shadcn widgets.

## Dart And Flutter

- Use `dart format` on touched Dart files.
- Prefer `const` constructors and widgets where possible.
- Dispose `TextEditingController`, `PageController`, timers, focus nodes, and similar resources.
- Use `StatefulWidget` for local ephemeral UI state and GetX controllers for flow or screen state that must coordinate behavior.
- Do not leave debug `print` calls in committed code.
- Avoid raw `Colors.*` in feature UI; use `SColors`.
- Avoid local opacity literals in shared widgets; use `SOpacities`.
- New shared widget classes should use the `S` prefix. Do not keep obsolete `T*` compatibility aliases after references have been migrated.
- Prefer theme text styles instead of ad hoc `TextStyle` trees.
- Use shadcn components only for planned shared overlays/forms where they add a clear interaction benefit.

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
- Use declared local assets through `SImages` instead of hard-coded asset paths in widgets.
- Use `STexts` for service category labels and badges.
- Keep long legal/help content in typed mapped content files when a page renders repeated sections.
- Keep repeated demo notification feeds in typed mapped content files until backend notification APIs are connected.
- Keep ride list UI backed by backend-aligned ride DTOs; add UI formatting helpers instead of changing API response models for presentation-only needs.
- Preserve mobile ergonomics: full-width primary buttons, clear form labels, and readable helper text.

## File Organization

- `lib/common/` - reusable widgets and style helpers not owned by one feature.
- `lib/common/navigation/` - reusable Navigator route transitions and helpers.
- `lib/common/widgets/navigation/` - reusable navigation shell pieces.
- `lib/common/widgets/containers/` - reusable decorative and layout containers.
- `lib/common/widgets/images/` - reusable image presentation widgets.
- `lib/common/widgets/drawers/` - reusable drawer/sheet components.
- `lib/data/` - shared DTOs, backend-aligned models, demo records, and future data providers.
- `lib/features/<feature>/controllers/` - GetX controllers and flow state.
- `lib/features/<feature>/models/` - feature-specific data models.
- `lib/features/<feature>/repositories/` - API/repository boundary for a feature.
- `lib/features/<feature>/screens/` - screen widgets and screen-local widgets.
- `lib/features/<feature>/screens/<screen>/widgets/` - focused screen-only widget files.
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
