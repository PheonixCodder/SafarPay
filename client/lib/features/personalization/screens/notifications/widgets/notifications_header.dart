import 'package:flutter/material.dart';
import 'package:iconsax/iconsax.dart';

import '../../../../../utils/constants/colors.dart';
import '../../../../../utils/constants/sizes.dart';
import '../../../../../utils/constants/texts.dart';
import '../../../../../utils/helpers/helpers.dart';

class SNotificationsHeader extends StatelessWidget {
  const SNotificationsHeader({
    super.key,
    required this.totalCount,
    required this.unreadCount,
  });

  final int totalCount;
  final int unreadCount;

  @override
  Widget build(BuildContext context) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(SSizes.lg),
      decoration: BoxDecoration(
        color: SColors.white,
        borderRadius: BorderRadius.circular(SSizes.notificationHeaderRadius),
        border: Border.all(color: SColors.borderSecondary),
        boxShadow: [
          BoxShadow(
            color: SHelperFunctions.withOpacity(
              SColors.pureBlack,
              SOpacities.soft,
            ),
            blurRadius: SSizes.shadowBlurLg,
            offset: const Offset(0, SSizes.shadowOffsetYMd),
          ),
        ],
      ),
      child: Row(
        children: [
          Container(
            width: SSizes.notificationHeroIconBoxSize,
            height: SSizes.notificationHeroIconBoxSize,
            decoration: BoxDecoration(
              color: SHelperFunctions.withOpacity(
                SColors.primary,
                SOpacities.placeholder,
              ),
              borderRadius: BorderRadius.circular(SSizes.cardRadiusLg),
            ),
            child: const Icon(
              Iconsax.notification,
              color: SColors.primary,
              size: SSizes.notificationHeroIconSize,
            ),
          ),
          const SizedBox(width: SSizes.md),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  unreadCount == 0
                      ? STexts.notificationsAllCaughtUp
                      : '$unreadCount ${STexts.notificationsNewUpdates}',
                  style: Theme.of(context).textTheme.headlineSmall,
                ),
                const SizedBox(height: SSizes.xs),
                Text(
                  '$totalCount ${STexts.notificationsInboxSummary}',
                  style: Theme.of(context).textTheme.bodySmall?.copyWith(
                        color: SColors.textSecondary,
                        height: 1.4,
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
