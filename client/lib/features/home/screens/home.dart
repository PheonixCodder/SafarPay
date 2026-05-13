import 'package:flutter/material.dart';
import 'package:iconsax/iconsax.dart';

import '../../../utils/constants/colors.dart';
import '../../../utils/constants/sizes.dart';
import '../../../utils/constants/texts.dart';

class HomeScreen extends StatelessWidget {
  const HomeScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: SColors.primaryBackground,
      appBar: AppBar(
        titleSpacing: SSizes.defaultSpace,
        title: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              STexts.homeAppbarTitle,
              style: Theme.of(context).textTheme.labelMedium?.copyWith(
                    color: SColors.textSecondary,
                  ),
            ),
            Text(
              STexts.homeAppbarSubTitle,
              style: Theme.of(context).textTheme.titleMedium?.copyWith(
                    color: SColors.textPrimary,
                    fontWeight: FontWeight.w700,
                  ),
            ),
          ],
        ),
      ),
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(SSizes.defaultSpace),
          child: Center(
            child: ConstrainedBox(
              constraints: const BoxConstraints(maxWidth: 420),
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Container(
                    width: 96,
                    height: 96,
                    decoration: BoxDecoration(
                      color: SColors.primary.withOpacity(0.12),
                      shape: BoxShape.circle,
                    ),
                    child: const Icon(
                      Iconsax.home_2,
                      color: SColors.primary,
                      size: 40,
                    ),
                  ),
                  const SizedBox(height: SSizes.spaceBtwSections),
                  Text(
                    STexts.homeTitle,
                    textAlign: TextAlign.center,
                    style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                          color: SColors.textPrimary,
                          fontWeight: FontWeight.w700,
                        ),
                  ),
                  const SizedBox(height: SSizes.spaceBtnItems),
                  Text(
                    STexts.homeSubTitle,
                    textAlign: TextAlign.center,
                    style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                          color: SColors.textSecondary,
                          height: 1.5,
                        ),
                  ),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }
}
