# Contact Us Page Prompt

Create the Help & Support Contact Us page to match the provided mobile reference while using the existing SafarPay app structure.

## Source Prompt

The Contact Us page is opened from `client/lib/features/personalization/screens/help_support/help_support.dart` through the existing Help & Support option list. Implement it at `client/lib/features/personalization/screens/help_support/screens/contact/contact.dart`.

Use the shared `SAppBar` from `client/lib/common/widgets/appbar/appbar.dart` with the title `Let's get in touch!`. Everything below the app bar should visually follow the provided reference: a centered support illustration, three contact method cards, and an `Our social media` section with rows for Twitter, Instagram, Facebook, Linked In, and Medium.

Use existing app colors, typography, sizing, and the current client screen-folder structure. Add the support email and phone number to `client/lib/utils/constants/texts.dart` and read them from there.

## Requirements

- Replace the existing Contact placeholder screen.
- Keep the route entry from Help & Support unchanged.
- Add screen-local widgets under `screens/contact/widgets/`.
- Keep one primary widget per Dart file.
- Use `STexts` for user-facing strings that need reuse, especially support phone/email.
- Use `SColors`, `SSizes`, and existing icons instead of local style drift.
- Provide action affordances for Call Us, Email Us, and Chat.
- Render the social media list exactly as local rows; external launch behavior can stay best-effort and non-blocking.
- Update client context and plan files for memory.
