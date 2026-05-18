import 'package:flutter/material.dart';
import 'package:iconsax/iconsax.dart';

import '../../../../../utils/constants/colors.dart';
import '../../../../../utils/constants/sizes.dart';
import '../../../../../utils/helpers/helpers.dart';

class SDriverRegistrationOptionImageTile extends StatelessWidget {
  const SDriverRegistrationOptionImageTile({
    super.key,
    required this.image,
    required this.compact,
  });

  final String image;
  final bool compact;

  @override
  Widget build(BuildContext context) {
    final size = compact ? 72.0 : 86.0;

    return Container(
      width: size,
      height: size,
      decoration: BoxDecoration(
        color: SHelperFunctions.withOpacity(SColors.primary, SOpacities.light),
        borderRadius: BorderRadius.circular(SSizes.cardRadiusLg),
        border: Border.all(color: SColors.borderSecondary),
      ),
      clipBehavior: Clip.antiAlias,
      child: Image.asset(
        image,
        fit: BoxFit.contain,
        errorBuilder: (context, error, stackTrace) => Icon(
          Iconsax.car,
          color: SColors.primary,
          size: compact ? SSizes.iconLg : 42,
        ),
      ),
    );
  }
}
