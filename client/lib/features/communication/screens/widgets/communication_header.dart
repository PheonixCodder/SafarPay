import 'package:flutter/material.dart';
import 'package:iconsax/iconsax.dart';

import '../../../../utils/constants/colors.dart';
import '../../../../utils/constants/sizes.dart';

class SCommunicationHeader extends StatelessWidget {
  const SCommunicationHeader({
    super.key,
    required this.statusText,
    required this.onCallPressed,
    required this.callEnabled,
  });

  final String statusText;
  final VoidCallback onCallPressed;
  final bool callEnabled;

  @override
  Widget build(BuildContext context) {
    final textTheme = Theme.of(context).textTheme;

    return DecoratedBox(
      decoration: const BoxDecoration(
        color: SColors.white,
        border: Border(
          bottom: BorderSide(color: SColors.borderSecondary),
        ),
      ),
      child: Padding(
        padding: const EdgeInsets.fromLTRB(
          SSizes.defaultSpace,
          SSizes.sm,
          SSizes.defaultSpace,
          SSizes.md,
        ),
        child: Row(
          children: [
            Container(
              width: 44,
              height: 44,
              decoration: BoxDecoration(
                color: SColors.primaryBackground,
                borderRadius: BorderRadius.circular(SSizes.cardRadiusMd),
                border: Border.all(color: SColors.borderSecondary),
              ),
              child: const Icon(Iconsax.message_text, color: SColors.primary),
            ),
            const SizedBox(width: SSizes.md),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'Ride communication',
                    style: textTheme.titleMedium?.copyWith(
                      color: SColors.textPrimary,
                      fontWeight: FontWeight.w900,
                    ),
                  ),
                  const SizedBox(height: SSizes.xs),
                  Text(
                    statusText,
                    style: textTheme.bodySmall?.copyWith(
                      color: SColors.textSecondary,
                    ),
                  ),
                ],
              ),
            ),
            IconButton.filled(
              onPressed: callEnabled ? onCallPressed : null,
              style: IconButton.styleFrom(
                backgroundColor: SColors.primary,
                foregroundColor: SColors.white,
                disabledBackgroundColor: SColors.borderSecondary,
              ),
              icon: const Icon(Iconsax.call),
            ),
          ],
        ),
      ),
    );
  }
}
