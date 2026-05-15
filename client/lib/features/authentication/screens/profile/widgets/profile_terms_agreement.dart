import 'package:flutter/material.dart';
import 'package:get/get.dart';

import '../../../../../utils/constants/colors.dart';
import '../../../../../utils/constants/sizes.dart';
import '../../../../../utils/constants/texts.dart';
import '../../../controllers/profile.dart';

class SProfileTermsAgreement extends StatelessWidget {
  const SProfileTermsAgreement({
    super.key,
    required this.controller,
  });

  final SProfileController controller;

  @override
  Widget build(BuildContext context) {
    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Obx(
          () => Checkbox(
            value: controller.hasAcceptedTerms.value,
            onChanged: controller.toggleTermsAgreement,
          ),
        ),
        Expanded(
          child: Padding(
            padding: const EdgeInsets.only(top: SSizes.profileTermsTopPadding),
            child: RichText(
              text: TextSpan(
                style: Theme.of(context).textTheme.bodySmall?.copyWith(
                          color: SColors.textSecondary,
                        ) ??
                    const TextStyle(color: SColors.textSecondary),
                children: [
                  const TextSpan(text: '${STexts.iAgreeTo} '),
                  TextSpan(
                    text: STexts.privacyPolicy,
                    style: const TextStyle(color: SColors.primary),
                  ),
                  const TextSpan(text: ' and '),
                  TextSpan(
                    text: STexts.termsOfUse,
                    style: const TextStyle(color: SColors.primary),
                  ),
                ],
              ),
            ),
          ),
        ),
      ],
    );
  }
}
