import 'package:flutter/material.dart';
import 'package:iconsax/iconsax.dart';

import '../../../../../utils/constants/colors.dart';
import '../../../../../utils/constants/sizes.dart';

class SRequestsEmptyState extends StatelessWidget {
  const SRequestsEmptyState({
    super.key,
    required this.title,
    required this.subtitle,
  });

  final String title;
  final String subtitle;

  @override
  Widget build(BuildContext context) {
    final textTheme = Theme.of(context).textTheme;

    return DecoratedBox(
      decoration: BoxDecoration(
        color: SColors.white,
        borderRadius: BorderRadius.circular(SSizes.cardRadiusMd),
        border: Border.all(color: SColors.borderSecondary),
      ),
      child: Padding(
        padding: const EdgeInsets.all(SSizes.xl),
        child: Column(
          children: [
            const Icon(
              Iconsax.routing_2,
              color: SColors.primary,
              size: 38,
            ),
            const SizedBox(height: SSizes.md),
            Text(
              title,
              style: textTheme.titleLarge?.copyWith(
                fontWeight: FontWeight.w900,
              ),
            ),
            const SizedBox(height: SSizes.xs),
            Text(
              subtitle,
              textAlign: TextAlign.center,
              style: textTheme.bodyMedium?.copyWith(
                color: SColors.textSecondary,
              ),
            ),
          ],
        ),
      ),
    );
  }
}
