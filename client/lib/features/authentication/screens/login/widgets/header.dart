import 'package:flutter/material.dart';

import '../../../../../utils/constants/colors.dart';
import '../../../../../utils/constants/sizes.dart';

class SLoginHeader extends StatelessWidget {
  const SLoginHeader({super.key});

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      width: double.infinity, // Ensures it takes the full screen width
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start, // Aligns content to the left
        mainAxisAlignment: MainAxisAlignment.start, // Aligns content to the top
        children: [
          Text(
            "Welcome Back!",
            style: Theme.of(context).textTheme.headlineLarge?.copyWith(
              fontWeight: FontWeight.bold,
              fontSize: 32,
              color: SColors.textPrimary,
            ),
          ),
          const SizedBox(height: SSizes.xs),
          Text(
            "log in with your phone number",
            style: Theme.of(context).textTheme.bodyMedium?.copyWith(
              color: SColors.textSecondary,
              fontSize: 16,
            ),
          ),
        ],
      ),
    );
  }
}
