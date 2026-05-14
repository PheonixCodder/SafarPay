# Progress Tracker

Update this file after every meaningful implementation change.

## Current Phase

- Client foundation and authentication UI/mock phase complete; next phase is backend integration and ride-feature expansion.

## Current Goal

- Reengineer the whole current client history into feature-spec prompts, feature-first plans, updated context files, and decision logs.

## Completed

- Flutter scaffold and platform folders were added.
- Shared utilities, theme constants, app text constants, validators, HTTP client, storage helpers, and auth feature structure were added.
- Phone OTP registration flow was added with login, OTP, profile, and post-auth permission routing.
- Google auth setup was added with Google token verification and a dedicated phone-link screen when a phone is required.
- `client/lib/data/.gitkeep` was added to preserve the empty data folder.
- Client context documentation and plans folder were introduced.
- Reconstructed feature-spec prompt files were planned for scaffold, design foundation, onboarding, auth gate/login, phone OTP/profile, permissions/home, Google phone linking, and documentation workflow.

## In Progress

- Google phone-link flow implementation exists locally and needs final review/commit when ready.
- Documentation history is being reorganized into feature-first prompt and plan files.
- Flutter analyzer still reports existing info-level cleanup items in unrelated files.

## Next Up

- Manually test phone OTP and Google phone-link flows on a device or emulator.
- Decide when to connect mocked auth repository methods to real backend endpoints.
- Clean existing analyzer info items when the team chooses a lint-cleanup pass.
- Add real ride booking, bidding, location tracking, and payment client screens as separate planned feature units.

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

## Session Notes

- Existing local dirty files include auth flow code changes, platform generated plugin registrant files, `code.md`, `PAYMENT_SERVICE_FLOW.md`, `SafarPay.iml`, and `client/AGENTS.md`.
- `flutter analyze --no-pub` was run after the Google phone-link work and only reported existing info-level items outside the new screen.
- Future agents should read `client/AGENTS.md` and then the context files before changing client code.
