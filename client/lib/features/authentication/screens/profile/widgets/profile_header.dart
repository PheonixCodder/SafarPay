import 'package:flutter/material.dart';
import 'package:iconsax/iconsax.dart';

import '../../../../../utils/constants/colors.dart';
import '../../../../../utils/constants/sizes.dart';
import '../../../../../utils/constants/texts.dart';
import '../../../../../utils/helpers/helpers.dart';

class SProfileHeader extends StatelessWidget {
  const SProfileHeader({super.key});

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        Container(
          width: SSizes.authHeaderIconBoxSize,
          height: SSizes.authHeaderIconBoxSize,
          decoration: BoxDecoration(
            color: SHelperFunctions.withOpacity(
              SColors.primary,
              SOpacities.placeholder,
            ),
            borderRadius: BorderRadius.circular(SSizes.cardRadiusLg),
          ),
          child: const Icon(
            Iconsax.user_edit,
            color: SColors.primary,
            size: SSizes.iconLg,
          ),
        ),
        const SizedBox(height: SSizes.defaultSpace),
        Text(
          STexts.completeProfileTitle,
          textAlign: TextAlign.center,
          style: Theme.of(context).textTheme.headlineLarge?.copyWith(
                color: SColors.textPrimary,
              ),
        ),
        const SizedBox(height: SSizes.sm),
        FractionallySizedBox(
          widthFactor: SSizes.authHeaderSubtitleWidthFactor,
          child: Text(
            STexts.completeProfileSubTitle,
            textAlign: TextAlign.center,
            style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                  color: SColors.textSecondary,
                ),
          ),
        ),
      ],
    );
  }
}
