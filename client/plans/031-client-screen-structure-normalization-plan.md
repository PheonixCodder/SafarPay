# Client Screen Structure Normalization Plan

## Summary

Refactor the Flutter client screen tree into a consistent screen-folder pattern. The work is structural only: no UI redesign, API behavior, controller behavior, or navigation behavior should change.

## Implementation

- Add this feature spec and plan to the client documentation index.
- Update architecture/code standards/progress/decisions docs with the normalized screen-folder rule.
- Move driver registration root screen files into screen folders and split private widgets into screen-local `widgets/` files.
- Move location root screen files into `ride_search`, `ride_preview`, and `ride_tracking` screen folders and split private widgets.
- Move home screen-owned widgets from `home/screens/widgets` into `home/screens/home/widgets`.
- Move personalization content/model files out of screen roots into `data/` or `models/`.
- Split multi-widget trips files into one widget per file.
- Update all imports after moves.

## Verification

- Run a structural scan for `.dart` files directly under `driver_registration/screens`.
- Run a scan for Dart files containing multiple widget classes.
- Run `flutter analyze --no-pub`.
- Run `flutter test`.
- Attempt `dart format` on touched Dart files; report if it times out.

## Constraints

- Keep public screen class names stable.
- Keep the existing `vechicle_info` folder spelling until a separate rename is approved.
- Do not touch generated platform files or unrelated dirty files.
