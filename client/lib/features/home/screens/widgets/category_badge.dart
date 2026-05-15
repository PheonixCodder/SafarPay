import 'package:flutter/material.dart';

import '../../../../utils/constants/colors.dart';
import '../../../../utils/constants/sizes.dart';
import '../../../../utils/constants/texts.dart';
import '../../../../utils/helpers/helpers.dart';

class SCategoryBadge extends StatelessWidget {
  const SCategoryBadge({super.key});

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(
        horizontal: SSizes.md,
        vertical: SSizes.homeCategoryBadgeVerticalPadding,
      ),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: [
            SColors.error,
            SHelperFunctions.withOpacity(SColors.error, SOpacities.strong),
          ],
        ),
        borderRadius: BorderRadius.circular(SSizes.radiusFull),
        boxShadow: [
          BoxShadow(
            color: SHelperFunctions.withOpacity(
              SColors.error,
              SOpacities.shadow,
            ),
            blurRadius: SSizes.homeCategoryBadgeShadowBlur,
            offset: const Offset(0, SSizes.homeCategoryBadgeShadowOffsetY),
          ),
        ],
      ),
      child: Text(
        STexts.categoryNew,
        style: Theme.of(context).textTheme.labelMedium?.copyWith(
              color: SColors.textWhite,
              fontWeight: FontWeight.w800,
              letterSpacing: SSizes.homeCategoryBadgeLetterSpacing,
            ),
      ),
    );
  }
}
