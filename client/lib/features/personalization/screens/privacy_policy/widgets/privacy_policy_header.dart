import 'package:flutter/material.dart';
import 'package:iconsax/iconsax.dart';

import '../../../../../utils/constants/colors.dart';
import '../../../../../utils/constants/sizes.dart';
import '../../../../../utils/constants/texts.dart';
import '../../../../../utils/helpers/helpers.dart';
import 'privacy_policy_highlight.dart';

class SPrivacyPolicyHeader extends StatelessWidget {
  const SPrivacyPolicyHeader({super.key});

  @override
  Widget build(BuildContext context) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(SSizes.lg),
      decoration: BoxDecoration(
        color: SColors.white,
        borderRadius: BorderRadius.circular(SSizes.privacyPolicyCardRadius),
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
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Container(
                width: SSizes.privacyPolicyHeroIconBoxSize,
                height: SSizes.privacyPolicyHeroIconBoxSize,
                decoration: BoxDecoration(
                  color: SHelperFunctions.withOpacity(
                    SColors.primary,
                    SOpacities.placeholder,
                  ),
                  borderRadius: BorderRadius.circular(SSizes.cardRadiusLg),
                ),
                child: const Icon(
                  Iconsax.security_safe,
                  color: SColors.primary,
                  size: SSizes.privacyPolicyHeroIconSize,
                ),
              ),
              const SizedBox(width: SSizes.md),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      STexts.privacyPolicyTitle,
                      style: Theme.of(context).textTheme.headlineSmall,
                    ),
                    const SizedBox(height: SSizes.xs),
                    Row(
                      children: [
                        Container(
                          width: SSizes.privacyPolicyStatusDotSize,
                          height: SSizes.privacyPolicyStatusDotSize,
                          decoration: const BoxDecoration(
                            color: SColors.success,
                            shape: BoxShape.circle,
                          ),
                        ),
                        const SizedBox(width: SSizes.sm),
                        Flexible(
                          child: Text(
                            '${STexts.privacyPolicyUpdated} - ${STexts.privacyPolicyEffectiveDate}',
                            style: Theme.of(context)
                                .textTheme
                                .bodySmall
                                ?.copyWith(color: SColors.textSecondary),
                            overflow: TextOverflow.ellipsis,
                          ),
                        ),
                      ],
                    ),
                  ],
                ),
              ),
            ],
          ),
          const SizedBox(height: SSizes.md),
          Text(
            STexts.privacyPolicySummary,
            style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                  color: SColors.textSecondary,
                  height: 1.5,
                ),
          ),
          const SizedBox(height: SSizes.md),
          const SPrivacyPolicyHighlight(
            icon: Iconsax.setting_4,
            title: STexts.privacyPolicyDataControl,
            subtitle: STexts.privacyPolicyDataControlSubTitle,
          ),
          const SizedBox(height: SSizes.sm),
          const SPrivacyPolicyHighlight(
            icon: Iconsax.lock_1,
            title: STexts.privacyPolicySecureHandling,
            subtitle: STexts.privacyPolicySecureHandlingSubTitle,
          ),
        ],
      ),
    );
  }
}
