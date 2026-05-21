import 'package:flutter/material.dart';
import 'package:iconsax/iconsax.dart';

import '../../../../../utils/constants/colors.dart';
import '../../../../../utils/constants/sizes.dart';
import 'driver_registration_option_image_tile.dart';

class SDriverRegistrationOptionTile extends StatelessWidget {
  const SDriverRegistrationOptionTile({
    super.key,
    required this.title,
    required this.image,
    this.subtitle,
    this.onTap,
    this.compact = false,
    this.isCompleted = false,
  });

  final String title;
  final String? subtitle;
  final String image;
  final VoidCallback? onTap;
  final bool compact;
  final bool isCompleted;

  @override
  Widget build(BuildContext context) {
    final textTheme = Theme.of(context).textTheme;

    return Material(
      color: SColors.white,
      borderRadius: BorderRadius.circular(SSizes.cardRadiusLg),
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(SSizes.cardRadiusLg),
        child: Padding(
          padding: EdgeInsets.symmetric(
            horizontal: SSizes.md,
            vertical: compact ? SSizes.md : SSizes.lg,
          ),
          child: Row(
            children: [
              SDriverRegistrationOptionImageTile(
                image: image,
                compact: compact,
              ),
              const SizedBox(width: SSizes.md),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      title,
                      style: textTheme.titleLarge?.copyWith(
                        color: SColors.textPrimary,
                        fontWeight: FontWeight.w700,
                      ),
                    ),
                    if (subtitle != null) ...[
                      const SizedBox(height: SSizes.xs),
                      Text(
                        subtitle!,
                        maxLines: 2,
                        overflow: TextOverflow.ellipsis,
                        style: textTheme.bodyMedium?.copyWith(
                          color: SColors.textSecondary,
                          height: 1.3,
                        ),
                      ),
                    ],
                  ],
                ),
              ),
              const SizedBox(width: SSizes.sm),
              Icon(
                isCompleted ? Iconsax.tick_circle : Iconsax.arrow_right_3,
                color: isCompleted ? SColors.success : SColors.textSecondary,
                size: SSizes.iconMd,
              ),
            ],
          ),
        ),
      ),
    );
  }
}
