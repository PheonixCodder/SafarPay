# FAQ Search And Category Interactions Prompt

Fix the Help Support FAQ page so it is functional instead of display-only.

## Current Problem

- The `View All Articles` button was removed and should not return.
- The search field is currently only visual and does not filter anything.
- Category rows are currently only visual and do not show category-specific articles.

## Target File

- `client/lib/features/personalization/screens/help_support/screens/faqs/faqs.dart`

## Required Behavior

- Keep the existing FAQ data under:
  - `client/lib/features/personalization/screens/help_support/screens/faqs/data`
- Search should filter local FAQ content:
  - empty search shows all categories and popular articles
  - non-empty search shows matching articles and matching categories
  - match against article title, summary, bullets, and category title/subtitle
  - show `Search Results` as the article section title while search is active
  - show a compact empty state when no matching articles exist
- Category rows should be interactive:
  - tapping a category sets it as active
  - article section title changes to `{Category Title} Articles`
  - article list shows only `SFaqsData.articlesForCategory(category.id)`
  - categories remain visible so users can switch categories
- Article rows should continue opening `FaqArticleDetailScreen` with `SRightSlidePageRoute`.

## Constraints

- No backend calls.
- No new package.
- Do not restore the `View All Articles` button.
- Keep styling aligned with the existing FAQ page and SafarPay tokens.
- Keep one primary widget per file.

## Acceptance Criteria

- Search for `refund` shows `How do refunds work?`.
- Search hides unrelated articles such as `I lost an item in the ride`.
- Tapping `Payments` shows payment articles and hides rider-only articles.
- Article detail navigation still works.
- Existing FAQ tests are updated to cover the interactions.
- Targeted analyzer passes.
