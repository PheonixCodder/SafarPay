import 'package:flutter/material.dart';

import '../../../../../utils/constants/colors.dart';
import '../../../../../utils/constants/sizes.dart';
import '../../../../../utils/helpers/helpers.dart';
import '../notification_item.dart';

class SNotificationTimelineItem extends StatelessWidget {
  const SNotificationTimelineItem({
    super.key,
    required this.item,
  });

  final SNotificationItem item;

  @override
  Widget build(BuildContext context) {
    final accentColor = _accentColor(item.type);

    return Container(
      padding: const EdgeInsets.all(SSizes.md),
      decoration: BoxDecoration(
        color: SColors.white,
        borderRadius: BorderRadius.circular(SSizes.notificationTileRadius),
        border: Border.all(color: SColors.borderSecondary),
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Stack(
            clipBehavior: Clip.none,
            children: [
              Container(
                width: SSizes.notificationTimelineIconBoxSize,
                height: SSizes.notificationTimelineIconBoxSize,
                decoration: BoxDecoration(
                  color: SHelperFunctions.withOpacity(
                    accentColor,
                    SOpacities.placeholder,
                  ),
                  borderRadius: BorderRadius.circular(SSizes.cardRadiusMd),
                ),
                child: Icon(
                  item.icon,
                  color: accentColor,
                  size: SSizes.notificationTimelineIconSize,
                ),
              ),
              if (item.isUnread)
                Positioned(
                  right: -SSizes.xs,
                  top: -SSizes.xs,
                  child: Container(
                    width: SSizes.notificationUnreadDotSize,
                    height: SSizes.notificationUnreadDotSize,
                    decoration: BoxDecoration(
                      color: SColors.primary,
                      shape: BoxShape.circle,
                      border: Border.all(color: SColors.white, width: 2),
                    ),
                  ),
                ),
            ],
          ),
          const SizedBox(width: SSizes.md),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Expanded(
                      child: Text(
                        item.title,
                        style: Theme.of(context)
                            .textTheme
                            .titleMedium
                            ?.copyWith(fontWeight: FontWeight.w700),
                      ),
                    ),
                    const SizedBox(width: SSizes.sm),
                    Text(
                      item.timeAgo,
                      style: Theme.of(context).textTheme.bodySmall?.copyWith(
                            color: SColors.textSecondary,
                          ),
                    ),
                  ],
                ),
                const SizedBox(height: SSizes.xs),
                Text(
                  item.message,
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

  Color _accentColor(SNotificationType type) {
    return switch (type) {
      SNotificationType.trip => SColors.primary,
      SNotificationType.payment => SColors.success,
      SNotificationType.offer => SColors.warning,
      SNotificationType.safety => SColors.info,
      SNotificationType.system => SColors.secondary,
    };
  }
}
