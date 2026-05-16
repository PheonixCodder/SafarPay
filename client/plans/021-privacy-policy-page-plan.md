# Privacy Policy Page Plan

## Summary

Add a Settings subpage for Privacy Policy content. The page will be opened from `Privacy & Security`, use the existing right-slide route pattern, and render typed placeholder policy content from a separate data file.

## Implementation

- Create `PrivacyPolicyScreen` under `features/personalization/screens/privacy_policy`.
- Store policy sections in typed mapped content using `SPrivacyPolicySection` and `SPrivacyPolicyContent`.
- Build the UI from focused screen-local widgets:
  - `SPrivacyPolicyHeader` for the summary and trust cues.
  - `SPrivacyPolicyHighlight` for compact control/security notes.
  - `SPrivacyPolicySectionTile` for expandable policy sections.
  - `SPrivacyPolicyFooter` for support guidance.
- Wire `SettingsScreen` so only the `Privacy & Security` app-settings row opens `PrivacyPolicyScreen` with `SRightSlidePageRoute`.
- Add reusable strings to `STexts` and page dimensions to `SSizes`.
- Update `client/AGENTS.md`, context docs, progress, and decision log.

## Verification

- Run `dart format` on touched Dart files.
- Run `flutter analyze --no-pub` when tooling responds.
- Verify Settings `Privacy & Security` opens the new page and back returns to Settings.
- Verify `User Info` still opens the personalization profile screen.
- Search touched Dart files for raw `Colors.*`, stale `T*` names, and hard-coded asset paths.

## Assumptions

- Placeholder privacy copy is acceptable and will be replaced later.
- This unit is informational only; no backend persistence or consent workflow is introduced.
