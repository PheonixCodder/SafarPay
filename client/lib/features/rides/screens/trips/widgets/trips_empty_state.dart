import 'package:flutter/material.dart';
import 'package:iconsax/iconsax.dart';

import '../../../../../utils/constants/colors.dart';
import '../../../../../utils/constants/sizes.dart';
import '../../../../../utils/constants/texts.dart';
import '../../../../../utils/helpers/helpers.dart';

class STripsEmptyState extends StatelessWidget {
  const STripsEmptyState({
    super.key,
    required this.title,
  });

  final String title;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: SSizes.spaceBtwSections),
      child: Column(
        children: [
          Container(
            width: SSizes.tripsEmptyIconBoxSize,
            height: SSizes.tripsEmptyIconBoxSize,
            decoration: BoxDecoration(
              color: SHelperFunctions.withOpacity(
                SColors.primary,
                SOpacities.placeholder,
              ),
              shape: BoxShape.circle,
            ),
            child: const Icon(
              Iconsax.clock,
              color: SColors.primary,
              size: SSizes.iconLg,
            ),
          ),
          const SizedBox(height: SSizes.md),
          Text(title, style: Theme.of(context).textTheme.titleMedium),
          const SizedBox(height: SSizes.xs),
          Text(
            STexts.tripsEmptySubTitle,
            style: Theme.of(context).textTheme.bodySmall?.copyWith(
                  color: SColors.textSecondary,
                ),
            textAlign: TextAlign.center,
          ),
        ],
      ),
    );
  }
}
