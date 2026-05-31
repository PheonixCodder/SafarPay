import 'package:flutter/material.dart';
import 'package:get/get.dart';
 
import '../../controllers/auth_flow.dart';
import '../onboarding/onboarding.dart';
 
class AuthFlowScreen extends StatelessWidget {
  const AuthFlowScreen({super.key});
 
  @override
  Widget build(BuildContext context) {
    Get.put(SAuthFlowController(), permanent: true);
 
    return const OnBoardingScreen();
  }
}
