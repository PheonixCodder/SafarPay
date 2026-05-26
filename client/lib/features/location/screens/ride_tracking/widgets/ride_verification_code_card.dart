import 'package:flutter/material.dart';

import '../../../../../utils/constants/colors.dart';
import '../../../../../utils/constants/sizes.dart';

class SRideVerificationCodeCard extends StatelessWidget {
  const SRideVerificationCodeCard({
    super.key,
    required this.title,
    required this.code,
  });

  final String title;
  final String code;

  @override
  Widget build(BuildContext context) {
    final textTheme = Theme.of(context).textTheme;

    return DecoratedBox(
      decoration: BoxDecoration(
        color: SColors.white,
        borderRadius: BorderRadius.circular(SSizes.rideSheetRadius),
      ),
      child: Padding(
        padding: const EdgeInsets.all(SSizes.lg),
        child: Row(
          children: [
            Expanded(
              child: Text(
                title,
                style: textTheme.titleMedium?.copyWith(
                  color: SColors.textPrimary,
                  fontWeight: FontWeight.w800,
                ),
              ),
            ),
            Text(
              code,
              style: textTheme.headlineSmall?.copyWith(
                color: SColors.primary,
                fontWeight: FontWeight.w900,
                letterSpacing: 2,
              ),
            ),
          ],
        ),
      ),
    );
  }
}
