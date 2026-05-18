import 'package:flutter/material.dart';

import '../../../../../utils/constants/colors.dart';
import '../../../../../utils/constants/sizes.dart';
import '../../../../../utils/helpers/helpers.dart';

class OnBoardingPage extends StatelessWidget {
  const OnBoardingPage({
    super.key,
    required this.image,
    required this.title,
    required this.subTitle,
  });

  final String image, title, subTitle;

  @override
  Widget build(BuildContext context) {
    return Stack(
      fit: StackFit.expand,
      children: [
        /// Background Image
        Image.asset(
          image,
          fit: BoxFit.cover,
          gaplessPlayback: true,
          filterQuality: FilterQuality.high,
          frameBuilder: (context, child, frame, wasSynchronouslyLoaded) {
            if (wasSynchronouslyLoaded || frame != null) {
              return child;
            }

            return const ColoredBox(color: SColors.black);
          },
        ),

        /// Dark Gradient Overlay
        Container(
          decoration: BoxDecoration(
            gradient: LinearGradient(
              begin: Alignment.topCenter,
              end: Alignment.bottomCenter,
              colors: [
                SColors.transparent,
                SHelperFunctions.withOpacity(
                  SColors.black,
                  SOpacities.onboardingGradientMid,
                ),
                SHelperFunctions.withOpacity(
                  SColors.black,
                  SOpacities.onboardingGradientDeep,
                ),
                SColors.black,
              ],
              stops: [0.4, 0.65, 0.85, 1],
            ),
          ),
        ),

        /// Bottom Content
        Positioned(
          left: SSizes.defaultSpace,
          right: SSizes.defaultSpace,
          bottom: (SSizes.appBarHeight + SSizes.xs / 2) * 2 +
              SSizes.spaceBtnItems +
              SSizes.xl +
              SSizes.sm +
              SSizes.appBarHeight +
              SSizes.xs,
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              /// Title
              Text(
                title,
                textAlign: TextAlign.center,
                style: Theme.of(context).textTheme.headlineMedium?.copyWith(
                      color: SColors.textWhite,
                      fontWeight: FontWeight.bold,
                      fontSize: SSizes.xl + SSizes.xs / 2,
                    ),
              ),

              const SizedBox(height: SSizes.spaceBtnItems),

              /// Subtitle
              FractionallySizedBox(
                widthFactor: 0.75,
                child: Text(
                  subTitle,
                  textAlign: TextAlign.center,
                  style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                        color: SHelperFunctions.withOpacity(
                          SColors.textWhite,
                          SOpacities.onboardingButtonText,
                        ),
                        fontSize: SSizes.fontSizeMd,
                        height: 1.5,
                      ),
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }
}
