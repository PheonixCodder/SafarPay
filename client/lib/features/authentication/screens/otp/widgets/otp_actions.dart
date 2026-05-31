import 'package:flutter/material.dart';
import 'package:get/get.dart';

import '../../../../../utils/constants/colors.dart';
import '../../../../../utils/constants/sizes.dart';
import '../../../../../utils/constants/texts.dart';
import '../../../controllers/otp.dart';

class SOtpActions extends StatelessWidget {
  const SOtpActions({
    super.key,
    required this.controller,
  });

  final SOtpController controller;

  @override
  Widget build(BuildContext context) {
    final bodyMedium = Theme.of(context).textTheme.bodyMedium;
    final bodyLarge = Theme.of(context).textTheme.bodyLarge;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // Resend row
        Obx(() {
          if (!controller.canResend) {
            return Text(
              '${STexts.resendOtpIn} ${controller.resendSecondsRemaining.value}s',
              style: bodyMedium?.copyWith(color: SColors.textSecondary),
            );
          }

          return GestureDetector(
            onTap: controller.resendOtp,
            child: RichText(
              text: TextSpan(
                text: "Didn't receive the code? ",
                style: bodyMedium?.copyWith(color: SColors.textSecondary),
                children: [
                  TextSpan(
                    text: 'Send again',
                    style: bodyMedium?.copyWith(
                      color: SColors.textPrimary,
                      fontWeight: FontWeight.w600,
                      decoration: TextDecoration.underline,
                      decorationColor: SColors.textPrimary,
                    ),
                  ),
                ],
              ),
            ),
          );
        }),

        const SizedBox(height: SSizes.spaceBtwSections),

        // Verify button – black pill shape
        Obx(
          () => SizedBox(
            width: double.infinity,
            child: ElevatedButton(
              onPressed:
                  controller.canVerify ? () => controller.verifyOtp() : null,
              style: ElevatedButton.styleFrom(
                backgroundColor: SColors.pureBlack,
                disabledBackgroundColor: SColors.borderPrimary,
                foregroundColor: SColors.white,
                disabledForegroundColor: SColors.darkGrey,
                elevation: 0,
                padding: const EdgeInsets.symmetric(
                  vertical: SSizes.spaceBtnItems,
                ),
                shape: const StadiumBorder(),
              ),
              child: Text(
                STexts.verifyOtp,
                style: bodyLarge?.copyWith(
                  color: controller.canVerify
                      ? SColors.white
                      : SColors.darkGrey,
                  fontWeight: FontWeight.w600,
                  letterSpacing: 0.2,
                ),
              ),
            ),
          ),
        ),
      ],
    );
  }
}
