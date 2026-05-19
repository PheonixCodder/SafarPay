import 'package:flutter/material.dart';

import '../../../../../../../common/navigation/right_slide_page_route.dart';
import '../../../../../../../common/widgets/appbar/appbar.dart';
import '../../../../../../../utils/constants/colors.dart';
import '../../../../../../../utils/constants/sizes.dart';
import '../models/faq_models.dart';
import '../widgets/faq_article_illustration.dart';
import '../widgets/faq_helpful_card.dart';
import '../widgets/faq_highlight_card.dart';
import '../widgets/faq_related_articles_card.dart';

class FaqArticleDetailScreen extends StatelessWidget {
  const FaqArticleDetailScreen({
    super.key,
    required this.article,
  });

  final SFaqArticle article;

  void _openArticle(BuildContext context, SFaqArticle nextArticle) {
    Navigator.of(context).pushReplacement(
      SRightSlidePageRoute(
        page: FaqArticleDetailScreen(article: nextArticle),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final textTheme = Theme.of(context).textTheme;

    return Scaffold(
      backgroundColor: SColors.primaryBackground,
      appBar: SAppBar(
        showBackArrow: true,
        title: Text(article.title),
      ),
      body: SafeArea(
        child: SingleChildScrollView(
          physics: const BouncingScrollPhysics(),
          padding: const EdgeInsets.fromLTRB(
            SSizes.defaultSpace,
            SSizes.sm,
            SSizes.defaultSpace,
            SSizes.xl,
          ),
          child: Center(
            child: ConstrainedBox(
              constraints: const BoxConstraints(maxWidth: 440),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const SFaqArticleIllustration(),
                  const SizedBox(height: SSizes.md),
                  Text(
                    article.summary,
                    style: textTheme.bodyMedium?.copyWith(
                      color: SColors.textSecondary,
                      height: 1.4,
                      fontWeight: FontWeight.w500,
                    ),
                  ),
                  const SizedBox(height: SSizes.md),
                  Text(
                    article.sectionTitle,
                    style: textTheme.labelLarge?.copyWith(
                      color: SColors.textPrimary,
                      fontWeight: FontWeight.w900,
                    ),
                  ),
                  const SizedBox(height: SSizes.sm),
                  for (final bullet in article.bullets)
                    Padding(
                      padding: const EdgeInsets.only(bottom: SSizes.xs),
                      child: Text(
                        '- $bullet',
                        style: textTheme.bodySmall?.copyWith(
                          color: SColors.textPrimary,
                          height: 1.35,
                          fontWeight: FontWeight.w500,
                        ),
                      ),
                    ),
                  const SizedBox(height: SSizes.md),
                  SFaqHighlightCard(
                    title: article.highlightTitle,
                    body: article.highlightBody,
                  ),
                  const SizedBox(height: SSizes.lg),
                  const SFaqHelpfulCard(),
                  const SizedBox(height: SSizes.lg),
                  Text(
                    'Related Articles',
                    style: textTheme.labelLarge?.copyWith(
                      color: SColors.textPrimary,
                      fontWeight: FontWeight.w900,
                    ),
                  ),
                  const SizedBox(height: SSizes.sm),
                  SFaqRelatedArticlesCard(
                    article: article,
                    onArticleSelected: (nextArticle) =>
                        _openArticle(context, nextArticle),
                  ),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }
}
