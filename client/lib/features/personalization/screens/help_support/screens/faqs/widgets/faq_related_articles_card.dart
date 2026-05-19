import 'package:flutter/material.dart';

import '../data/faqs_data.dart';
import '../models/faq_models.dart';
import 'faq_popular_articles_card.dart';

class SFaqRelatedArticlesCard extends StatelessWidget {
  const SFaqRelatedArticlesCard({
    super.key,
    required this.article,
    required this.onArticleSelected,
  });

  final SFaqArticle article;
  final ValueChanged<SFaqArticle> onArticleSelected;

  @override
  Widget build(BuildContext context) {
    final related = article.relatedArticleIds
        .map(SFaqsData.articleById)
        .toList(growable: false);

    return SFaqPopularArticlesCard(
      articles: related,
      onArticleSelected: onArticleSelected,
    );
  }
}
