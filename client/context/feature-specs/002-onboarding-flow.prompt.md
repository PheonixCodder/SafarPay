# Prompt: Onboarding Flow

Build the SafarPay onboarding experience.

## Prompt

Create a three-page onboarding flow for a ride-hailing app using full-screen background images, dark gradient overlays, centered bottom copy, smooth page indicators, skip behavior, and a final get-started action. Use GetX for page state and transition into the login screen through `SAuthFlowController`, not direct route replacement.

## Target Files

- `lib/features/authentication/controllers/onboarding.dart`
- `lib/features/authentication/controllers/auth_flow.dart`
- `lib/features/authentication/screens/auth_flow/auth_flow.dart`
- `lib/features/authentication/screens/onboarding/**`
- `lib/utils/constants/images.dart`
- `lib/utils/constants/texts.dart`

## Acceptance Criteria

- Three onboarding pages use `ON1.jpg`, `ON2.jpg`, and `ON3.jpg`.
- User can skip to the last page.
- Next advances pages, and final action switches to login.
- Images are precached.
- `PageController` is disposed.

## Status

- Implemented.
