import 'package:flutter/material.dart';
import 'package:iconsax/iconsax.dart';

import '../../../../../utils/constants/colors.dart';
import '../../../../../utils/constants/sizes.dart';
import '../help_support_option.dart';

class SHelpSupportOptionTile extends StatelessWidget {
  const SHelpSupportOptionTile({
    super.key,
    required this.option,
    required this.onTap,
  });

  final SHelpSupportOption option;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      height: SSizes.helpSupportOptionHeight,
      child: InkWell(
        onTap: onTap,
        child: Row(
          children: [
            Icon(
              option.icon,
              color: SColors.pureBlack,
              size: SSizes.helpSupportOptionIconSize,
            ),
            const SizedBox(width: SSizes.lg),
            Expanded(
              child: Text(
                option.title,
                style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                      color: SColors.pureBlack,
                      fontWeight: FontWeight.w500,
                    ),
              ),
            ),
            const Icon(
              Iconsax.arrow_right_3,
              color: SColors.black,
              size: SSizes.helpSupportOptionArrowSize,
            ),
          ],
        ),
      ),
    );
  }
}
