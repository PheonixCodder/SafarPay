# Contact Us Page Plan

## Goal

Build the Help & Support Contact Us page as a polished local support-contact screen that matches the supplied reference while staying within SafarPay's light theme and folder conventions.

## Implementation Steps

1. Add focused coverage.
   - Add a widget test for the Contact screen.
   - Assert the app bar title, three contact cards, and five social rows render.
   - Assert support phone/email constants exist.

2. Add contact constants.
   - Add `contactSupportPhone` and `contactSupportEmail` to `STexts`.
   - Add contact/social display labels only when reused outside a single widget.

3. Replace the placeholder Contact screen.
   - Keep `ContactScreen` as the single main screen widget in `contact.dart`.
   - Use `SAppBar(showBackArrow: true)` and the title `Let's get in touch!`.
   - Use `SafeArea`, `SingleChildScrollView`, and a constrained mobile content width.

4. Add screen-local widgets.
   - `SContactIllustration`: reference-style support agent illustration using Flutter drawing and Iconsax symbols.
   - `SContactActionCard`: card for Call Us, Email Us, and Chat.
   - `SContactSocialRow`: row for each social media destination.

5. Wire actions.
   - Call Us launches `tel:` using `STexts.contactSupportPhone`.
   - Email Us launches `mailto:` using `STexts.contactSupportEmail`.
   - Chat can route later to live chat; for now it uses the same visible affordance without changing the Help & Support route graph.
   - Social rows can use best-effort URL launch and stay UI-safe if the platform cannot open the link.

6. Update context.
   - `client/context/progress-tracker.md`
   - `client/context/project-overview.md`
   - `client/context/ui-context.md`

7. Verify.
   - `flutter test test/personalization/contact_screen_test.dart --no-pub`
   - `flutter analyze lib/features/personalization/screens/help_support/screens/contact test/personalization/contact_screen_test.dart --no-pub`
   - Attempt `dart format`; report timeout if the formatter hangs.

## Acceptance Checks

- Help & Support Contact Us opens a complete screen instead of the placeholder.
- The screen visually contains the reference layout: illustration, action cards, and social rows.
- Support phone/email are centralized in `STexts`.
- The touched contact screen and test pass focused analyzer checks.
