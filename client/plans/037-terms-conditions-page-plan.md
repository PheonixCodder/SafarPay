# Terms And Conditions Page Plan

## Goal

Build a Help Support Terms & Conditions experience matching the provided reference image while preserving the existing SafarPay Flutter structure, shared app bar, navigation helper, design constants, and screen/widget/data folder pattern.

## Scope

- Replace the placeholder `TermsConditionsScreen` with a real policy list page.
- Add static policy data under the existing `terms_conditions/data` folder.
- Add a detail page for individual policy content.
- Wire policy row taps to detail navigation.
- Keep all content local and backend-free.

## Files To Add Or Update

- Update:
  - `client/lib/features/personalization/screens/help_support/screens/terms_conditions/terms_conditions.dart`
- Add:
  - `client/lib/features/personalization/screens/help_support/screens/terms_conditions/data/terms_conditions_data.dart`
  - `client/lib/features/personalization/screens/help_support/screens/terms_conditions/models/terms_policy.dart`
  - `client/lib/features/personalization/screens/help_support/screens/terms_conditions/screens/terms_policy_detail.dart`
  - `client/lib/features/personalization/screens/help_support/screens/terms_conditions/widgets/terms_policy_list_card.dart`
  - `client/lib/features/personalization/screens/help_support/screens/terms_conditions/widgets/terms_policy_tile.dart`
  - `client/lib/features/personalization/screens/help_support/screens/terms_conditions/widgets/terms_last_updated_label.dart`
  - `client/lib/features/personalization/screens/help_support/screens/terms_conditions/widgets/terms_detail_section_tile.dart`

If the `models/` or nested `screens/` folders do not exist yet, create them under `terms_conditions/` to keep this page self-contained.

## Step By Step Implementation

1. Inspect existing Help Support files.
   - Confirm `TermsConditionsScreen` is already referenced by `SHelpSupportContent`.
   - Confirm Help Support uses `SRightSlidePageRoute`.
   - Preserve that route style for policy detail navigation.

2. Create local data models.
   - `STermsPolicy`
   - `STermsPolicySection`
   - Required fields:
     - `id`
     - `title`
     - `subtitle`
     - `IconData icon`
     - `lastUpdated`
     - `sections`

3. Create static terms data.
   - Store in `STermsConditionsData`.
   - Include six policies:
     - Rider Terms of Service
     - Driver Terms of Service
     - Privacy Policy
     - Refund Policy
     - Community Guidelines
     - Safety & Liability
   - Use `May 15, 2024` as the display date to match the reference.
   - Keep copy concise, realistic, and replaceable.

4. Rebuild `TermsConditionsScreen`.
   - Use `Scaffold`.
   - Use `SAppBar(showBackArrow: true, title: Text(...))`.
   - Body uses `SafeArea`, padding, and a vertically centered/constrained list card.
   - Show `STermsPolicyListCard` for the six policy rows.
   - Show `STermsLastUpdatedLabel` below the card.

5. Add list widgets.
   - `STermsPolicyListCard` owns the rounded white card and row dividers.
   - `STermsPolicyTile` owns a single policy row.
   - Use teal-accent icon styling from `SColors.primary`.
   - Keep the visual density close to the image.

6. Add detail screen.
   - `TermsPolicyDetailScreen` receives an `STermsPolicy`.
   - Use the shared `SAppBar`.
   - Show last-updated label near the top.
   - Render ordered expandable sections.
   - Use `ExpansionTile` or a custom controlled expansion widget if needed for visual accuracy.

7. Add detail section widget.
   - `STermsDetailSectionTile` renders:
     - numbered bold title
     - chevron
     - body text when expanded
     - subtle divider
   - Keep each file to one primary widget.

8. Verify navigation.
   - Help Support -> Terms & Conditions list.
   - Policy list row -> detail screen.
   - Back button returns to previous screen.

9. Verify quality.
   - Search touched files for raw `Colors.`.
   - Run targeted analyzer:
     - `flutter analyze lib/features/personalization/screens/help_support/screens/terms_conditions --no-pub`
   - If practical, run a focused widget test later for list rendering and row navigation.

## Design Decisions

- The shared `SAppBar` replaces the image's custom teal app bar because the user explicitly requested it.
- Policy data remains static and local because this screen is informational and no backend contract was requested.
- The detail screen is a nested sub-screen under `terms_conditions/screens` to match the project's normalized screen structure.
- The list and detail UI are split into local widgets so the main screen file stays focused.

## Acceptance Checks

- The placeholder Terms screen is gone.
- The first screen matches the reference list layout.
- The second screen matches the reference detail layout.
- All policy content comes from the local data folder.
- No new package is required.
- Analyzer reports no issues for touched files.
