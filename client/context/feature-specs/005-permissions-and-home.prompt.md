# Prompt: Permissions And Home

Build post-auth permissions and starter home.

## Prompt

Create a permissions flow that requests location first and notification second, stores completion locally, handles permanently denied permissions by opening app settings, and routes to home once complete. Add a simple starter home screen with a greeting app bar and centered welcome state.

## Target Files

- `lib/features/authentication/controllers/permissions.dart`
- `lib/features/authentication/screens/permissions/**`
- `lib/features/home/screens/home.dart`
- `lib/utils/local_storage/storage.dart`
- `lib/utils/constants/texts.dart`

## Acceptance Criteria

- Location permission is required before notification.
- Completed permissions are stored with `SLocalStorage`.
- Authenticated users with completed permissions go directly home.
- Home uses SafarPay theme tokens and is clearly a placeholder for future ride features.

## Status

- Implemented.
