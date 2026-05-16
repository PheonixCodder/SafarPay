# Prompt: Help & Support Page

Create a Help & Support page for the SafarPay Flutter client and open it from Settings.

## Goal

When the rider taps `Help & Support` in `client/lib/features/personalization/screens/settings/settings.dart`, open a new support hub screen that closely follows the provided reference image.

## Requirements

- Read `client/AGENTS.md` and the context files before editing.
- Add the main page under `client/lib/features/personalization/screens/help_support`.
- Use `SPrimaryHeaderContainer` for the teal header area.
- Use the existing support scooter illustration at `assets/images/support/support.png` and expose it through `SImages`.
- Add the support asset folder to `pubspec.yaml`.
- Match the reference layout:
  - teal top header
  - back arrow and centered `Help & Support` title
  - scooter support image centered under the title
  - rounded white sheet starting below the image
  - `What can we help you with?` heading
  - simple rows for `Live Chat`, `Contact Us`, `FAQ's`, `Terms & Condition`, and `Something else`
  - left icons and right chevrons
- Use `SRightSlidePageRoute` for page navigation.
- Use the existing empty subfolders for each support option and add one screen file per option.
- Put main Help & Support widgets under `help_support/widgets`.
- Keep one primary widget per Dart file.
- Use `SColors`, `SSizes`, `STexts`, Iconsax, and existing common components.
- Update context docs, the saved implementation plan, progress, and decision log.

## Acceptance Criteria

1. Tapping `Help & Support` opens `HelpSupportScreen`.
2. The main screen visually matches the provided reference.
3. The support image is loaded through `SImages.supportScooter`.
4. All five support options render in the requested order.
5. Each support option opens its corresponding placeholder subpage.
6. User Info, Notifications, and Privacy & Security navigation remain unchanged.
