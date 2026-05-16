# Settings User Info Navigation Plan

## Objective

Connect Settings to the personalization profile screen through a reusable right-slide transition while preserving the existing settings and profile designs.

## Steps

1. Add the feature-spec and plan docs for Settings user-info navigation.
2. Add a common transition helper under `lib/common/navigation`.
3. Expose a right-slide `PageRouteBuilder` that slides from the right, fades in slightly, and reverses on pop.
4. Update Settings so one callback opens `ProfileScreen` through the shared transition.
5. Pass the callback to `SSettingsProfileTile.onEdit`.
6. Update `SSettingsList` to accept an optional item tap handler.
7. Route only the `User Info` row to `ProfileScreen`; leave all other settings rows inert.
8. Update context and decision docs.
9. Run targeted source scans, formatting, and analyzer verification where available.

## Non-Goals

- Do not modify authentication profile completion.
- Do not redesign the profile or settings pages.
- Do not add backend persistence or profile-edit forms.
- Do not make other settings rows navigate yet.

## Verification

- Source scan for stale `T*` names.
- Source scan for multi-widget Dart files.
- `dart format` on touched Dart files.
- `flutter analyze --no-pub` from `client/`, or report timeout if tooling hangs.
