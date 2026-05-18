import 'package:client/utils/constants/colors.dart';
import 'package:client/utils/constants/sizes.dart';
import 'package:client/utils/constants/texts.dart';
import 'package:client/utils/helpers/helpers.dart';
import 'package:flutter/material.dart';
import 'package:iconsax/iconsax.dart';

class SSelfieHeader extends StatelessWidget {
  const SSelfieHeader({
    super.key,
    required this.subtitle,
  });

  final String subtitle;

  @override
  Widget build(BuildContext context) {
    final textTheme = Theme.of(context).textTheme;

    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(SSizes.lg),
      decoration: BoxDecoration(
        color: SColors.white,
        borderRadius: BorderRadius.circular(SSizes.cardRadiusLg),
        border: Border.all(color: SColors.borderSecondary),
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Container(
            width: 48,
            height: 48,
            decoration: BoxDecoration(
              color: SHelperFunctions.withOpacity(
                SColors.primary,
                SOpacities.tinted,
              ),
              borderRadius: BorderRadius.circular(SSizes.cardRadiusMd),
            ),
            child: const Icon(Iconsax.camera, color: SColors.primary),
          ),
          const SizedBox(width: SSizes.md),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  STexts.driverRegistrationSelfieTitle,
                  style: textTheme.titleLarge?.copyWith(
                    color: SColors.textPrimary,
                    fontWeight: FontWeight.w800,
                  ),
                ),
                const SizedBox(height: SSizes.xs),
                Text(
                  subtitle,
                  style: textTheme.bodySmall?.copyWith(
                    color: SColors.primary,
                    fontWeight: FontWeight.w700,
                  ),
                ),
                const SizedBox(height: SSizes.sm),
                Text(
                  STexts.driverRegistrationSelfieCapture,
                  style: textTheme.bodyMedium?.copyWith(
                    color: SColors.textSecondary,
                    height: 1.35,
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
