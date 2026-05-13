import 'package:flutter/material.dart';
import 'package:iconsax/iconsax.dart';

import '../../../../../utils/constants/colors.dart';
import '../../../../../utils/constants/sizes.dart';
import '../../../../../utils/constants/texts.dart';

class SProfileHeader extends StatelessWidget {
  const SProfileHeader({super.key});

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        Container(
          width: 72,
          height: 72,
          decoration: BoxDecoration(
            color: SColors.primary.withOpacity(0.12),
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
          widthFactor: 0.9,
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
