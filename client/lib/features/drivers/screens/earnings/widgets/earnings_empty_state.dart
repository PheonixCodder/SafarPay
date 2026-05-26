import 'package:flutter/material.dart';
import 'package:iconsax/iconsax.dart';

import '../../../../../utils/constants/colors.dart';
import '../../../../../utils/constants/sizes.dart';
import '../../../../../utils/constants/texts.dart';
import '../../../../../utils/helpers/helpers.dart';

class SEarningsEmptyState extends StatelessWidget {
  const SEarningsEmptyState({super.key, required this.message});

  final String message;

  @override
  Widget build(BuildContext context) {
    return ListView(
      padding: const EdgeInsets.all(SSizes.defaultSpace),
      children: [
        const SizedBox(height: 120),
        Center(
          child: Container(
            width: SSizes.tripsEmptyIconBoxSize,
            height: SSizes.tripsEmptyIconBoxSize,
            decoration: BoxDecoration(
              color: SHelperFunctions.withOpacity(
                SColors.primary,
                SOpacities.tinted,
              ),
              borderRadius: BorderRadius.circular(SSizes.borderRadiusLg),
            ),
            child: const Icon(
              Iconsax.wallet_3,
              color: SColors.primary,
              size: SSizes.iconLg,
            ),
          ),
        ),
        const SizedBox(height: SSizes.md),
        Text(
          STexts.earningsEmptyTitle,
          textAlign: TextAlign.center,
          style: Theme.of(context).textTheme.titleLarge?.copyWith(
                fontWeight: FontWeight.w800,
              ),
        ),
        const SizedBox(height: SSizes.sm),
        Text(
          message.isEmpty ? STexts.earningsEmptySubTitle : message,
          textAlign: TextAlign.center,
          style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                color: SColors.textSecondary,
              ),
        ),
      ],
    );
  }
}
