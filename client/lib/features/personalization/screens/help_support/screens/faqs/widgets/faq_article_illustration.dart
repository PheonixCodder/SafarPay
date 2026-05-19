import 'package:flutter/material.dart';
import 'package:iconsax/iconsax.dart';

import '../../../../../../../utils/constants/colors.dart';
import '../../../../../../../utils/constants/sizes.dart';
import '../../../../../../../utils/helpers/helpers.dart';

class SFaqArticleIllustration extends StatelessWidget {
  const SFaqArticleIllustration({super.key});

  @override
  Widget build(BuildContext context) {
    return Center(
      child: SizedBox(
        width: 150,
        height: 112,
        child: Stack(
          alignment: Alignment.center,
          children: [
            Positioned(
              left: 0,
              top: 12,
              child: Container(
                width: 86,
                height: 70,
                decoration: BoxDecoration(
                  color: SHelperFunctions.withOpacity(
                    SColors.primary,
                    SOpacities.tinted,
                  ),
                  borderRadius: BorderRadius.circular(SSizes.cardRadiusLg),
                ),
              ),
            ),
            Positioned(
              right: 12,
              top: 4,
              child: Icon(
                Iconsax.undo,
                color: SHelperFunctions.withOpacity(
                  SColors.primary,
                  SOpacities.strong,
                ),
                size: 42,
              ),
            ),
            Positioned(
              left: 24,
              bottom: 20,
              child: Container(
                width: 76,
                height: 54,
                decoration: BoxDecoration(
                  color: SColors.primary,
                  borderRadius: BorderRadius.circular(SSizes.cardRadiusMd),
                  boxShadow: [
                    BoxShadow(
                      color: SHelperFunctions.withOpacity(
                        SColors.primary,
                        SOpacities.placeholder,
                      ),
                      blurRadius: SSizes.shadowBlurLg,
                      offset: const Offset(0, SSizes.sm),
                    ),
                  ],
                ),
                child: const Icon(
                  Iconsax.wallet_3,
                  color: SColors.white,
                  size: SSizes.iconLg,
                ),
              ),
            ),
            Positioned(
              right: 24,
              bottom: 18,
              child: Row(
                children: [
                  _Coin(size: 28),
                  const SizedBox(width: SSizes.xs),
                  _Coin(size: 22),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _Coin extends StatelessWidget {
  const _Coin({required this.size});

  final double size;

  @override
  Widget build(BuildContext context) {
    return Container(
      width: size,
      height: size,
      decoration: const BoxDecoration(
        color: SColors.warning,
        shape: BoxShape.circle,
      ),
      child: Center(
        child: Container(
          width: size * 0.62,
          height: size * 0.62,
          decoration: BoxDecoration(
            border: Border.all(color: SColors.white),
            shape: BoxShape.circle,
          ),
        ),
      ),
    );
  }
}
