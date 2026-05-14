import 'package:flutter/material.dart';
import 'package:get/get.dart';

import '../../../../utils/constants/sizes.dart';
import '../../controllers/profile.dart';
import 'widgets/profile_form.dart';
import 'widgets/profile_header.dart';

class CompleteProfileScreen extends StatelessWidget {
  const CompleteProfileScreen({
    super.key,
    required this.verificationToken,
  });

  final String verificationToken;

  @override
  Widget build(BuildContext context) {
    final controller = Get.put(
      SProfileController(verificationToken: verificationToken),
      tag: verificationToken,
    );

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
                padding: const EdgeInsets.all(SSizes.defaultSpace),
                child: Center(
                  child: ConstrainedBox(
                    constraints: const BoxConstraints(maxWidth: 420),
                    child: Column(
                      children: [
                        const SProfileHeader(),
                        const SizedBox(height: SSizes.spaceBtwSections),
                        SProfileForm(controller: controller),
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
