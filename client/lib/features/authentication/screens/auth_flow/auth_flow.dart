import 'package:flutter/material.dart';
import 'package:get/get.dart';

import '../../controllers/auth_flow.dart';
import '../login/login.dart';
import '../onboarding/onboarding.dart';

class AuthFlowScreen extends StatelessWidget {
  const AuthFlowScreen({super.key});

  static const _duration = Duration(milliseconds: 450);
  static const _beginOffset = Offset(0.04, 0);

  @override
  Widget build(BuildContext context) {
    final controller = Get.put(SAuthFlowController());

    return Obx(
      () => AnimatedSwitcher(
        duration: _duration,
        switchInCurve: Curves.easeOutCubic,
        switchOutCurve: Curves.easeInCubic,
        transitionBuilder: (child, animation) {
          final offsetAnimation = Tween<Offset>(
            begin: _beginOffset,
            end: Offset.zero,
          ).animate(animation);

          return FadeTransition(
            opacity: animation,
            child: SlideTransition(
              position: offsetAnimation,
              child: child,
            ),
          );
        },
        child: switch (controller.currentStep.value) {
          SAuthFlowStep.onboarding => const OnBoardingScreen(
              key: ValueKey(SAuthFlowStep.onboarding),
            ),
          SAuthFlowStep.login => const LoginScreen(
              key: ValueKey(SAuthFlowStep.login),
            ),
        },
      ),
    );
  }
}
