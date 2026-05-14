# Prompt: Firebase Config Hardening

Harden Firebase generated configuration handling for the SafarPay Flutter client.

## Prompt

Remove generated Firebase configuration files that contain API keys from Git tracking while preserving them locally for development. Add ignore rules for FlutterFire-generated config files, provide a safe example file with placeholders, and document how developers should regenerate local config with FlutterFire CLI. Update client context, plans, and decisions so future agents do not recommit generated Firebase config.

## Target Files

- `client/.gitignore`
- `client/FIREBASE_SETUP.md`
- `client/lib/firebase_options.example.dart`
- `client/context/**`
- `client/plans/**`

## Acceptance Criteria

- `lib/firebase_options.dart` is ignored and no longer tracked.
- `android/app/google-services.json` is ignored and no longer tracked.
- Apple `GoogleService-Info.plist` files are ignored.
- `firebase.json` remains tracked.
- Developers can regenerate config locally using `FIREBASE_SETUP.md`.
- Decisions log records the security/workflow decision.

## Status

- Implemented as repository hardening work. External key rotation/restriction remains a Firebase/Google Cloud console task.
