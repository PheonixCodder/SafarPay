import 'package:flutter/material.dart';
import 'package:get/get.dart';

import '../../../../common/widgets/appbar/appbar.dart';
import '../../../../common/widgets/divider.dart';
import '../../../../utils/constants/colors.dart';
import '../../../../utils/constants/images.dart';
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
      appBar: SAppBar(
        showCircularBack: true,
        leadingOnPressed: () => Navigator.of(context).pop(),
        centerTitle: true,
      ),
      body: SafeArea(
        child: SingleChildScrollView(
          child: Padding(
            padding: const EdgeInsets.symmetric(horizontal: SSizes.defaultSpace),
            child: Center(
              child: ConstrainedBox(
                constraints: const BoxConstraints(maxWidth: 420),
                child: Column(
                  children: [
                    const SizedBox(height: SSizes.spaceBtwSections),
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
    );
  }
}
