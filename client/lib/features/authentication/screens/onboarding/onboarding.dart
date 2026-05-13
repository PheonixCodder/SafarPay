import 'package:flutter/material.dart';
import 'package:get/get.dart';

import '../../../../utils/constants/colors.dart';
import '../../../../utils/constants/images.dart';
import '../../../../utils/constants/texts.dart';
import '../../controllers/onboarding.dart';
import 'widgets/onboarding.dart';
import 'widgets/onboarding_navigation_buttons.dart';

class OnBoardingScreen extends StatefulWidget {
  const OnBoardingScreen({
    super.key,
  });

  @override
  State<OnBoardingScreen> createState() => _OnBoardingScreenState();
}

class _OnBoardingScreenState extends State<OnBoardingScreen> {
  bool _didPrecacheImages = false;

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();

    if (_didPrecacheImages) return;

    precacheImage(const AssetImage(SImages.onBoarding1), context);
    precacheImage(const AssetImage(SImages.onBoarding2), context);
    precacheImage(const AssetImage(SImages.onBoarding3), context);
    _didPrecacheImages = true;
  }

  @override
  Widget build(BuildContext context) {
    final controller = Get.put(OnBoardingController());

    return Scaffold(
      backgroundColor: SColors.black,
      body: Stack(
        fit: StackFit.expand,
        children: [
          PageView(
            controller: controller.pageController,
            onPageChanged: controller.updatePageIndicator,
            allowImplicitScrolling: true,
            physics: const BouncingScrollPhysics(),
            children: const [
              OnBoardingPage(
                image: SImages.onBoarding1,
                title: STexts.onBoardingTitle1,
                subTitle: STexts.onBoardingSubTitle1,
              ),
              OnBoardingPage(
                image: SImages.onBoarding2,
                title: STexts.onBoardingTitle2,
                subTitle: STexts.onBoardingSubTitle2,
              ),
              OnBoardingPage(
                image: SImages.onBoarding3,
                title: STexts.onBoardingTitle3,
                subTitle: STexts.onBoardingSubTitle3,
              ),
            ],
          ),
          OnBoardingDotNavigation(controller: controller),
          OnBoardingNavigationButtons(controller: controller),
        ],
      ),
    );
  }
}
