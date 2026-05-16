import 'package:flutter/material.dart';

import '../../../../utils/constants/colors.dart';
import '../../../../utils/constants/sizes.dart';
import '../../../../utils/helpers/helpers.dart';
import 'category_badge.dart';

class SCategoryTile extends StatelessWidget {
  const SCategoryTile({
    super.key,
    required this.title,
    required this.image,
    this.subtitle,
    this.isLarge = false,
    this.showBadge = false,
  });

  final String title;
  final String image;
  final String? subtitle;
  final bool isLarge;
  final bool showBadge;

  @override
  Widget build(BuildContext context) {
    final textTheme = Theme.of(context).textTheme;

    return Container(
      clipBehavior: Clip.antiAlias,
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(SSizes.homeCategoryTileRadius),
        gradient: LinearGradient(
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
          colors: [
            SColors.white,
            SHelperFunctions.withOpacity(
              SColors.lightContainer,
              SOpacities.nearSolid,
            ),
          ],
        ),
        border: Border.all(
          color: SHelperFunctions.withOpacity(
            SColors.white,
            SOpacities.border,
          ),
          width: SSizes.borderWidthSm,
        ),
        boxShadow: [
          BoxShadow(
            color: SHelperFunctions.withOpacity(
              SColors.pureBlack,
              SOpacities.soft,
            ),
            blurRadius: SSizes.shadowBlurLg,
            offset: const Offset(0, SSizes.shadowOffsetYMd),
          ),
        ],
      ),
      child: Stack(
        children: [
          Positioned(
            top: SSizes.homeCategoryDecorCircleTop,
            right: SSizes.homeCategoryDecorCircleRight,
            child: Container(
              width: SSizes.homeCategoryDecorCircleSize,
              height: SSizes.homeCategoryDecorCircleSize,
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                color: SHelperFunctions.withOpacity(
                  SColors.primary,
                  SOpacities.light,
                ),
              ),
            ),
          ),
          Positioned(
            right: isLarge
                ? SSizes.homeCategoryLargeImageRight
                : SSizes.homeCategorySmallImageRight,
            bottom: isLarge
                ? SSizes.homeCategoryLargeImageBottom
                : SSizes.homeCategorySmallImageBottom,
            child: Hero(
              tag: title,
              child: Image.asset(
                image,
                height: isLarge
                    ? SSizes.homeCategoryLargeImageHeight
                    : SSizes.homeCategorySmallImageHeight,
                fit: BoxFit.contain,
              ),
            ),
          ),
          Padding(
            padding: const EdgeInsets.all(SSizes.md),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Expanded(
                      child: SizedBox(
                        width: isLarge
                            ? SSizes.homeCategoryLargeTitleWidth
                            : SSizes.homeCategorySmallTitleWidth,
                        child: Text(
                          title,
                          maxLines: 2,
                          overflow: TextOverflow.ellipsis,
                          style: textTheme.titleMedium?.copyWith(
                            fontSize: isLarge
                                ? SSizes.homeCategoryLargeTitleFontSize
                                : SSizes.homeCategorySmallTitleFontSize,
                            fontWeight: FontWeight.w800,
                            height: SSizes.homeCategoryTileTitleHeight,
                            letterSpacing:
                                SSizes.homeCategoryTileTitleLetterSpacing,
                            color: SColors.textPrimary,
                          ),
                        ),
                      ),
                    ),
                    if (showBadge) ...[
                      const SizedBox(width: SSizes.sm),
                      const SCategoryBadge(),
                    ],
                  ],
                ),
                const Spacer(),
                if (subtitle != null)
                  Container(
                    padding: const EdgeInsets.symmetric(
                      horizontal: SSizes.sm,
                      vertical: SSizes.homeCategorySubtitleVerticalPadding,
                    ),
                    decoration: BoxDecoration(
                      color: SHelperFunctions.withOpacity(
                        SColors.success,
                        SOpacities.successTint,
                      ),
                      borderRadius: BorderRadius.circular(SSizes.cardRadiusMd),
                    ),
                    child: Text(
                      subtitle!,
                      style: textTheme.labelLarge?.copyWith(
                        color: SColors.success,
                        fontWeight: FontWeight.w700,
                      ),
                    ),
                  ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
