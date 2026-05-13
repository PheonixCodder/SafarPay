import 'package:flutter/material.dart';
import 'package:get/get.dart';

import '../../../../../utils/constants/colors.dart';
import '../../../../../utils/constants/images.dart';
import '../../../../../utils/constants/sizes.dart';
import '../../../../../utils/constants/texts.dart';
import '../../../controllers/login.dart';

class SSocialButtons extends StatelessWidget {
  const SSocialButtons({
    super.key,
    required this.controller,
  });

  final SLoginController controller;

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      width: double.infinity,
      child: Obx(
        () => OutlinedButton.icon(
          onPressed: controller.isGoogleLoading.value
              ? null
              : controller.loginWithGoogle,
          icon: const Image(
            width: SSizes.iconMd,
            height: SSizes.iconMd,
            image: AssetImage(SImages.google),
          ),
          label: const Text(STexts.continueWithGoogle),
          style: OutlinedButton.styleFrom(
            foregroundColor: SColors.textPrimary,
            side: const BorderSide(color: SColors.borderSecondary),
            padding: const EdgeInsets.symmetric(vertical: 18),
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(SSizes.borderRadiusLg),
            ),
          ),
        ),
      ),
    );
  }
}
