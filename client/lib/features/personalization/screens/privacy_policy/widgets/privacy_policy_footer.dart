import 'package:flutter/material.dart';
import 'package:iconsax/iconsax.dart';

import '../../../../../utils/constants/colors.dart';
import '../../../../../utils/constants/sizes.dart';
import '../../../../../utils/constants/texts.dart';
import '../../../../../utils/helpers/helpers.dart';

class SPrivacyPolicyFooter extends StatelessWidget {
  const SPrivacyPolicyFooter({super.key});

  @override
  Widget build(BuildContext context) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(SSizes.md),
      decoration: BoxDecoration(
        color: SHelperFunctions.withOpacity(
          SColors.primary,
          SOpacities.light,
        ),
        borderRadius: BorderRadius.circular(SSizes.privacyPolicyTileRadius),
      ),
      child: Row(
        children: [
          Container(
            width: SSizes.privacyPolicyFooterIconBoxSize,
            height: SSizes.privacyPolicyFooterIconBoxSize,
            decoration: BoxDecoration(
              color: SColors.white,
              borderRadius: BorderRadius.circular(SSizes.cardRadiusMd),
            ),
            child: const Icon(
              Iconsax.message_question,
              color: SColors.primary,
              size: SSizes.privacyPolicyFooterIconSize,
            ),
          ),
          const SizedBox(width: SSizes.md),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  STexts.privacyPolicyContactTitle,
                  style: Theme.of(context).textTheme.titleMedium,
                ),
                const SizedBox(height: SSizes.xs),
                Text(
                  STexts.privacyPolicyContactSubTitle,
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
