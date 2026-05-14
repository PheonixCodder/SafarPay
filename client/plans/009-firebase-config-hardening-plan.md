# Firebase Config Hardening Plan

## Summary

Resolve GitHub secret-scanning alerts for Firebase API keys by stopping Git tracking of generated Firebase client config, adding local setup documentation, and documenting key restriction/rotation requirements.

## Key Changes

- Ignore generated Firebase config files.
- Untrack `client/lib/firebase_options.dart` and `client/android/app/google-services.json` while keeping local working copies.
- Keep `client/firebase.json` tracked.
- Add `client/FIREBASE_SETUP.md`.
- Add `client/lib/firebase_options.example.dart` with placeholder values only.
- Update context, workflow, progress, feature-spec, and decision docs.

## External Security Steps

- Rotate or replace exposed Firebase API keys in Google Cloud/Firebase.
- Apply application restrictions for web, Android, iOS, and macOS keys.
- Apply API restrictions to only the Firebase/Google APIs the app uses.
- Resolve GitHub secret-scanning alerts after rotation/restriction.

## Verification

- `git check-ignore -v client/lib/firebase_options.dart client/android/app/google-services.json`.
- `git ls-files` no longer lists ignored generated Firebase config files.
- Local files remain available for development.
- Fresh clones can follow `FIREBASE_SETUP.md`.

## Status

- Implemented in repo configuration and docs. Console-side key rotation/restriction remains manual.
