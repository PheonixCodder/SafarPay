import 'package:flutter/material.dart';
import 'package:get/get.dart';

import '../../../../../utils/constants/colors.dart';
import '../../../../../utils/constants/sizes.dart';
import '../../../../../utils/constants/texts.dart';
import '../../../../../utils/helpers/helpers.dart';
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
                      color: SHelperFunctions.withOpacity(
                        SColors.primary,
                        SOpacities.onboardingButtonBorder,
                      ),
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
                      color: SHelperFunctions.withOpacity(
                        SColors.textWhite,
                        SOpacities.onboardingButtonText,
                      ),
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
