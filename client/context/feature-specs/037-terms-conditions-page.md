# Terms And Conditions Page Prompt

Create the Terms & Conditions page shown in the provided reference image.

## Entry Point

- The page is opened from `client/lib/features/personalization/screens/help_support/help_support.dart` through the existing Help & Support option list.
- Keep the existing navigation pattern from Help & Support:
  - `SHelpSupportSheet`
  - `SHelpSupportOptionTile`
  - `SRightSlidePageRoute`
- The target screen file is:
  - `client/lib/features/personalization/screens/help_support/screens/terms_conditions/terms_conditions.dart`

## Required Layout

- Use the existing app bar:
  - `client/lib/common/widgets/appbar/appbar.dart`
  - Do not recreate the teal custom app bar from the image.
- Everything below the app bar should closely match the reference:
  - White/light background.
  - A list page showing policy categories in a rounded white card.
  - Each row has a teal icon block on the left, a bold title, a smaller subtitle, and row separation.
  - A centered "Last Updated: May 15, 2024" footer on the list screen.
  - Tapping a policy category opens a detail view for that category.
  - The detail view shows a centered last-updated line and vertically stacked numbered expandable sections.
  - Section rows look like the image: bold section title, subtle divider, chevron for collapsed/expanded state.

## Required Data Location

- Store all displayed terms/policy data under:
  - `client/lib/features/personalization/screens/help_support/screens/terms_conditions/data`
- Do not hard-code the content directly inside the screen widget.
- Data should include:
  - Rider Terms of Service
  - Driver Terms of Service
  - Privacy Policy
  - Refund Policy
  - Community Guidelines
  - Safety & Liability
- Each policy item needs:
  - id
  - title
  - subtitle
  - icon
  - last updated value
  - ordered detail sections

## Detail Content

Use practical placeholder legal copy that matches the app domain without pretending to be final legal advice. Keep content concise and production-shaped so the UI can be reviewed now and legal copy can be replaced later.

The Rider Terms of Service detail page should visually match the second panel in the image and include sections similar to:

1. Acceptance of Terms
2. Use of the Service
3. User Responsibilities
4. Payments & Fees
5. Cancellations & Refunds
6. Prohibited Conduct
7. Limitation of Liability

Other policy detail pages should reuse the same component structure with their own relevant sections.

## Folder And Widget Rules

- Follow the existing centralized screen structure:
  - one main screen file
  - screen-specific widgets inside `widgets/`
  - static screen data inside `data/`
- Keep each Dart file focused on one primary widget.
- If a widget becomes reusable across Help Support screens, place it under `client/lib/common/widgets`; otherwise keep it local to `terms_conditions/widgets`.

## Styling Rules

- Use existing constants:
  - `SColors`
  - `SSizes`
  - `STexts` if adding shared strings is useful
- Use `iconsax` icons.
- Avoid raw `Colors.*` in touched UI files.
- Keep the design light-mode, rounded, compact, and close to the reference.
- Match the reference spacing and hierarchy:
  - card width constrained by screen padding
  - rows tall enough for icon + two text lines
  - subtle borders/shadows
  - compact typography

## Acceptance Criteria

- Help Support opens the Terms & Conditions list page.
- The list page visually matches the first reference screen except for the shared app bar.
- Tapping any policy item opens its detail screen using the same navigation style.
- The Rider Terms detail page visually matches the second reference screen except for the shared app bar.
- Terms data is sourced from the local `data/` folder.
- No backend calls are introduced.
- `flutter analyze` passes for touched files.
