import 'package:flutter/material.dart';
import 'package:iconsax/iconsax.dart';

import '../../../../../../../utils/constants/colors.dart';
import '../../../../../../../utils/constants/sizes.dart';
import '../../../../../../../utils/helpers/helpers.dart';

class SSupportSuccessIllustration extends StatelessWidget {
  const SSupportSuccessIllustration({super.key});

  @override
  Widget build(BuildContext context) {
    return Center(
      child: SizedBox(
        width: 150,
        height: 150,
        child: Stack(
          alignment: Alignment.center,
          children: [
            Container(
              width: 136,
              height: 136,
              decoration: BoxDecoration(
                color: SHelperFunctions.withOpacity(
                  SColors.primary,
                  SOpacities.tinted,
                ),
                shape: BoxShape.circle,
              ),
            ),
            Positioned(
              top: SSizes.md,
              child: Container(
                width: 66,
                height: 66,
                decoration: const BoxDecoration(
                  color: SColors.primary,
                  shape: BoxShape.circle,
                ),
                child: const Icon(
                  Iconsax.tick_circle,
                  color: SColors.white,
                  size: 38,
                ),
              ),
            ),
            Positioned(
              bottom: SSizes.sm,
              child: Container(
                width: 72,
                height: 72,
                decoration: BoxDecoration(
                  color: SColors.white,
                  borderRadius: BorderRadius.circular(SSizes.cardRadiusLg),
                ),
                child: const Icon(
                  Iconsax.user,
                  color: SColors.primary,
                  size: 42,
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
