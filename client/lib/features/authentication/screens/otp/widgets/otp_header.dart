import 'package:flutter/material.dart';
import 'package:iconsax/iconsax.dart';

import '../../../../../utils/constants/colors.dart';
import '../../../../../utils/constants/sizes.dart';
import '../../../../../utils/constants/texts.dart';
import '../../../../../utils/helpers/helpers.dart';
import '../../../controllers/otp.dart';

class SOtpHeader extends StatelessWidget {
  const SOtpHeader({
    super.key,
    required this.controller,
  });

  final SOtpController controller;

  @override
  Widget build(BuildContext context) {
    final title = controller.isGooglePhoneLink && controller.hasDisplayName
        ? '${STexts.googleOtpTitlePrefix} ${controller.displayName}, ${STexts.otpTitle.toLowerCase()}'
        : STexts.otpTitle;

    return Column(
      children: [
        Container(
          width: SSizes.authHeaderIconBoxSize,
          height: SSizes.authHeaderIconBoxSize,
          decoration: BoxDecoration(
            color: SHelperFunctions.withOpacity(
              SColors.primary,
              SOpacities.placeholder,
            ),
            borderRadius: BorderRadius.circular(SSizes.cardRadiusLg),
          ),
          child: const Icon(
            Iconsax.message_text,
            color: SColors.primary,
            size: SSizes.iconLg,
          ),
        ),
        const SizedBox(height: SSizes.defaultSpace),
        Text(
          title,
          textAlign: TextAlign.center,
          style: Theme.of(context).textTheme.headlineLarge?.copyWith(
                color: SColors.textPrimary,
              ),
        ),
        const SizedBox(height: SSizes.sm),
        FractionallySizedBox(
          widthFactor: SSizes.authHeaderSubtitleWidthFactor,
          child: Text(
            '${STexts.otpSubTitle} ${controller.phoneNumber}.',
            textAlign: TextAlign.center,
            style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                  color: SColors.textSecondary,
                ),
          ),
        ),
        const SizedBox(height: SSizes.md),
        TextButton(
          onPressed: controller.changeNumber,
          child: const Text(STexts.changeNumber),
        ),
      ],
    );
  }
}
