import 'package:flutter/material.dart';
import 'package:iconsax/iconsax.dart';

import '../../../../../../../utils/constants/colors.dart';
import '../../../../../../../utils/constants/sizes.dart';
import '../../../../../../../utils/helpers/helpers.dart';

class SSupportRelatedRideCard extends StatelessWidget {
  const SSupportRelatedRideCard({super.key});

  @override
  Widget build(BuildContext context) {
    final textTheme = Theme.of(context).textTheme;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'Select a related ride (optional)',
          style: textTheme.labelLarge?.copyWith(
            color: SColors.textPrimary,
            fontWeight: FontWeight.w800,
          ),
        ),
        const SizedBox(height: SSizes.sm),
        DecoratedBox(
          decoration: BoxDecoration(
            color: SColors.white,
            borderRadius: BorderRadius.circular(SSizes.cardRadiusLg),
            border: Border.all(color: SColors.borderSecondary),
          ),
          child: Padding(
            padding: const EdgeInsets.all(SSizes.md),
            child: Row(
              children: [
                Container(
                  width: 34,
                  height: 34,
                  decoration: BoxDecoration(
                    color: SHelperFunctions.withOpacity(
                      SColors.primary,
                      SOpacities.tinted,
                    ),
                    shape: BoxShape.circle,
                  ),
                  child: const Icon(
                    Iconsax.car,
                    color: SColors.primary,
                    size: SSizes.iconSm,
                  ),
                ),
                const SizedBox(width: SSizes.sm),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'May 20, 2024 - 10:21 AM',
                        style: textTheme.labelMedium?.copyWith(
                          color: SColors.textPrimary,
                          fontWeight: FontWeight.w800,
                        ),
                      ),
                      const SizedBox(height: SSizes.xs),
                      Text(
                        'Main Street, Lahore\nLiberty Market, Lahore',
                        maxLines: 2,
                        overflow: TextOverflow.ellipsis,
                        style: textTheme.labelSmall?.copyWith(
                          color: SColors.textSecondary,
                          height: 1.25,
                          fontWeight: FontWeight.w500,
                        ),
                      ),
                      const SizedBox(height: SSizes.xs),
                      Text(
                        'PKR 320',
                        style: textTheme.labelMedium?.copyWith(
                          color: SColors.textPrimary,
                          fontWeight: FontWeight.w900,
                        ),
                      ),
                    ],
                  ),
                ),
                const Icon(
                  Iconsax.arrow_right_3,
                  color: SColors.textSecondary,
                  size: SSizes.iconSm,
                ),
              ],
            ),
          ),
        ),
      ],
    );
  }
}
