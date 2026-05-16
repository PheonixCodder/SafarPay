import 'package:flutter/material.dart';
import 'package:iconsax/iconsax.dart';

import '../../../../../utils/constants/colors.dart';
import '../../../../../utils/constants/sizes.dart';
import '../../../../../utils/constants/texts.dart';
import '../../../../../utils/helpers/helpers.dart';

class SNotificationsEmptyState extends StatelessWidget {
  const SNotificationsEmptyState({super.key});

  @override
  Widget build(BuildContext context) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(SSizes.lg),
      decoration: BoxDecoration(
        color: SHelperFunctions.withOpacity(
          SColors.primary,
          SOpacities.light,
        ),
        borderRadius: BorderRadius.circular(SSizes.notificationTileRadius),
      ),
      child: Column(
        children: [
          const Icon(
            Iconsax.notification_bing,
            color: SColors.primary,
            size: SSizes.iconLg,
          ),
          const SizedBox(height: SSizes.sm),
          Text(
            STexts.notificationsEmptyTitle,
            style: Theme.of(context).textTheme.titleMedium,
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: SSizes.xs),
          Text(
            STexts.notificationsEmptySubTitle,
            style: Theme.of(context).textTheme.bodySmall?.copyWith(
                  color: SColors.textSecondary,
                  height: 1.4,
                ),
            textAlign: TextAlign.center,
          ),
        ],
      ),
    );
  }
}
