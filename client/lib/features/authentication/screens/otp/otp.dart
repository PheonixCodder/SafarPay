import 'package:flutter/material.dart';
import 'package:get/get.dart';

import '../../../../common/widgets/appbar/appbar.dart';
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
      appBar: const SAppBar(
        showCircularBack: true,
        centerTitle: true,
      ),
      body: SafeArea(
        child: SingleChildScrollView(
          child: Padding(
            padding: const EdgeInsets.all(24.0),
            child: ConstrainedBox(
              constraints: const BoxConstraints(maxWidth: 420),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const SizedBox(height: 32.0),
                  SOtpHeader(controller: controller),
                  const SizedBox(height: 32.0),
                  SOtpInput(controller: controller),
                  const SizedBox(height: 32.0),
                  SOtpActions(controller: controller),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }
}
