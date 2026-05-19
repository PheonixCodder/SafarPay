# FAQs Page Plan

## Goal

Build a Help Support FAQ experience matching the provided category, popular articles, and article detail reference images while preserving SafarPay's shared app bar, right-slide navigation, local data pattern, and one-widget-per-file screen structure.

## Scope

- Replace the placeholder `FaqsScreen`.
- Add typed FAQ categories and articles under the existing `faqs/data` folder.
- Add article detail navigation and UI.
- Keep the feature local and backend-free.

## Implementation Steps

1. Add tests first.
   - Verify FAQ data includes six categories and six popular articles.
   - Verify the FAQ screen renders search, categories, popular articles, and `View All Articles`.
   - Verify tapping `How do refunds work?` opens article detail with refund content, helpful controls, and related articles.

2. Add local FAQ models.
   - `SFaqCategory`
   - `SFaqArticle`
   - Required fields include id, title, subtitle/body, icon, category id, bullets, optional highlight, and related article ids.

3. Add local FAQ data.
   - `SFaqsData.categories`
   - `SFaqsData.popularArticles`
   - `SFaqsData.articleById(String id)`
   - `SFaqsData.articlesForCategory(String categoryId)`

4. Rebuild `FaqsScreen`.
   - Use `SAppBar(showBackArrow: true, title: Text(STexts.helpSupportFaqs))`.
   - Add a compact search field.
   - Render `Categories` and `Popular Articles` sections.
   - Use `SRightSlidePageRoute` for article details.

5. Add local widgets.
   - Search field.
   - Category card and category tile.
   - Popular articles card and article row.
   - Article illustration, highlight card, helpful row, and related articles card.

6. Add article detail screen.
   - Owned by `faqs/screens`.
   - Receives `SFaqArticle`.
   - Renders the detail layout from the reference.

7. Update context docs.
   - `client/context/progress-tracker.md`
   - `client/context/project-overview.md`
   - `client/context/ui-context.md`

8. Verify.
   - Run focused FAQ tests.
   - Run targeted analyzer.
   - Attempt `dart format`; report if the formatter hangs in this environment.

## Acceptance Checks

- Placeholder FAQ screen is gone.
- FAQ data comes from `faqs/data`.
- Category and article list layout follows the image.
- Article detail layout follows the image.
- Tests and analyzer pass for touched FAQ files.
