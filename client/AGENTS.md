# AGENTS.md

Guidance for coding agents working inside the SafarPay Flutter client app.

## Application Building Context

Read these files in order before implementing code or making architectural decisions:

1. `context/project-overview.md` - product definition, users, flows, scope, and success criteria
2. `context/architecture.md` - stack, boundaries, auth model, storage model, and invariants
3. `context/ui-context.md` - visual language, colors, typography, layout rules, and component conventions
4. `context/code-standards.md` - Dart, Flutter, GetX, styling, and file organization rules
5. `context/ai-workflow-rules.md` - development workflow, scoping rules, protected files, and verification
6. `context/progress-tracker.md` - current phase, completed work, open questions, and next steps
7. `context/feature-specs/000-client-scaffold.prompt.md` - reconstructed prompt for the Flutter scaffold
8. `context/feature-specs/001-design-system-foundation.prompt.md` - reconstructed prompt for shared UI foundation
9. `context/feature-specs/002-onboarding-flow.prompt.md` - reconstructed prompt for onboarding
10. `context/feature-specs/003-auth-gate-and-login.prompt.md` - reconstructed prompt for auth gate and login
11. `context/feature-specs/004-phone-otp-and-profile.prompt.md` - reconstructed prompt for phone OTP and profile completion
12. `context/feature-specs/005-permissions-and-home.prompt.md` - reconstructed prompt for permissions and home
13. `context/feature-specs/006-google-phone-link.prompt.md` - reconstructed prompt for Google phone linking
14. `context/feature-specs/007-client-context-workflow.prompt.md` - reconstructed prompt for context documentation workflow
15. `context/feature-specs/008-firebase-config-hardening.prompt.md` - reconstructed prompt for Firebase config hardening
16. `plans/000-client-product-and-architecture-plan.md` - canonical client product and architecture plan
17. `plans/001-flutter-scaffold-plan.md` - Flutter scaffold plan
18. `plans/002-design-system-foundation-plan.md` - shared design system plan
19. `plans/003-onboarding-flow-plan.md` - onboarding implementation plan
20. `plans/004-auth-gate-and-login-plan.md` - auth gate and login plan
21. `plans/005-phone-otp-and-profile-plan.md` - phone OTP and profile plan
22. `plans/006-permissions-and-home-plan.md` - permissions and home plan
23. `plans/007-google-phone-link-screen-plan.md` - Google phone-link auth flow plan
24. `plans/008-client-context-documentation-plan.md` - client documentation setup plan
25. `plans/009-firebase-config-hardening-plan.md` - Firebase config hardening plan
26. `plans/900-branch-split-and-merge-plan.md` - Git branch split and merge plan
27. `plans/901-empty-folder-restoration-plan.md` - empty-folder preservation plan
28. `plans/decisions-log.md` - permanent decision record

Update `context/progress-tracker.md` after each meaningful implementation change.

Update `plans/decisions-log.md` when a decision changes architecture, product scope, auth behavior, storage, deployment, security, or workflow behavior.

If implementation changes architecture, scope, standards, or UI rules, update the relevant context file before continuing.

## Scope

These instructions apply only to the `client/` Flutter project. Do not create or move this file to the SafarPay repository root.

## Project Overview

This is the SafarPay Flutter client for a ride-hailing app. It uses:

- Flutter / Dart
- GetX for state management and navigation
- `get_storage` and `flutter_secure_storage` for local state and token storage
- Google Sign-In and Firebase Core for Google auth setup
- `iconsax` for icons
- Centralized utilities under `lib/utils`
- Feature-first screens under `lib/features`

## Commands

Run commands from `client/`:

```bash
flutter pub get
flutter analyze
flutter test
dart format lib test
```

If Flutter tooling hangs in this environment, report it clearly instead of repeatedly retrying.

## Structure

Important folders:

```text
lib/
  app.dart
  common/
  data/
  features/
    authentication/
      controllers/
      models/
      repositories/
      screens/
      utils/
    home/
  utils/
    constants/
    device/
    helpers/
    http/
    local_storage/
    logging/
    theme/
    validators/
```

Authentication screen folders normally follow this pattern:

```text
screens/<screen_name>/
  <screen_name>.dart
  widgets/
```

Controllers for authentication screens go in:

```text
lib/features/authentication/controllers/
```

## Naming and Style

- Custom project classes should use the `S` prefix, for example `SColors`, `SSizes`, `SLoginForm`, `SOtpController`.
- Do not introduce `T*` class names.
- Prefer existing utilities from `lib/utils` before adding new constants or helpers.
- Avoid hard-coded Flutter `Colors.*` in feature UI. Use `SColors`.
- Use `SSizes` for spacing, radius, font sizes, and common dimensions where possible.
- Use `STexts` for user-facing strings.
- Use `SDeviceUtils`, not `TDeviceUtils`.
- Use `iconsax` icons where appropriate.

## UI Patterns

- Keep authentication pages visually consistent:
  - subtle branded top accent
  - `SafeArea`
  - `SingleChildScrollView`
  - centered `ConstrainedBox(maxWidth: 420)`
  - `SColors.primaryBackground`
- Avoid heavy nested card layouts unless explicitly requested.
- Keep phone OTP as the primary authentication path and Google as secondary.
- Use `SAuthNavigation` for normal auth screen pushes.
- Onboarding to login is handled by the auth-flow `AnimatedSwitcher`, not direct route replacement.

## State Management

- Use GetX controllers for screen state that owns `PageController`, `TextEditingController`, timers, or reactive UI state.
- Dispose controllers, timers, focus nodes, and text controllers properly.
- Use `Obx` only around the smallest widget subtree that needs reactive updates.

## Current Auth Flow

Current flow:

```text
AuthGateScreen
  AuthFlowScreen
    OnBoardingScreen
    LoginScreen
      phone OTP -> OtpScreen -> CompleteProfileScreen
      Google -> GoogleOtpProfileScreen when phone linking is required
      Google -> PermissionsScreen/HomeScreen when fully authenticated
```

Notes:

- `AuthFlowScreen` switches onboarding to login using `AnimatedSwitcher`.
- Phone login validates phone number and navigates to OTP.
- OTP uses a custom 6-digit underline input.
- Google phone linking uses `screens/profile/otp_google.dart`, then reuses `OtpScreen` with `SAuthOtpFlow.googlePhoneLink`.
- Post-auth routing goes to permissions first unless required permissions are already complete.
- Firebase generated config is local-only. Follow `FIREBASE_SETUP.md` to regenerate ignored config files.

## Verification

Before finishing UI/auth changes:

- Search for stale `S*` class names in touched files.
- Search for raw `Colors.*` in touched UI files.
- Attempt `flutter analyze` from `client/`.
- If analyzer times out or reports existing unrelated warnings, state that explicitly in the final response.
