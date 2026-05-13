import 'package:flutter/material.dart';
import 'package:get/get.dart';

import '../../../../../utils/constants/colors.dart';
import '../../../../../utils/constants/sizes.dart';

class SPermissionPage extends StatelessWidget {
  const SPermissionPage({
    super.key,
    required this.icon,
    required this.title,
    required this.subTitle,
    required this.buttonText,
    required this.onPressed,
    required this.isRequesting,
  });

  final IconData icon;
  final String title;
  final String subTitle;
  final String buttonText;
  final VoidCallback onPressed;
  final RxBool isRequesting;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: SColors.white,
      body: SafeArea(
        child: Stack(
          children: [
            Padding(
              padding: const EdgeInsets.symmetric(
                horizontal: SSizes.defaultSpace,
              ),
              child: Center(
                child: ConstrainedBox(
                  constraints: const BoxConstraints(maxWidth: 420),
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Container(
                        width: 118,
                        height: 118,
                        decoration: BoxDecoration(
                          color: SColors.secondary.withOpacity(0.12),
                          shape: BoxShape.circle,
                        ),
                        child: Icon(
                          icon,
                          color: SColors.black,
                          size: 44,
                        ),
                      ),
                      const SizedBox(height: SSizes.spaceBtwSections),
                      Text(
                        title,
                        textAlign: TextAlign.center,
                        style:
                            Theme.of(context).textTheme.headlineMedium?.copyWith(
                                  color: SColors.textPrimary,
                                  fontWeight: FontWeight.bold,
                                ),
                      ),
                      const SizedBox(height: SSizes.spaceBtnItems),
                      FractionallySizedBox(
                        widthFactor: 0.86,
                        child: Text(
                          subTitle,
                          textAlign: TextAlign.center,
                          style:
                              Theme.of(context).textTheme.bodyMedium?.copyWith(
                                    color: SColors.textSecondary,
                                    height: 1.5,
                                  ),
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            ),
            Align(
              alignment: Alignment.bottomCenter,
              child: Container(
                width: double.infinity,
                padding: const EdgeInsets.all(SSizes.spaceBtwSections),
                decoration: BoxDecoration(
                  color: SColors.white,
                  borderRadius: const BorderRadius.only(
                    topLeft: Radius.circular(32),
                    topRight: Radius.circular(32),
                  ),
                  boxShadow: [
                    BoxShadow(
                      color: SColors.black.withOpacity(0.08),
                      blurRadius: 24,
                      offset: const Offset(0, -8),
                    ),
                  ],
                ),
                child: Align( // Use Align instead of Center
                  alignment: Alignment.topCenter, // This prevents vertical expansion
                  heightFactor: 1.0, // Forces the container to hug the height of the child
                  child: ConstrainedBox(
                    constraints: const BoxConstraints(maxWidth: 420),
                    child: SizedBox(
                      width: double.infinity,
                      child: Obx(
                            () => ElevatedButton(
                          onPressed: isRequesting.value ? null : onPressed,
                          child: Text(buttonText),
                        ),
                      ),
                    ),
                  ),
                ),
              ),
            )
          ],
        ),
      ),
    );
  }
}
