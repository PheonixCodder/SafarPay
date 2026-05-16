# Progress Tracker

Update this file after every meaningful implementation change.

## Current Phase

- Client foundation, authentication UI/mock phase, and post-auth navigation shell are complete; next phase is backend integration and ride-feature expansion.

## Current Goal

- Keep client context synchronized while cleaning client structure and preparing future ride-feature expansion.

## Completed

- Flutter scaffold and platform folders were added.
- Shared utilities, theme constants, app text constants, validators, HTTP client, storage helpers, and auth feature structure were added.
- Phone OTP registration flow was added with login, OTP, profile, and post-auth permission routing.
- Google auth setup was added with Google token verification and a dedicated phone-link screen when a phone is required.
- `client/lib/data/.gitkeep` was added to preserve the empty data folder.
- Client context documentation and plans folder were introduced.
- Reconstructed feature-spec prompt files were planned for scaffold, design foundation, onboarding, auth gate/login, phone OTP/profile, permissions/home, Google phone linking, and documentation workflow.
- Firebase generated config hardening was added so API-key-bearing generated files are local-only and ignored going forward.
- Post-auth navigation now routes authenticated users through `NavigationMenu` instead of directly to `HomeScreen`.
- Navigation menu active-state design was updated to use a smooth top indicator line instead of a selected pill highlight.
- Navigation menu indicator positioning was refined to use responsive width-based centering, and bottom tab icons were reduced in size.
- Reusable ride search result row was added under `common/widgets/ride`.
- Typed demo ride response models and 10 demo ride records were added under `lib/data/rides`.
- Home search now shows two recent ride destinations from demo data.
- Home banner carousel was added with local banner assets.
- Home service categories were added with local category assets.
- Notification, category, and ride search widget design values were moved into shared utilities without intentional visual changes.
- Client widget structure was cleaned up with reusable widgets moved to `lib/common/widgets`, multi-widget files split, and settings rebuilt from focused components.
- Settings profile edit and `User Info` row now navigate to the personalization profile screen through a reusable right-slide transition.
- A reusable shadcn edit drawer was planned for local profile value edits from personalization profile rows.
- Settings `Privacy & Security` now opens a dedicated Privacy Policy page with expandable mapped policy sections.
- Settings `Notifications` now opens a dedicated timeline-style Notifications page with mapped demo notifications and local category filters.
- Settings `Help & Support` now opens a reference-matched support hub with five placeholder support option subpages.
- Bottom navigation Trips now opens a four-tab ride history page with ongoing, scheduled, canceled, completed, and ride details views.

## In Progress

- Documentation history is being reorganized into feature-first prompt and plan files.
- Firebase generated config is being removed from Git tracking while preserved locally for development.
- Flutter analyzer still reports existing info-level cleanup items in unrelated files.

## Next Up

- Manually test phone OTP and Google phone-link flows on a device or emulator.
- Decide when to connect mocked auth repository methods to real backend endpoints.
- Clean existing analyzer info items when the team chooses a lint-cleanup pass.
- Add real ride booking, bidding, location tracking, and payment client screens as separate planned feature units.
- Rotate or restrict the previously exposed Firebase API keys in Google Cloud/Firebase and resolve the GitHub secret-scanning alerts.

## Open Questions

- What exact backend response shape will production Google verification return when phone linking is required?
- Should the client support driver-specific onboarding or remain rider-only for the current phase?
- Which generated platform file changes should be committed, if any, after plugin changes?

## Architecture Decisions

- Phone OTP is the primary auth path; Google is a secondary provider.
- Google phone linking is a dedicated screen, not a modified login-screen state.
- OTP verification remains centralized in `OtpScreen` and `SOtpController`.
- Tokens are persisted only through `STokenStorage`.
- App copy remains centralized in `STexts`.
- Empty source folders that matter to architecture are preserved with `.gitkeep`.
- `NavigationMenu` is the authenticated app shell; `HomeScreen` is only the first tab.
- Navigation menu active state is represented by primary icon/label color and a custom animated top line.
- Navigation menu top indicator positioning must be calculated from tab width instead of hard-coded alignment values.
- Shared ride UI components live in `lib/common/widgets/ride` when they are not owned by one screen.
- Ride demo data mirrors backend response contracts until live ride APIs are integrated.
- Home carousel uses local banner assets and app sizing/radius tokens.
- Home service categories are static local UI until service destination screens are planned.
- Shared widget styling should use `SColors`, `SOpacities`, `SSizes`, `STexts`, and `SHelperFunctions` instead of local literals.
- Reusable widgets belong in `lib/common/widgets`; screen-local widgets should live in the owning screen's `widgets/` folder with one primary widget per file.
- Reusable non-auth page transitions live in `lib/common/navigation`.
- Reusable shadcn drawers live in `lib/common/widgets/drawers` and use the local shadcn-ui-flutter skill docs.
- Settings legal and privacy content should render from typed mapped content files so copy can be updated without rewriting page layout.
- Settings notification feeds should render from typed mapped demo content until backend notification APIs are integrated.
- Help & Support option rows should remain a simple support hub until live support workflows are planned.
- Trips list and details screens should consume backend-aligned ride DTOs and avoid backend mutation flows until ride APIs are connected.

## Session Notes

- Existing local dirty files include auth flow code changes, platform generated plugin registrant files, `code.md`, `PAYMENT_SERVICE_FLOW.md`, `SafarPay.iml`, and `client/AGENTS.md`.
- `flutter analyze --no-pub` was run after the Google phone-link work and only reported existing info-level items outside the new screen.
- During the client structure cleanup, `dart format` and `flutter analyze --no-pub` timed out in this environment; targeted source scans were used to verify widget-file structure and stale-name cleanup.
- Future agents should read `client/AGENTS.md` and then the context files before changing client code.
- The client structure cleanup added `context/feature-specs/017-client-structure-cleanup.md` and `plans/018-client-structure-cleanup-plan.md`.
- Settings user-info navigation added `context/feature-specs/018-settings-user-info-navigation.md` and `plans/019-settings-user-info-navigation-plan.md`.
- Common edit drawer work added `context/feature-specs/019-common-edit-drawer.md` and `plans/020-common-edit-drawer-plan.md`.
- Privacy Policy page work added `context/feature-specs/020-privacy-policy-page.md` and `plans/021-privacy-policy-page-plan.md`.
- Notifications page work added `context/feature-specs/021-notifications-page.md` and `plans/022-notifications-page-plan.md`.
- Help & Support page work added `context/feature-specs/022-help-support-page.md` and `plans/023-help-support-page-plan.md`.
- Trips page work added `context/feature-specs/023-rides-trips-page.md` and `plans/024-rides-trips-page-plan.md`.
