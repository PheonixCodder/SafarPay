import 'package:flutter/material.dart';
import 'package:iconsax/iconsax.dart';

import '../../../../../utils/constants/colors.dart';
import '../../../../../utils/constants/sizes.dart';
import '../../../../../utils/constants/texts.dart';
import '../../../../../utils/helpers/helpers.dart';

class SGooglePhoneLinkHeader extends StatelessWidget {
  const SGooglePhoneLinkHeader({
    super.key,
    required this.displayName,
    this.email,
  });

  final String displayName;
  final String? email;

  @override
  Widget build(BuildContext context) {
    final emailText = email?.trim();

    return Column(
      children: [
        Container(
          width: SSizes.googlePhoneLinkIconBoxSize,
          height: SSizes.googlePhoneLinkIconBoxSize,
          decoration: BoxDecoration(
            color: SHelperFunctions.withOpacity(
              SColors.primary,
              SOpacities.placeholder,
            ),
            borderRadius: BorderRadius.circular(SSizes.cardRadiusLg),
          ),
          child: const Icon(
            Iconsax.user_edit,
            color: SColors.primary,
            size: SSizes.iconLg,
          ),
        ),
        const SizedBox(height: SSizes.defaultSpace),
        Text(
          STexts.googlePhoneLinkTitle,
          textAlign: TextAlign.center,
          style: Theme.of(context).textTheme.headlineLarge?.copyWith(
                color: SColors.textPrimary,
              ),
        ),
        const SizedBox(height: SSizes.sm),
        FractionallySizedBox(
          widthFactor: SSizes.googlePhoneLinkSubtitleWidthFactor,
          child: Text(
            STexts.googlePhoneLinkSubTitle,
            textAlign: TextAlign.center,
            style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                  color: SColors.textSecondary,
                ),
          ),
        ),
        const SizedBox(height: SSizes.defaultSpace),
        Container(
          width: double.infinity,
          padding: const EdgeInsets.all(SSizes.md),
          decoration: BoxDecoration(
            color: SColors.white,
            border: Border.all(color: SColors.borderSecondary),
            borderRadius: BorderRadius.circular(SSizes.cardRadiusMd),
          ),
          child: Row(
            children: [
              Container(
                width: SSizes.googlePhoneLinkUserIconBoxSize,
                height: SSizes.googlePhoneLinkUserIconBoxSize,
                decoration: BoxDecoration(
                  color: SHelperFunctions.withOpacity(
                    SColors.primary,
                    SOpacities.successTint,
                  ),
                  borderRadius: BorderRadius.circular(SSizes.cardRadiusSm),
                ),
                child: const Icon(
                  Iconsax.user,
                  color: SColors.primary,
                  size: SSizes.iconMd,
                ),
              ),
              const SizedBox(width: SSizes.md),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      displayName,
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                      style: Theme.of(context).textTheme.titleMedium?.copyWith(
                            color: SColors.textPrimary,
                            fontWeight: FontWeight.w700,
                          ),
                    ),
                    if (emailText != null && emailText.isNotEmpty) ...[
                      const SizedBox(height: SSizes.xs),
                      Text(
                        emailText,
                        maxLines: 1,
                        overflow: TextOverflow.ellipsis,
                        style: Theme.of(context).textTheme.bodySmall?.copyWith(
                              color: SColors.textSecondary,
                            ),
                      ),
                    ],
                  ],
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }
}
