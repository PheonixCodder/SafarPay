import 'package:flutter/material.dart';

import '../../../../../../../utils/constants/colors.dart';
import '../../../../../../../utils/constants/sizes.dart';
import '../models/faq_models.dart';
import 'faq_article_row.dart';

class SFaqPopularArticlesCard extends StatelessWidget {
  const SFaqPopularArticlesCard({
    super.key,
    required this.articles,
    required this.onArticleSelected,
  });

  final List<SFaqArticle> articles;
  final ValueChanged<SFaqArticle> onArticleSelected;

  @override
  Widget build(BuildContext context) {
    return DecoratedBox(
      decoration: BoxDecoration(
        color: SColors.white,
        borderRadius: BorderRadius.circular(SSizes.cardRadiusLg),
        border: Border.all(color: SColors.borderSecondary),
      ),
      child: ClipRRect(
        borderRadius: BorderRadius.circular(SSizes.cardRadiusLg),
        child: Column(
          children: [
            for (var index = 0; index < articles.length; index++) ...[
              SFaqArticleRow(
                article: articles[index],
                onTap: () => onArticleSelected(articles[index]),
              ),
              if (index != articles.length - 1)
                const Divider(
                  height: SSizes.dividerHeight,
                  thickness: SSizes.dividerHeight,
                  color: SColors.borderSecondary,
                ),
            ],
          ],
        ),
      ),
    );
  }
}
