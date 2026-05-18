import 'package:client/features/personalization/screens/driver_registration/controllers/driver_verification_controller.dart';
import 'package:client/features/personalization/screens/driver_registration/models/driver_registration_models.dart';
import 'package:client/features/personalization/screens/driver_registration/screens/verification_status/widgets/driver_verification_message_panel.dart';
import 'package:client/features/personalization/screens/driver_registration/screens/verification_status/widgets/driver_verification_overall_status_notice.dart';
import 'package:client/features/personalization/screens/driver_registration/screens/verification_status/widgets/driver_verification_submit_review_button.dart';
import 'package:client/features/personalization/screens/driver_registration/widgets/verification_step_card.dart';
import 'package:client/utils/constants/colors.dart';
import 'package:client/utils/constants/sizes.dart';
import 'package:client/utils/constants/texts.dart';
import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'package:iconsax/iconsax.dart';

class SDriverVerificationStatusBody extends StatelessWidget {
  const SDriverVerificationStatusBody({
    super.key,
    required this.controller,
    required this.onStepTap,
  });

  final SDriverVerificationController controller;
  final ValueChanged<SVerificationStep> onStepTap;

  @override
  Widget build(BuildContext context) {
    return Obx(() {
      if (controller.isLoading.value) {
        return const Center(
          child: Padding(
            padding: EdgeInsets.all(SSizes.defaultSpace),
            child: CircularProgressIndicator(color: SColors.primary),
          ),
        );
      }

      final error = controller.errorMessage.value;

      if (error != null) {
        return SDriverVerificationMessagePanel(
          icon: Iconsax.warning_2,
          title: STexts.driverVerificationUnavailable,
          message: error,
          actionLabel: 'Retry',
          onAction: controller.loadStatus,
        );
      }

      final status = controller.status.value;

      if (status == null) {
        return SDriverVerificationMessagePanel(
          icon: Iconsax.warning_2,
          title: STexts.driverVerificationUnavailable,
          message: STexts.unexpectedError,
          actionLabel: 'Retry',
          onAction: controller.loadStatus,
        );
      }

      return Column(
        children: [
          SDriverVerificationOverallStatusNotice(status: status.overallStatus),
          const SizedBox(height: SSizes.md),
          ...controller.stepCards().map(
                (step) => Padding(
                  padding: const EdgeInsets.only(bottom: SSizes.md),
                  child: SVerificationStepCard(
                    step: step,
                    onTap: () => onStepTap(step.step),
                  ),
                ),
              ),
          if (controller.canSubmitForReview) ...[
            const SizedBox(height: SSizes.sm),
            SDriverVerificationSubmitReviewButton(controller: controller),
          ],
        ],
      );
    });
  }
}
