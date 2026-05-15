import 'package:flutter/material.dart';
import 'package:smooth_page_indicator/smooth_page_indicator.dart';

import '../../../../../utils/constants/colors.dart';
import '../../../../../utils/constants/sizes.dart';
import '../../../../../utils/device/utility.dart';
import '../../../controllers/onboarding.dart';

class OnBoardingDotNavigation extends StatelessWidget {
  const OnBoardingDotNavigation({
    super.key,
    required this.controller,
  });

  final OnBoardingController controller;

  @override
  Widget build(BuildContext context) {
    return Positioned(
      top: SDeviceUtils.getStatusBarHeight() + SSizes.onboardingDotTopOffset,
      left: 0,
      right: 0,
      child: Center(
        child: SmoothPageIndicator(
          controller: controller.pageController,
          onDotClicked: controller.dotNavigationClick,
          count: OnBoardingController.pageCount,
          effect: const ExpandingDotsEffect(
            activeDotColor: SColors.white,
            dotColor: SColors.grey,
            dotHeight: SSizes.onboardingDotSize,
            dotWidth: SSizes.onboardingDotSize,
          ),
        ),
      ),
    );
  }
}
