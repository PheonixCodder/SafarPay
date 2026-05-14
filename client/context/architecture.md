# Architecture Context

## Stack

| Layer | Technology | Role |
| --- | --- | --- |
| Framework | Flutter + Dart | Mobile UI and app runtime |
| State | GetX | Controllers, reactive state, and simple navigation coordination |
| Navigation | Flutter Navigator via `SAuthNavigation` and Get context | Auth flow transitions |
| Local preferences | `get_storage` | Lightweight app flags such as permissions completion |
| Secure storage | `flutter_secure_storage` | Access and refresh tokens |
| Auth providers | Phone OTP, Google Sign-In, Firebase Core | Client-side auth entrypoints and platform setup |
| HTTP | `http` through `SHttpClient` | Backend API communication |
| UI assets | Local fonts, images, logos, icons | Branded client experience |
| Documentation | `client/context`, `client/context/feature-specs`, `client/plans` | Source of truth for prompts, plans, decisions, and progress |

## System Boundaries

- `lib/app.dart` - app-level theme and root widget setup.
- `lib/main.dart` - Flutter/Firebase/bootstrap entrypoint.
- `lib/common/` - shared widgets and layout styles that are not feature-specific.
- `lib/data/` - reserved for future data providers, DTOs, and client-side data abstractions.
- `lib/features/authentication/` - onboarding, login, OTP, profile completion, permissions, auth models, repository, and auth navigation helpers.
- `lib/features/home/` - post-auth starter home experience.
- `lib/utils/` - constants, helpers, validation, HTTP, storage, logging, device utilities, and theme.
- `context/feature-specs/` - reconstructed prompts/specs that explain how current feature code should be produced.
- `plans/` - ordered implementation plans and decision history.
- Platform folders (`android/`, `ios/`, `web/`, `linux/`, `macos/`, `windows/`) - Flutter platform scaffolding and generated plugin registration.
- Firebase generated config files are local-only and ignored: `lib/firebase_options.dart`, `android/app/google-services.json`, and Apple `GoogleService-Info.plist` files.

## Auth And Access Model

- `AuthGateScreen` decides whether to show auth flow, permissions, or home based on token presence and current user lookup.
- `SAuthRepository` owns auth API calls and temporary mock behavior while backend integration is incomplete.
- `STokenStorage` owns secure access and refresh token persistence.
- Phone registration uses OTP verification followed by profile completion.
- Google auth verifies a Google ID token. If the backend requires phone linking, the client routes to `GoogleOtpProfileScreen`, then verifies OTP through `OtpScreen` with `SAuthOtpFlow.googlePhoneLink`.
- Permissions are tracked locally using `SPermissionsController` and `SLocalStorage`.
- Current auth is complete for client UI and mocked repository flows. Production backend endpoint activation remains pending.

## Storage Model

- **Secure token storage**: access token and refresh token only.
- **Local app storage**: completion flags such as permissions status.
- **Assets**: logos, onboarding images, icons, and fonts are local files declared in `pubspec.yaml`.
- **Firebase generated config**: generated locally with FlutterFire CLI and not committed. Use `FIREBASE_SETUP.md`.
- **Generated/build output**: `.dart_tool/`, `build/`, platform ephemeral folders, and plugin symlinks are not source of truth.

## Invariants

1. Auth screens must not bypass `SAuthRepository` for backend-facing auth behavior.
2. Auth routes should use `SAuthNavigation` unless they are part of `AuthFlowScreen`'s internal `AnimatedSwitcher`.
3. Tokens must only be persisted through `STokenStorage`.
4. User-facing text belongs in `STexts`.
5. Feature UI should use `SColors`, `SSizes`, app theme classes, and `iconsax` where possible.
6. Generated Flutter platform files should not be manually edited unless the change is required and documented.
7. Empty source folders that must survive Git should contain a `.gitkeep`.
8. Feature changes should update matching feature-spec, plan, progress, and decision docs when they alter behavior.
9. Firebase API keys and platform config files must be generated locally, ignored by Git, and restricted/rotated in Google Cloud/Firebase when exposed.
