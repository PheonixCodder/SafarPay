# FAQ Search And Category Interactions Plan

## Goal

Make the Help Support FAQ page functional by wiring local search and category filtering while keeping the `View All Articles` button removed.

## Implementation Steps

1. Update focused tests.
   - Remove the stale `View All Articles` expectation.
   - Add a search test for `refund`.
   - Add a category test for `Payments`.
   - Keep article detail navigation coverage.

2. Convert `FaqsScreen` to local state.
   - Use `StatefulWidget`.
   - Track `_query` and `_selectedCategory`.
   - Use `setState` for local UI-only interactions.

3. Add local filtering helpers.
   - `_filteredCategories` filters category title/subtitle by query.
   - `_visibleArticles` returns:
     - search results when query is not empty
     - selected category articles when a category is active
     - `SFaqsData.popularArticles` by default.
   - `_articleSectionTitle` returns:
     - `Search Results`
     - `{Category Title} Articles`
     - `Popular Articles`.

4. Wire UI callbacks.
   - `SFaqSearchField.onChanged` updates `_query` and clears selected category when searching.
   - `SFaqCategoryCard.onCategorySelected` sets selected category and clears query.
   - Article rows keep existing detail navigation.

5. Add an empty state.
   - Display a compact centered text when the visible article list is empty.
   - Keep categories visible even when no articles match.

6. Update context docs.
   - `client/context/progress-tracker.md`
   - `client/context/ui-context.md`

7. Verify.
   - `flutter test test/personalization/faqs_screen_test.dart --no-pub`
   - `flutter analyze lib/features/personalization/screens/help_support/screens/faqs test/personalization/faqs_screen_test.dart --no-pub`
   - Attempt `dart format`; report timeout if it persists.

## Acceptance Checks

- Search and category filters update visible articles.
- Removed button stays removed.
- Article detail navigation remains intact.
- Tests and analyzer pass.
