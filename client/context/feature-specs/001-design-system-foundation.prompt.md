# Prompt: Design System Foundation

Build the shared SafarPay client design foundation.

## Prompt

Create a light mobile design system for SafarPay with centralized colors, spacing, sizes, images, text constants, theme classes, form field themes, button themes, checkbox/chip/bottom sheet themes, validators, helper utilities, device utilities, logging, local storage, token storage, and an HTTP client wrapper. Use `S*` naming conventions such as `SColors`, `SSizes`, `STexts`, and `SValidator`.

## Target Files

- `lib/utils/constants/*`
- `lib/utils/theme/**`
- `lib/utils/device/utility.dart`
- `lib/utils/helpers/helpers.dart`
- `lib/utils/http/client.dart`
- `lib/utils/local_storage/*`
- `lib/common/**`

## Acceptance Criteria

- Feature UI can avoid raw strings, raw colors, and ad hoc spacing.
- Tokens cover auth, onboarding, profile, permissions, and home.
- Secure tokens use `flutter_secure_storage`.
- Local flags use `get_storage`.

## Status

- Implemented.
