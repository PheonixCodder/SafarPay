import 'package:flutter/material.dart';
import 'package:get/get.dart';

import '../../../../utils/constants/colors.dart';
import '../../../../utils/constants/sizes.dart';
import '../../controllers/otp.dart';
import '../../models/auth_models.dart';
import 'widgets/otp_actions.dart';
import 'widgets/otp_header.dart';
import 'widgets/otp_input.dart';

class OtpScreen extends StatelessWidget {
  const OtpScreen({
    super.key,
    required this.phoneNumber,
    required this.flow,
    this.displayName,
    this.googleLoginToken,
    this.maskedPhone,
  });

  final String phoneNumber;
  final SAuthOtpFlow flow;
  final String? displayName;
  final String? googleLoginToken;
  final String? maskedPhone;

  @override
  Widget build(BuildContext context) {
    final controller = Get.put(
      SOtpController(
        phoneNumber: phoneNumber,
        flow: flow,
        displayName: displayName,
        googleLoginToken: googleLoginToken,
        maskedPhone: maskedPhone,
      ),
      tag: '${phoneNumber}_${flow.name}',
    );

    return Scaffold(
      backgroundColor: SColors.primaryBackground,
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
                        SOtpHeader(controller: controller),
                        const SizedBox(height: SSizes.spaceBtwSections),
                        SOtpInput(controller: controller),
                        const SizedBox(height: SSizes.spaceBtwSections),
                        SOtpActions(controller: controller),
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
