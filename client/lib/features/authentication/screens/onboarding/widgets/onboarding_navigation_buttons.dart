import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'package:smooth_page_indicator/smooth_page_indicator.dart';

import '../../../../../utils/constants/colors.dart';
import '../../../../../utils/constants/sizes.dart';
import '../../../../../utils/constants/texts.dart';
import '../../../../../utils/device/utility.dart';
import '../../../controllers/onboarding.dart';

class OnBoardingNavigationButtons extends StatelessWidget {
  const OnBoardingNavigationButtons({
    super.key,
    required this.controller,
  });

  final OnBoardingController controller;

  @override
  Widget build(BuildContext context) {
    return Positioned(
      left: SSizes.defaultSpace,
      right: SSizes.defaultSpace,
      bottom: SSizes.appBarHeight + SSizes.xs,
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          SizedBox(
            width: double.infinity,
            height: SSizes.appBarHeight + SSizes.xs / 2,
            child: ElevatedButton(
              onPressed: controller.nextPage,
              style: ElevatedButton.styleFrom(
                backgroundColor: SColors.buttonPrimary,
                foregroundColor: SColors.textWhite,
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(
                    SSizes.borderRadiusLg + SSizes.xs / 2,
                  ),
                ),
              ),
              child: Obx(
                () => Text(
                  controller.isLastPage
                      ? STexts.onBoardingGetStarted
                      : STexts.onBoardingNext,
                  style: Theme.of(context).textTheme.titleLarge?.copyWith(
                    color: SColors.textWhite,
                    fontSize: SSizes.fontSizeLg,
                  ),
                ),
              ),
            ),
          ),
          const SizedBox(height: SSizes.spaceBtnItems),
          Obx(
            () => Visibility(
              visible: !controller.isLastPage,
              maintainSize: true,
              maintainAnimation: true,
              maintainState: true,
              child: SizedBox(
                width: double.infinity,
                height: SSizes.appBarHeight + SSizes.xs / 2,
                child: OutlinedButton(
                  onPressed: controller.skipPage,
                  style: OutlinedButton.styleFrom(
                    side: BorderSide(
                      color: SColors.primary.withOpacity(0.65),
                    ),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(
                        SSizes.borderRadiusLg + SSizes.xs / 2,
                      ),
                    ),
                  ),
                  child: Text(
                    STexts.onBoardingSkip,
                    style: Theme.of(context).textTheme.titleLarge?.copyWith(
                      fontSize: SSizes.fontSizeLg,
                      color: SColors.textWhite.withOpacity(0.7),
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

class OnBoardingDotNavigation extends StatelessWidget {
  const OnBoardingDotNavigation({
    super.key,
    required this.controller,
  });

  final OnBoardingController controller;

  @override
  Widget build(BuildContext context) {
    return Positioned(
      top: SDeviceUtils.getStatusBarHeight() + 75,
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
            dotHeight: 6,
            dotWidth: 6,
          ),
        ),
      ),
    );
  }
}
