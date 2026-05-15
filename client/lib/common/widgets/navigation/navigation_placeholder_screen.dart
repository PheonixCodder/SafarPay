import 'package:flutter/material.dart';

import '../../../utils/constants/colors.dart';
import '../../../utils/constants/sizes.dart';
import '../../../utils/helpers/helpers.dart';

class SNavigationPlaceholderScreen extends StatelessWidget {
  const SNavigationPlaceholderScreen({
    super.key,
    required this.icon,
    required this.title,
    required this.subtitle,
  });

  final IconData icon;
  final String title;
  final String subtitle;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: SColors.primaryBackground,
      appBar: AppBar(
        titleSpacing: SSizes.defaultSpace,
        title: Text(
          title,
          style: Theme.of(context).textTheme.titleMedium?.copyWith(
                color: SColors.textPrimary,
                fontWeight: FontWeight.w700,
              ),
        ),
      ),
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(SSizes.defaultSpace),
          child: Center(
            child: ConstrainedBox(
              constraints: const BoxConstraints(
                maxWidth: SSizes.navigationPlaceholderMaxWidth,
              ),
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Container(
                    width: SSizes.navigationPlaceholderIconBoxSize,
                    height: SSizes.navigationPlaceholderIconBoxSize,
                    decoration: BoxDecoration(
                      color: SHelperFunctions.withOpacity(
                        SColors.primary,
                        SOpacities.placeholder,
                      ),
                      shape: BoxShape.circle,
                    ),
                    child: Icon(
                      icon,
                      color: SColors.primary,
                      size: SSizes.navigationPlaceholderIconSize,
                    ),
                  ),
                  const SizedBox(height: SSizes.spaceBtwSections),
                  Text(
                    title,
                    textAlign: TextAlign.center,
                    style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                          color: SColors.textPrimary,
                          fontWeight: FontWeight.w700,
                        ),
                  ),
                  const SizedBox(height: SSizes.spaceBtnItems),
                  Text(
                    subtitle,
                    textAlign: TextAlign.center,
                    style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                          color: SColors.textSecondary,
                          height: SSizes.navigationPlaceholderTextHeight,
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
