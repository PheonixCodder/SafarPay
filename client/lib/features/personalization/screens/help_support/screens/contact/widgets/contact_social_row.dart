import 'package:flutter/material.dart';

import '../../../../../../../utils/constants/colors.dart';
import '../../../../../../../utils/constants/sizes.dart';
import '../../../../../../../utils/helpers/helpers.dart';

class SContactSocialRow extends StatelessWidget {
  const SContactSocialRow({
    super.key,
    required this.label,
    required this.mark,
    required this.onTap,
  });

  final String label;
  final String mark;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(SSizes.cardRadiusMd),
      child: Padding(
        padding: const EdgeInsets.symmetric(vertical: SSizes.sm),
        child: Row(
          children: [
            Container(
              width: 42,
              height: 42,
              alignment: Alignment.center,
              decoration: BoxDecoration(
                color: SColors.white,
                shape: BoxShape.circle,
                boxShadow: [
                  BoxShadow(
                    color: SHelperFunctions.withOpacity(
                      SColors.pureBlack,
                      SOpacities.light,
                    ),
                    blurRadius: 14,
                    offset: const Offset(0, 6),
                  ),
                ],
              ),
              child: Text(
                mark,
                style: Theme.of(context).textTheme.titleMedium?.copyWith(
                      color: SColors.pureBlack,
                      fontWeight: FontWeight.w700,
                    ),
              ),
            ),
            const SizedBox(width: SSizes.md),
            Expanded(
              child: Text(
                label,
                style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                      color: SColors.textPrimary,
                      fontWeight: FontWeight.w500,
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
