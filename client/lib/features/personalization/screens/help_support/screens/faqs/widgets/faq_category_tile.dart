import 'package:flutter/material.dart';
import 'package:iconsax/iconsax.dart';

import '../../../../../../../utils/constants/colors.dart';
import '../../../../../../../utils/constants/sizes.dart';
import '../../../../../../../utils/helpers/helpers.dart';
import '../models/faq_models.dart';

class SFaqCategoryTile extends StatelessWidget {
  const SFaqCategoryTile({
    super.key,
    required this.category,
    required this.onTap,
  });

  final SFaqCategory category;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    final textTheme = Theme.of(context).textTheme;

    return InkWell(
      onTap: onTap,
      child: Padding(
        padding: const EdgeInsets.symmetric(
          horizontal: SSizes.md,
          vertical: SSizes.sm,
        ),
        child: Row(
          children: [
            Container(
              width: 36,
              height: 36,
              decoration: BoxDecoration(
                color: SHelperFunctions.withOpacity(
                  SColors.primary,
                  SOpacities.tinted,
                ),
                borderRadius: BorderRadius.circular(SSizes.cardRadiusSm),
              ),
              child: Icon(
                category.icon,
                size: SSizes.helpSupportOptionIconSize,
                color: SColors.primary,
              ),
            ),
            const SizedBox(width: SSizes.md),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    category.title,
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                    style: textTheme.labelLarge?.copyWith(
                      color: SColors.textPrimary,
                      fontWeight: FontWeight.w900,
                    ),
                  ),
                  const SizedBox(height: SSizes.xs),
                  Text(
                    category.subtitle,
                    maxLines: 2,
                    overflow: TextOverflow.ellipsis,
                    style: textTheme.labelSmall?.copyWith(
                      color: SColors.textSecondary,
                      height: 1.2,
                      fontWeight: FontWeight.w500,
                    ),
                  ),
                ],
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
