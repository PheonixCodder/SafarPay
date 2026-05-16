# Help & Support Page Plan

## Summary

Add a Settings subpage for Help & Support that follows the supplied reference image. The page uses the shared primary header, the scooter support image, a rounded white options sheet, and right-slide navigation to five placeholder support subpages.

## Implementation

- Add `SImages.supportScooter` and register `assets/images/support/` in `pubspec.yaml`.
- Create `HelpSupportScreen` under `features/personalization/screens/help_support`.
- Build focused widgets for the main page:
  - `SHelpSupportHeader` for the teal header, title, back arrow, and image.
  - `SHelpSupportSheet` for the rounded white content area.
  - `SHelpSupportOptionTile` for each support row.
- Store support options in typed mapped content with `SHelpSupportOption` and `SHelpSupportContent`.
- Add placeholder subpages for Live Chat, Contact Us, FAQ's, Terms & Condition, and Something else in their existing folders.
- Wire `SettingsScreen` so only `Help & Support` opens `HelpSupportScreen` with `SRightSlidePageRoute`.
- Add required strings to `STexts` and page dimensions to `SSizes`.
- Update `client/AGENTS.md`, context docs, progress, and decision log.

## Verification

- Run `dart format` on touched Dart files.
- Run targeted `dart analyze` on help support, settings, constants, and `pubspec.yaml`-affected paths.
- Attempt `flutter analyze --no-pub`.
- Verify Settings `Help & Support` opens the support hub and back returns to Settings.
- Verify each support option opens its placeholder screen.
- Verify User Info, Notifications, and Privacy & Security still open their existing pages.
- Search touched Dart files for raw `Colors.*`, stale `T*` names, and one-primary-widget violations.

## Assumptions

- The existing `assets/images/support/support.png` is the supplied scooter illustration.
- The five support destination screens are placeholders in this unit; live chat, FAQ content, contact forms, and terms content will be planned separately.
