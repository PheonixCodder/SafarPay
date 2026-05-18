import 'package:flutter/material.dart';
import 'package:iconsax/iconsax.dart';

import '../../../../../utils/constants/colors.dart';
import '../../../../../utils/constants/sizes.dart';
import '../../../../../utils/helpers/helpers.dart';
import '../controllers/driver_verification_controller.dart';

class SVerificationStepCard extends StatelessWidget {
  const SVerificationStepCard({
    super.key,
    required this.step,
    this.onTap,
  });

  final SVerificationStepViewData step;
  final VoidCallback? onTap;

  @override
  Widget build(BuildContext context) {
    final textTheme = Theme.of(context).textTheme;
    final enabled = step.isEnabled && onTap != null;

    return Material(
      color: SColors.white,
      borderRadius: BorderRadius.circular(SSizes.cardRadiusLg),
      child: InkWell(
        onTap: enabled ? onTap : null,
        borderRadius: BorderRadius.circular(SSizes.cardRadiusLg),
        child: Container(
          padding: const EdgeInsets.all(SSizes.md),
          decoration: BoxDecoration(
            border: Border.all(color: SColors.borderSecondary),
            borderRadius: BorderRadius.circular(SSizes.cardRadiusLg),
          ),
          child: Row(
            children: [
              Container(
                width: 42,
                height: 42,
                decoration: BoxDecoration(
                  color: SHelperFunctions.withOpacity(
                    step.iconColor,
                    SOpacities.tinted,
                  ),
                  borderRadius: BorderRadius.circular(SSizes.cardRadiusMd),
                ),
                child: Icon(
                  step.icon,
                  color: step.iconColor,
                  size: SSizes.iconMd,
                ),
              ),
              const SizedBox(width: SSizes.md),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      step.title,
                      style: textTheme.titleMedium?.copyWith(
                        color: SColors.textPrimary,
                        fontWeight: FontWeight.w700,
                      ),
                    ),
                    if (step.supportingText != null) ...[
                      const SizedBox(height: SSizes.xs),
                      Text(
                        step.supportingText!,
                        maxLines: 2,
                        overflow: TextOverflow.ellipsis,
                        style: textTheme.bodySmall?.copyWith(
                          color: step.iconColor,
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                    ],
                  ],
                ),
              ),
              Icon(
                enabled ? Iconsax.arrow_right_3 : Iconsax.lock_1,
                color: enabled ? SColors.textSecondary : SColors.borderPrimary,
                size: SSizes.iconMd,
              ),
            ],
          ),
        ),
      ),
    );
  }
}
