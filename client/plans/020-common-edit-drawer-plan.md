# Common Edit Drawer Plan

## Objective

Add shadcn-powered reusable edit drawer support and wire it into the personalization profile screen for local value editing.

## Steps

1. Add `shadcn_ui: ^0.54.0` and required Flutter localization setup.
2. Wrap the existing GetX app with shadcn interop while preserving `SAppTheme.lightTheme`.
3. Add a common edit drawer component under `lib/common/widgets/drawers`.
4. Give the drawer a right-side `ShadSheet`, a `ShadInput`, cancel/save actions, and a save callback.
5. Convert `ProfileScreen` to local state for its current demo profile values.
6. Update `SProfileMenu` so rows show a boxed edit icon and call the drawer action.
7. Use keyboard types appropriate to name, email, phone, gender, and date of birth.
8. Save edits into local state only.
9. Update context, plan, and decision docs.
10. Run dependency install, formatting, analyzer, and targeted scans.

## Non-Goals

- No backend persistence.
- No repository or API changes.
- No dedicated select/date picker for gender or date of birth yet.
- No redesign of the profile page beyond the edit icon affordance.

## Verification

- `flutter pub get`.
- Tap each editable profile row and save a new value.
- Confirm dismissing the sheet leaves values unchanged.
- `dart format` on touched Dart files.
- `flutter analyze --no-pub`, or report timeout/tooling failure.
- Source scans for stale `T*`, raw feature `Colors.*`, and multi-widget files.
