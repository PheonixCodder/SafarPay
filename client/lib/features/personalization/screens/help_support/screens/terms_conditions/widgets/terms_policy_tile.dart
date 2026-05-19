import 'package:flutter/material.dart';
import 'package:iconsax/iconsax.dart';

import '../../../../../../../utils/constants/colors.dart';
import '../../../../../../../utils/constants/sizes.dart';
import '../../../../../../../utils/helpers/helpers.dart';
import '../models/terms_policy.dart';

class STermsPolicyTile extends StatelessWidget {
  const STermsPolicyTile({
    super.key,
    required this.policy,
    required this.onTap,
  });

  final STermsPolicy policy;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    final textTheme = Theme.of(context).textTheme;

    return InkWell(
      onTap: onTap,
      child: Padding(
        padding: const EdgeInsets.symmetric(
          horizontal: SSizes.md,
          vertical: SSizes.sm,
        ),
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
                borderRadius: BorderRadius.circular(SSizes.cardRadiusSm),
              ),
              child: Icon(
                policy.icon,
                color: SColors.primary,
                size: SSizes.helpSupportOptionIconSize,
              ),
            ),
            const SizedBox(width: SSizes.md),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    policy.title,
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                    style: textTheme.labelLarge?.copyWith(
                      color: SColors.textPrimary,
                      fontWeight: FontWeight.w800,
                    ),
                  ),
                  const SizedBox(height: SSizes.xs),
                  Text(
                    policy.subtitle,
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                    style: textTheme.labelSmall?.copyWith(
                      color: SColors.textSecondary,
                      fontWeight: FontWeight.w500,
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(width: SSizes.sm),
            const Icon(
              Iconsax.arrow_right_3,
              color: SColors.textSecondary,
              size: SSizes.iconSm,
            ),
          ],
        ),
      ),
    );
  }
}
