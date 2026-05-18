import 'package:flutter/material.dart';
import 'package:iconsax/iconsax.dart';

import '../../utils/constants/colors.dart';
import '../../utils/constants/sizes.dart';
import '../../utils/helpers/helpers.dart';

class SNotificationCounterIcon extends StatelessWidget {
  const SNotificationCounterIcon({
    super.key,
    required this.onPressed,
    required this.iconColor,
    this.count = 2,
  });

  final Color iconColor;
  final VoidCallback onPressed;
  final int count;

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onPressed,
      child: Container(
        width: SSizes.notificationButtonSize,
        height: SSizes.notificationButtonSize,
        margin: const EdgeInsets.only(right: SSizes.notificationMarginRight),
        decoration: BoxDecoration(
          color: SColors.white,
          borderRadius: BorderRadius.circular(SSizes.notificationButtonRadius),
          border: Border.all(
            color: SHelperFunctions.withOpacity(
              SColors.borderSecondary,
              SOpacities.border,
            ),
          ),
        ),
        child: Stack(
          clipBehavior: Clip.none,
          children: [
            Center(
              child: Icon(
                Iconsax.notification,
                color: iconColor,
                size: SSizes.iconMd,
              ),
            ),
            Positioned(
              top: SSizes.notificationBadgeOffset,
              right: SSizes.notificationBadgeOffset,
              child: Container(
                width: SSizes.notificationBadgeSize,
                height: SSizes.notificationBadgeSize,
                decoration: BoxDecoration(
                  gradient: LinearGradient(
                    colors: [
                      SColors.error,
                      SHelperFunctions.withOpacity(
                        SColors.error,
                        SOpacities.stronger,
                      ),
                    ],
                  ),
                  borderRadius: BorderRadius.circular(SSizes.radiusFull),
                  border: Border.all(
                    color: SColors.white,
                    width: SSizes.notificationBadgeBorderWidth,
                  ),
                ),
                child: Center(
                  child: Text(
                    count.toString(),
                    style: Theme.of(context).textTheme.labelSmall?.copyWith(
                          color: SColors.white,
                          fontWeight: FontWeight.w800,
                          fontSize: SSizes.notificationBadgeFontSize,
                        ),
                  ),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
