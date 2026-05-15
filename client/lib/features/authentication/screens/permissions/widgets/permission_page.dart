import 'package:flutter/material.dart';
import 'package:get/get.dart';

import '../../../../../utils/constants/colors.dart';
import '../../../../../utils/constants/sizes.dart';
import '../../../../../utils/helpers/helpers.dart';

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
                  constraints: const BoxConstraints(
                    maxWidth: SSizes.permissionContentMaxWidth,
                  ),
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Container(
                        width: SSizes.permissionIconBoxSize,
                        height: SSizes.permissionIconBoxSize,
                        decoration: BoxDecoration(
                          color: SHelperFunctions.withOpacity(
                            SColors.secondary,
                            SOpacities.placeholder,
                          ),
                          shape: BoxShape.circle,
                        ),
                        child: Icon(
                          icon,
                          color: SColors.black,
                          size: SSizes.permissionIconSize,
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
                        widthFactor: SSizes.permissionSubtitleWidthFactor,
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
                    topLeft: Radius.circular(SSizes.permissionSheetRadius),
                    topRight: Radius.circular(SSizes.permissionSheetRadius),
                  ),
                  boxShadow: [
                    BoxShadow(
                      color: SHelperFunctions.withOpacity(
                        SColors.black,
                        SOpacities.tinted,
                      ),
                      blurRadius: SSizes.permissionSheetShadowBlur,
                      offset: const Offset(
                        0,
                        SSizes.permissionSheetShadowOffsetY,
                      ),
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
