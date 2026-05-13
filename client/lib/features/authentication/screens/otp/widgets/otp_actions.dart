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
    return Column(
      children: [
        SizedBox(
          width: double.infinity,
          child: Obx(
            () => ElevatedButton(
              onPressed:
                  controller.canVerify ? () => controller.verifyOtp() : null,
              child: const Text(STexts.verifyOtp),
            ),
          ),
        ),
        const SizedBox(height: SSizes.spaceBtnItems),
        Obx(
          () {
            if (!controller.canResend) {
              return Text(
                '${STexts.resendOtpIn} ${controller.resendSecondsRemaining.value}s',
                textAlign: TextAlign.center,
                style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                      color: SColors.textSecondary,
                    ),
              );
            }

            return TextButton(
              onPressed: controller.resendOtp,
              child: const Text(STexts.resendOnWhatsapp),
            );
          },
        ),
      ],
    );
  }
}
