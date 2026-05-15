# Client Structure Cleanup Plan

## Objective

Clean the Flutter client structure without changing the current app design, setup, or user-facing behavior.

## Plan

1. Read `client/AGENTS.md` and current context files to confirm naming, utility, and documentation rules.
2. Scan `client/lib` for files that contain multiple widget classes, stale `T*` references, hard-coded feature UI values, and settings-screen compile risks.
3. Move reusable widgets into `client/lib/common/widgets`:
   - shared image widgets
   - shared container/header widgets
   - shared navigation widgets
4. Split screen-local composite widgets into their owning `widgets/` folders:
   - home category tiles and badges
   - onboarding dot navigation
   - profile terms agreement
   - Google phone-link header and form
5. Rebuild the personalization settings screen using focused components and centralized settings menu data.
6. Move additional static sizes, opacities, strings, and helper color mappings into `client/lib/utils`.
7. Remove obsolete compatibility aliases and stale imports.
8. Update context, feature-spec, progress, and decision documentation.
9. Run formatting, analyzer checks where available, and targeted source scans for regressions.

## Non-Goals

- Do not redesign any screen.
- Do not change authentication, permission, navigation, or data flow behavior.
- Do not modify generated platform files or Firebase generated config.
- Do not remove or overwrite user-created work.

## Verification

- `dart format` on touched Dart files.
- `flutter analyze --no-pub` from `client/` when tooling is available.
- Source scan for multi-widget Dart files.
- Source scan for stale `T*` references and raw feature UI values in touched files.
