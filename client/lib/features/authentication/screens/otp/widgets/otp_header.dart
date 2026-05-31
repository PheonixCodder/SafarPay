import 'package:flutter/material.dart';

import '../../../../../utils/constants/colors.dart';
import '../../../../../utils/constants/sizes.dart';
import '../../../../../utils/constants/texts.dart';
import '../../../controllers/otp.dart';

class SOtpHeader extends StatelessWidget {
  const SOtpHeader({
    super.key,
    required this.controller,
  });

  final SOtpController controller;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context).textTheme;

    final title = controller.isGooglePhoneLink && controller.hasDisplayName
        ? '${STexts.googleOtpTitlePrefix} ${controller.displayName}!'
        : 'We just sent\nan SMS';

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          title,
          textAlign: TextAlign.left,
          style: theme.displaySmall?.copyWith(
                color: SColors.textPrimary,
                fontWeight: FontWeight.w800,
                letterSpacing: -0.5,
              )
        ),
        const SizedBox(height: SSizes.sm),
        Text(
          'Enter the six-digit security code we sent to ${controller.phoneDisplay}.',
          textAlign: TextAlign.left,
          style: theme.bodyMedium?.copyWith(
                color: SColors.textSecondary,
                height: 1.45,
              ) ??
              const TextStyle(
                color: SColors.textSecondary,
                fontSize: 15,
                height: 1.45,
              ),
        ),
      ],
    );
  }
}
