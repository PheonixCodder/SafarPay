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
16. `context/feature-specs/009-add-navigation-menu.md` - prompt for post-auth navigation menu integration
17. `context/feature-specs/010-update-navigation-menu-design.md` - prompt for custom navigation menu active-state design
18. `context/feature-specs/011-fix-navigation-menu-indicator-alignment.md` - prompt for navigation indicator alignment and icon sizing
19. `context/feature-specs/012-ride-search-result-widget.md` - prompt for reusable ride search result row
20. `context/feature-specs/013-demo-ride-data-and-home-recents.md` - prompt for typed demo ride data and home recent rides
21. `context/feature-specs/014-home-carousel.md` - prompt for home banner carousel
22. `context/feature-specs/015-home-categories.md` - prompt for home service categories
23. `context/feature-specs/016-widget-design-token-cleanup.md` - prompt for shared widget design token cleanup
24. `context/feature-specs/017-client-structure-cleanup.md` - prompt for client structure cleanup
25. `context/feature-specs/018-settings-user-info-navigation.md` - prompt for Settings user-info navigation
26. `context/feature-specs/019-common-edit-drawer.md` - prompt for reusable shadcn edit drawer
27. `context/feature-specs/020-privacy-policy-page.md` - prompt for Settings Privacy Policy page
28. `context/feature-specs/021-notifications-page.md` - prompt for Settings Notifications page
29. `context/feature-specs/022-help-support-page.md` - prompt for Settings Help & Support page
30. `context/feature-specs/023-rides-trips-page.md` - prompt for Trips ride history page
31. `context/feature-specs/024-common-searchbar-widget.md` - prompt for common search bar widget
32. `context/feature-specs/025-passenger-map-location-tracking.md` - prompt for passenger map and live ride tracking foundation
33. `context/feature-specs/026-driver-registration-flow.md` - prompt for Settings-launched driver registration entry flow
34. `context/feature-specs/027-driver-verification-demo-status.md` - prompt for backend-offline driver verification status demos
35. `context/feature-specs/028-driver-submit-review-and-header-polish.md` - prompt for driver submit-review CTA and header polish
36. `context/feature-specs/029-driver-registration-step-submission-pages.md` - prompt for driver registration step forms and presigned uploads
37. `context/feature-specs/030-client-screen-structure-normalization.md` - prompt for client screen structure normalization
38. `context/feature-specs/031-branch-split-and-pr-merge.md` - prompt for splitting current mixed client work into scoped PR branches
39. `context/feature-specs/032-map-first-passenger-booking-flow.md` - prompt for map-first passenger booking and hybrid offers
40. `context/feature-specs/045-real-auth-api-and-console-otp.md` - prompt for real Auth APIs and console OTP local testing
41. `context/feature-specs/046-existing-phone-login.md` - prompt for existing phone users to log in after OTP
42. `context/feature-specs/047-auth-profile-demographics.md` - prompt for auth profile demographics and editable profile sync
43. `context/feature-specs/052-driver-vehicle-service-consent.md` - prompt for confirming existing vehicle reuse before service attachment
44. `context/feature-specs/053-safe-branch-split-and-pr-merge.md` - prompt for safe branch splitting and sequential PR merges
45. `context/feature-specs/054-ride-backend-client-integration.md` - prompt for real passenger Ride, Bidding, Location, and Geospatial backend integration
45. `plans/000-client-product-and-architecture-plan.md` - canonical client product and architecture plan
45. `plans/001-flutter-scaffold-plan.md` - Flutter scaffold plan
46. `plans/002-design-system-foundation-plan.md` - shared design system plan
47. `plans/003-onboarding-flow-plan.md` - onboarding implementation plan
48. `plans/004-auth-gate-and-login-plan.md` - auth gate and login plan
49. `plans/005-phone-otp-and-profile-plan.md` - phone OTP and profile plan
50. `plans/006-permissions-and-home-plan.md` - permissions and home plan
51. `plans/007-google-phone-link-screen-plan.md` - Google phone-link auth flow plan
52. `plans/008-client-context-documentation-plan.md` - client documentation setup plan
53. `plans/009-firebase-config-hardening-plan.md` - Firebase config hardening plan
54. `plans/010-navigation-menu-plan.md` - post-auth navigation menu plan
55. `plans/011-update-navigation-menu-design-plan.md` - custom navigation menu design plan
56. `plans/012-navigation-menu-alignment-and-icon-size-plan.md` - navigation indicator alignment and icon size plan
57. `plans/013-ride-search-result-widget-plan.md` - reusable ride search result widget plan
58. `plans/014-demo-ride-data-and-home-recents-plan.md` - typed demo ride data and home recents plan
59. `plans/015-home-carousel-plan.md` - home banner carousel plan
60. `plans/016-home-categories-plan.md` - home service categories plan
61. `plans/017-widget-design-token-cleanup-plan.md` - shared widget design token cleanup plan
62. `plans/018-client-structure-cleanup-plan.md` - client structure cleanup plan
63. `plans/019-settings-user-info-navigation-plan.md` - Settings user-info navigation plan
64. `plans/020-common-edit-drawer-plan.md` - reusable shadcn edit drawer plan
65. `plans/021-privacy-policy-page-plan.md` - Settings Privacy Policy page plan
66. `plans/022-notifications-page-plan.md` - Settings Notifications page plan
67. `plans/023-help-support-page-plan.md` - Settings Help & Support page plan
68. `plans/024-rides-trips-page-plan.md` - Trips ride history page plan
69. `plans/025-common-searchbar-widget-plan.md` - common search bar widget plan
70. `plans/026-passenger-map-location-tracking-plan.md` - passenger map and live ride tracking foundation plan
71. `plans/027-driver-registration-flow-plan.md` - Settings-launched driver registration entry flow plan
72. `plans/028-driver-verification-demo-status-plan.md` - backend-offline driver verification status demo plan
73. `plans/029-driver-submit-review-and-header-polish-plan.md` - driver submit-review CTA and header polish plan
74. `plans/030-driver-registration-step-submission-pages-plan.md` - driver registration step forms and presigned upload plan
75. `plans/031-client-screen-structure-normalization-plan.md` - client screen structure normalization plan
76. `plans/032-map-first-passenger-booking-flow-plan.md` - map-first passenger booking and hybrid offers plan
77. `plans/045-real-auth-api-and-console-otp-plan.md` - real Auth API and console OTP plan
78. `plans/046-existing-phone-login-plan.md` - existing phone login branch plan
79. `plans/047-auth-profile-demographics-plan.md` - auth profile demographics implementation plan
81. `plans/052-driver-vehicle-service-consent-plan.md` - driver vehicle reuse consent plan
82. `plans/053-safe-branch-split-and-pr-merge-plan.md` - safe branch split and sequential PR merge plan
83. `plans/054-ride-backend-client-integration-plan.md` - real passenger Ride, Bidding, Location, and Geospatial backend integration plan
84. `plans/900-branch-split-and-merge-plan.md` - Git branch split and merge plan
85. `plans/901-empty-folder-restoration-plan.md` - empty-folder preservation plan
86. `plans/decisions-log.md` - permanent decision record

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
- Keep each Dart file focused on one primary widget class; split reusable or independently meaningful widgets into their own files.
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
- Use shared transition helpers from `lib/common/navigation` for reusable non-auth page transitions.
- Before using or changing shadcn UI widgets, read `client/.agents/skills/shadcn-ui-flutter/SKILL.md` and the relevant component docs.
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
      phone OTP -> OtpScreen -> NavigationMenu/PermissionsScreen when phone exists
      phone OTP -> OtpScreen -> CompleteProfileScreen when phone is new
      Google -> GoogleOtpProfileScreen when phone linking is required
      Google -> PermissionsScreen/NavigationMenu when fully authenticated
```

Notes:

- `AuthFlowScreen` switches onboarding to login using `AnimatedSwitcher`.
- Phone login validates phone number and navigates to OTP.
- OTP verification branches by backend `next_step`: existing phone users receive tokens and enter post-auth routing, while new phone users receive `registration_token` and complete profile.
- OTP uses a custom 6-digit underline input.
- Google phone linking uses `screens/profile/otp_google.dart`, then reuses `OtpScreen` with `SAuthOtpFlow.googlePhoneLink`.
- Post-auth routing goes to permissions first unless required permissions are already complete, then enters `NavigationMenu`.
- Firebase generated config is local-only. Follow `FIREBASE_SETUP.md` to regenerate ignored config files.

## Verification

Before finishing UI/auth changes:

- Search for stale `S*` class names in touched files.
- Search for raw `Colors.*` in touched UI files.
- Attempt `flutter analyze` from `client/`.
- If analyzer times out or reports existing unrelated warnings, state that explicitly in the final response.
