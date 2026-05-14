# Firebase Setup

Firebase generated configuration is intentionally not tracked in Git.

## Why

GitHub secret scanning can flag Firebase API keys in generated client config files. Firebase API keys are generally client identifiers rather than private server secrets, but they should still be restricted in Google Cloud/Firebase and kept out of public repository history going forward.

Ignored generated files:

- `lib/firebase_options.dart`
- `android/app/google-services.json`
- `ios/Runner/GoogleService-Info.plist`
- `macos/Runner/GoogleService-Info.plist`

`firebase.json` remains tracked because it is project configuration and does not contain API keys by itself.

## Local Setup

Run these commands from `client/` after cloning or after Firebase config changes:

```bash
dart pub global activate flutterfire_cli
flutterfire configure
```

Select the SafarPay Firebase project and the supported platforms. The command should regenerate `lib/firebase_options.dart` and platform config files.

## Key Restrictions

In Google Cloud Console, restrict Firebase API keys:

- Web key: allowed HTTP referrers for approved domains.
- Android key: package name and SHA certificate fingerprints.
- iOS/macOS key: allowed bundle IDs.
- API restrictions: only Firebase/Google APIs used by the app.

If a key was already committed to a public repository, rotate or replace it in Google Cloud/Firebase and update local generated config.

## Example File

Use `lib/firebase_options.example.dart` only as a shape reference. Do not copy placeholder values into production builds.
