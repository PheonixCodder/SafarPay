# Prompt: Flutter Client Scaffold

Build the initial SafarPay Flutter client scaffold inside `client/`.

## Prompt

Create a Flutter app named `client` for the SafarPay ride-hailing product. Include Android, iOS, web, Linux, macOS, and Windows platform scaffolding. Configure `pubspec.yaml` with app assets, SF Pro fonts, Flutter Material support, GetX, GetStorage, HTTP, secure storage, Google Sign-In, Firebase Core, permissions, Iconsax, smooth page indicators, native splash support, and logging utilities. Keep generated build and ephemeral folders out of source control.

## Target Files

- `client/pubspec.yaml`
- `client/main.dart`
- `client/app.dart`
- Platform folders under `client/`
- Asset folders under `client/assets/`

## Acceptance Criteria

- App boots through `main.dart`.
- `GetStorage.init()` and `Firebase.initializeApp()` run before `runApp`.
- `GetMaterialApp` uses the SafarPay light theme.
- Assets and fonts are declared in `pubspec.yaml`.
- Platform scaffold files exist but generated build output is not authoritative.

## Status

- Implemented.
