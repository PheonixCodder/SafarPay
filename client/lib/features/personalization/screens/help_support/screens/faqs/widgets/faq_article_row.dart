import 'package:flutter/material.dart';
import 'package:iconsax/iconsax.dart';

import '../../../../../../../utils/constants/colors.dart';
import '../../../../../../../utils/constants/sizes.dart';
import '../models/faq_models.dart';

class SFaqArticleRow extends StatelessWidget {
  const SFaqArticleRow({
    super.key,
    required this.article,
    required this.onTap,
  });

  final SFaqArticle article;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return InkWell(
      onTap: onTap,
      child: Padding(
        padding: const EdgeInsets.symmetric(
          horizontal: SSizes.md,
          vertical: SSizes.md,
        ),
        child: Row(
          children: [
            Expanded(
              child: Text(
                article.title,
                maxLines: 2,
                overflow: TextOverflow.ellipsis,
                style: Theme.of(context).textTheme.labelLarge?.copyWith(
                      color: SColors.textPrimary,
                      fontWeight: FontWeight.w900,
                      height: 1.2,
                    ),
              ),
            ),
            const SizedBox(width: SSizes.sm),
            const Icon(
              Iconsax.arrow_right_3,
              size: SSizes.iconSm,
              color: SColors.textSecondary,
            ),
          ],
        ),
      ),
    );
  }
}
