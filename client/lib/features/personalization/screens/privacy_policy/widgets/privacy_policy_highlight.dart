import 'package:flutter/material.dart';

import '../../../../../utils/constants/colors.dart';
import '../../../../../utils/constants/sizes.dart';
import '../../../../../utils/helpers/helpers.dart';

class SPrivacyPolicyHighlight extends StatelessWidget {
  const SPrivacyPolicyHighlight({
    super.key,
    required this.icon,
    required this.title,
    required this.subtitle,
  });

  final IconData icon;
  final String title;
  final String subtitle;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(SSizes.md),
      decoration: BoxDecoration(
        color: SHelperFunctions.withOpacity(
          SColors.primary,
          SOpacities.light,
        ),
        borderRadius: BorderRadius.circular(SSizes.cardRadiusMd),
        border: Border.all(
          color: SHelperFunctions.withOpacity(
            SColors.primary,
            SOpacities.placeholder,
          ),
        ),
      ),
      child: Row(
        children: [
          Icon(icon, color: SColors.primary, size: SSizes.iconMd),
          const SizedBox(width: SSizes.sm),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  title,
                  style: Theme.of(context).textTheme.titleSmall,
                ),
                const SizedBox(height: SSizes.xs),
                Text(
                  subtitle,
                  style: Theme.of(context).textTheme.bodySmall?.copyWith(
                        color: SColors.textSecondary,
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
