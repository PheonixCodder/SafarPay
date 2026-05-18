import 'package:flutter/material.dart';
import 'package:get/get.dart';

import 'auth_flow.dart';

class OnBoardingController extends GetxController {
  static OnBoardingController get instance => Get.find();

  static const int pageCount = 3;
  static const int lastPageIndex = pageCount - 1;

  final PageController pageController = PageController();
  final RxInt currentPageIndex = 0.obs;

  bool get isLastPage => currentPageIndex.value == lastPageIndex;

  void updatePageIndicator(int index) {
    currentPageIndex.value = index;
  }

  void dotNavigationClick(int index) {
    if (index < 0 || index >= pageCount) return;

    currentPageIndex.value = index;
    pageController.animateToPage(
      index,
      duration: const Duration(milliseconds: 300),
      curve: Curves.easeInOut,
    );
  }

  void nextPage() {
    if (isLastPage) {
      completeOnboarding();
      return;
    }

    pageController.nextPage(
      duration: const Duration(milliseconds: 300),
      curve: Curves.easeInOut,
    );
  }

  void skipPage() {
    dotNavigationClick(lastPageIndex);
  }

  void completeOnboarding() {
    SAuthFlowController.instance.showLogin();
  }

  @override
  void onClose() {
    pageController.dispose();
    super.onClose();
  }
}
