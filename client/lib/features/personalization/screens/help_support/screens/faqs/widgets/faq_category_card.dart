import 'package:flutter/material.dart';

import '../../../../../../../utils/constants/colors.dart';
import '../../../../../../../utils/constants/sizes.dart';
import '../models/faq_models.dart';
import 'faq_category_tile.dart';

class SFaqCategoryCard extends StatelessWidget {
  const SFaqCategoryCard({
    super.key,
    required this.categories,
    required this.onCategorySelected,
  });

  final List<SFaqCategory> categories;
  final ValueChanged<SFaqCategory> onCategorySelected;

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
            for (var index = 0; index < categories.length; index++) ...[
              SFaqCategoryTile(
                category: categories[index],
                onTap: () => onCategorySelected(categories[index]),
              ),
              if (index != categories.length - 1)
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
