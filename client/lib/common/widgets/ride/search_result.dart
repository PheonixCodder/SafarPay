import 'package:flutter/material.dart';

import '../../../utils/constants/colors.dart';
import '../../../utils/constants/sizes.dart';
import '../../../utils/helpers/helpers.dart';

class SSearchResult extends StatelessWidget {
  const SSearchResult({
    super.key,
    required this.icon,
    required this.title,
    required this.address,
    required this.duration,
    this.onTap,
    this.showDivider = true,
  });

  final IconData icon;
  final String title;
  final String address;
  final String duration;
  final VoidCallback? onTap;
  final bool showDivider;

  @override
  Widget build(BuildContext context) {
    final textTheme = Theme.of(context).textTheme;

    final content = Padding(
      padding: const EdgeInsets.symmetric(
        horizontal: SSizes.lg,
        vertical: SSizes.md,
      ),
      child: Column(
        children: [
          Row(
            crossAxisAlignment: CrossAxisAlignment.center,
            children: [
              /// ICON
              Container(
                width: SSizes.rideSearchIconBoxSize,
                height: SSizes.rideSearchIconBoxSize,
                decoration: BoxDecoration(
                  color: SColors.lightContainer,
                  borderRadius: BorderRadius.circular(SSizes.cardRadiusLg),
                ),
                child: Icon(
                  icon,
                  color: SColors.primary,
                  size: SSizes.rideSearchIconSize,
                ),
              ),

              const SizedBox(width: SSizes.md),

              /// TEXTS
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Text(
                      title,
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                      style: textTheme.titleLarge?.copyWith(
                        color: SColors.textPrimary,
                        fontWeight: FontWeight.w800,
                        letterSpacing: SSizes.rideSearchTitleLetterSpacing,
                      ),
                    ),
                    const SizedBox(height: SSizes.rideSearchTextGap),
                    Text(
                      address,
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                      style: textTheme.bodyMedium?.copyWith(
                        color: SColors.textSecondary,
                        height: SSizes.rideSearchAddressTextHeight,
                      ),
                    ),
                  ],
                ),
              ),

              const SizedBox(width: SSizes.md),

              /// DURATION
              Container(
                padding: const EdgeInsets.symmetric(
                  horizontal: SSizes.md,
                  vertical: SSizes.rideSearchDurationVerticalPadding,
                ),
                decoration: BoxDecoration(
                  color: SHelperFunctions.withOpacity(
                    SColors.primary,
                    SOpacities.tinted,
                  ),
                  borderRadius: BorderRadius.circular(SSizes.radiusFull),
                ),
                child: Text(
                  duration,
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                  textAlign: TextAlign.right,
                  style: textTheme.labelLarge?.copyWith(
                    color: SColors.primary,
                    fontWeight: FontWeight.w800,
                  ),
                ),
              ),
            ],
          ),
          if (showDivider)
            Padding(
              padding: const EdgeInsets.only(
                left: SSizes.rideSearchDividerLeftPadding,
                top: SSizes.md,
              ),
              child: Divider(
                height: SSizes.dividerHeight,
                thickness: SSizes.dividerHeight,
                color: SHelperFunctions.withOpacity(
                  SColors.borderSecondary,
                  SOpacities.divider,
                ),
              ),
            ),
        ],
      ),
    );

    if (onTap == null) return content;

    return Material(
      color: SColors.transparent,
      child: InkWell(
        borderRadius: BorderRadius.circular(SSizes.rideSearchInkRadius),
        onTap: onTap,
        splashColor:
            SHelperFunctions.withOpacity(SColors.primary, SOpacities.light),
        highlightColor:
            SHelperFunctions.withOpacity(SColors.primary, SOpacities.subtle),
        child: content,
      ),
    );
  }
}
