import 'package:get/get.dart';

enum SAuthFlowStep {
  onboarding,
  login,
}

class SAuthFlowController extends GetxController {
  static SAuthFlowController get instance => Get.find();

  final Rx<SAuthFlowStep> currentStep = SAuthFlowStep.onboarding.obs;

  void showLogin() {
    currentStep.value = SAuthFlowStep.login;
  }
}
