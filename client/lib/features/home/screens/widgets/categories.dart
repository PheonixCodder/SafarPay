import 'package:flutter/material.dart';

import '../../../../utils/constants/colors.dart';
import '../../../../utils/constants/images.dart';
import '../../../../utils/constants/sizes.dart';
import '../../../../utils/constants/texts.dart';
import '../../../../utils/helpers/helpers.dart';
import 'category_tile.dart';

class SHomeCategories extends StatelessWidget {
  const SHomeCategories({super.key});

  @override
  Widget build(BuildContext context) {
    const gap = SSizes.md;
    final textTheme = Theme.of(context).textTheme;

    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: SSizes.lg),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Expanded(
                child: Text(
                  STexts.categories,
                  style: textTheme.headlineSmall?.copyWith(
                    fontWeight: FontWeight.w800,
                    color: SColors.textPrimary,
                    letterSpacing: SSizes.homeCategoryTitleLetterSpacing,
                  ),
                ),
              ),
              Container(
                padding: const EdgeInsets.symmetric(
                  horizontal: SSizes.md,
                  vertical: SSizes.sm,
                ),
                decoration: BoxDecoration(
                  color: SHelperFunctions.withOpacity(
                    SColors.primary,
                    SOpacities.tinted,
                  ),
                  borderRadius: BorderRadius.circular(SSizes.cardRadiusLg),
                ),
                child: Text(
                  STexts.categoriesExplore,
                  style: textTheme.labelMedium?.copyWith(
                    color: SColors.primary,
                    fontWeight: FontWeight.w700,
                  ),
                ),
              ),
            ],
          ),

          const SizedBox(height: SSizes.lg),

          /// TOP GRID
          SizedBox(
            height: SSizes.homeCategoryTopGridHeight,
            child: Row(
              children: [
                const Expanded(
                  flex: 6,
                  child: SCategoryTile(
                    title: STexts.groceries,
                    subtitle: STexts.groceriesEta,
                    image: SImages.groceries,
                    isLarge: true,
                    showBadge: true,
                  ),
                ),

                const SizedBox(width: gap),

                Expanded(
                  flex: 4,
                  child: Column(
                    children: const [
                      Expanded(
                        child: SCategoryTile(
                          title: STexts.cityRides,
                          image: SImages.cityRides,
                        ),
                      ),
                      SizedBox(height: gap),
                      Expanded(
                        child: SCategoryTile(
                          title: STexts.cityToCity,
                          image: SImages.cityToCity,
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),

          const SizedBox(height: gap),

          /// BOTTOM GRID
          SizedBox(
            height: SSizes.homeCategoryBottomGridHeight,
            child: Row(
              children: const [
                Expanded(
                  child: SCategoryTile(
                    title: STexts.courier,
                    image: SImages.courier,
                  ),
                ),
                SizedBox(width: gap),
                Expanded(
                  child: SCategoryTile(
                    title: STexts.freight,
                    image: SImages.freight,
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
