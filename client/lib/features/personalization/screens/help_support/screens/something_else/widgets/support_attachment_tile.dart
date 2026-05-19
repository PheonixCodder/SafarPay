import 'package:flutter/material.dart';

import '../../../../../../../utils/constants/colors.dart';
import '../../../../../../../utils/constants/sizes.dart';
import '../../../../../../../utils/helpers/helpers.dart';

class SSupportAttachmentTile extends StatelessWidget {
  const SSupportAttachmentTile({
    super.key,
    required this.icon,
    required this.label,
    required this.isSelected,
    required this.onTap,
  });

  final IconData icon;
  final String label;
  final bool isSelected;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return Expanded(
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(SSizes.cardRadiusLg),
        child: Container(
          padding: const EdgeInsets.symmetric(
            horizontal: SSizes.sm,
            vertical: SSizes.md,
          ),
          decoration: BoxDecoration(
            color: SColors.white,
            borderRadius: BorderRadius.circular(SSizes.cardRadiusLg),
            border: Border.all(
              color: isSelected ? SColors.primary : SColors.borderSecondary,
            ),
          ),
          child: Column(
            children: [
              Container(
                width: 34,
                height: 34,
                decoration: BoxDecoration(
                  color: SHelperFunctions.withOpacity(
                    isSelected ? SColors.success : SColors.primary,
                    SOpacities.tinted,
                  ),
                  borderRadius: BorderRadius.circular(SSizes.cardRadiusSm),
                ),
                child: Icon(
                  icon,
                  color: isSelected ? SColors.success : SColors.primary,
                  size: SSizes.iconMd,
                ),
              ),
              const SizedBox(height: SSizes.sm),
              Text(
                label,
                textAlign: TextAlign.center,
                style: Theme.of(context).textTheme.labelSmall?.copyWith(
                      color: SColors.textPrimary,
                      fontWeight: FontWeight.w800,
                    ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
