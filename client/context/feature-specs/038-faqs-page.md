# FAQs Page Prompt

Create the FAQ page shown in the provided reference images.

## Entry Point

- The page is opened from `client/lib/features/personalization/screens/help_support/help_support.dart` through the existing Help & Support option list.
- The target screen file is:
  - `client/lib/features/personalization/screens/help_support/screens/faqs/faqs.dart`
- Keep the existing Help Support navigation pattern:
  - `SHelpSupportSheet`
  - `SHelpSupportOptionTile`
  - `SRightSlidePageRoute`

## Required Layout

- Use the existing shared app bar:
  - `client/lib/common/widgets/appbar/appbar.dart`
  - Do not recreate the teal custom app bar from the images.
- Everything below the app bar should closely match the screenshots:
  - White/light background.
  - Top search field with search icon and `Search help articles...`.
  - A Categories section with rounded white card rows.
  - Category rows include teal icon blocks, bold title, small subtitle, and a chevron.
  - A Popular Articles section with rounded white article rows and a primary `View All Articles` button.
  - Article rows have bold compact titles and a chevron.
- Article detail page should match the second image:
  - shared `SAppBar`
  - article title
  - compact illustration/header visual
  - article summary/body
  - bullet list
  - highlighted `Refund Timelines` style card when applicable
  - `Was this article helpful?` row with Yes/No controls
  - `Related Articles` card.

## Required Data Location

- Store all displayed FAQ data under:
  - `client/lib/features/personalization/screens/help_support/screens/faqs/data`
- Do not hard-code data directly inside widgets.
- Include these categories:
  - Rider
  - Payments
  - Safety
  - Account
  - Technical
  - Driver
- Include these popular articles:
  - How do I cancel a ride?
  - How do refunds work?
  - What is a cancellation fee?
  - How do I change my payment method?
  - How to report a driver?
  - I lost an item in the ride

## Folder And Widget Rules

- Follow the existing centralized screen structure:
  - one main screen file
  - screen-specific widgets inside `widgets/`
  - owned sub-screens inside `screens/`
  - typed static data inside `data/`
  - local models inside `models/`
- Keep each Dart file focused on one primary widget.
- Use local widgets unless a widget becomes reusable across features.

## Styling Rules

- Use existing constants:
  - `SColors`
  - `SSizes`
  - `STexts` where shared stable strings are useful
- Use `iconsax` icons.
- Avoid raw `Colors.*` in touched UI files.
- Keep the design compact, light-mode, rounded, and close to the reference.
- No backend calls or new packages.

## Acceptance Criteria

- Help Support opens the FAQ list page.
- The FAQ page visually matches the category and popular article screenshots except for the shared app bar.
- Article detail visually matches the provided article detail screenshot except for the shared app bar.
- FAQ data is sourced from the local `data/` folder.
- Tapping `How do refunds work?` opens its detail page.
- `flutter analyze` passes for touched files.
