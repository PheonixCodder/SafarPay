import 'package:client/features/personalization/screens/driver_registration/controllers/driver_verification_controller.dart';
import 'package:client/utils/constants/texts.dart';
import 'package:flutter/material.dart';

class SDriverVerificationSubmitReviewButton extends StatelessWidget {
  const SDriverVerificationSubmitReviewButton({
    super.key,
    required this.controller,
  });

  final SDriverVerificationController controller;

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      width: double.infinity,
      child: ElevatedButton(
        onPressed: controller.isSubmittingReview.value
            ? null
            : controller.submitForReview,
        child: Text(
          controller.isSubmittingReview.value
              ? STexts.driverVerificationSubmittingReview
              : STexts.driverVerificationSubmitReview,
        ),
      ),
    );
  }
}
