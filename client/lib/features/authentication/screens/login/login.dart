import 'package:flutter/material.dart';
import 'package:get/get.dart';

import '../../../../common/widgets/divider.dart';
import '../../../../common/styles/spacing_styles.dart';
import '../../../../utils/constants/sizes.dart';
import '../../../../utils/constants/texts.dart';
import '../../controllers/login.dart';
import 'widgets/form.dart';
import 'widgets/header.dart';
import 'widgets/social_buttons.dart';

class LoginScreen extends StatelessWidget {
  const LoginScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final controller = Get.put(SLoginController());

    return Scaffold(
      body: Stack(
        children: [
          Positioned(
            top: -96,
            left: -56,
            right: -56,
            child: Container(
              height: 230,
              decoration: BoxDecoration(
                borderRadius: const BorderRadius.only(
                  bottomLeft: Radius.circular(120),
                  bottomRight: Radius.circular(120),
                ),
              ),
            ),
          ),
          SafeArea(
            child: SingleChildScrollView(
              child: Padding(
                padding: SSpacingStyle.paddingWithAppBarHeight,
                child: Center(
                  child: ConstrainedBox(
                    constraints: const BoxConstraints(maxWidth: 420),
                    child: Column(
                      children: [
                        const SLoginHeader(),
                        const SizedBox(height: SSizes.spaceBtwSections),
                        SLoginForm(controller: controller),
                        const SizedBox(height: SSizes.spaceBtwSections),
                        const SFormDivider(dividerText: STexts.orContinueWith),
                        const SizedBox(height: SSizes.spaceBtnItems),
                        SSocialButtons(controller: controller),
                      ],
                    ),
                  ),
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }
}
