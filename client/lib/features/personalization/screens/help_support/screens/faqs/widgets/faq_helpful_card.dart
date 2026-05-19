import 'package:flutter/material.dart';
import 'package:iconsax/iconsax.dart';

import '../../../../../../../utils/constants/colors.dart';
import '../../../../../../../utils/constants/sizes.dart';

class SFaqHelpfulCard extends StatelessWidget {
  const SFaqHelpfulCard({super.key});

  @override
  Widget build(BuildContext context) {
    final textTheme = Theme.of(context).textTheme;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'Was this article helpful?',
          style: textTheme.labelLarge?.copyWith(
            color: SColors.textPrimary,
            fontWeight: FontWeight.w900,
          ),
        ),
        const SizedBox(height: SSizes.sm),
        Row(
          children: [
            Expanded(
              child: OutlinedButton.icon(
                onPressed: () {},
                icon: const Icon(Iconsax.like_1, size: SSizes.iconSm),
                label: const Text('Yes'),
              ),
            ),
            const SizedBox(width: SSizes.sm),
            Expanded(
              child: OutlinedButton.icon(
                onPressed: () {},
                icon: const Icon(Iconsax.dislike, size: SSizes.iconSm),
                label: const Text('No'),
              ),
            ),
          ],
        ),
      ],
    );
  }
}
