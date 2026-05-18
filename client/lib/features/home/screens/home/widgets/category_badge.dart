import 'package:client/utils/constants/colors.dart';
import 'package:client/utils/constants/sizes.dart';
import 'package:client/utils/constants/texts.dart';
import 'package:client/utils/helpers/helpers.dart';
import 'package:flutter/material.dart';

class SCategoryBadge extends StatelessWidget {
  const SCategoryBadge({super.key});

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(
        horizontal: SSizes.sm,
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
        style: Theme.of(context).textTheme.labelSmall?.copyWith(
              color: SColors.textWhite,
              fontWeight: FontWeight.w800,
              letterSpacing: SSizes.homeCategoryBadgeLetterSpacing,
            ),
      ),
    );
  }
}
