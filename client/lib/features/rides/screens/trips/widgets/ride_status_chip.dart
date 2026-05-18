import 'package:flutter/material.dart';

import '../../../../../utils/constants/colors.dart';
import '../../../../../utils/constants/sizes.dart';
import '../../../../../utils/helpers/helpers.dart';

class SRideStatusChip extends StatelessWidget {
  const SRideStatusChip({
    super.key,
    required this.label,
    required this.color,
  });

  final String label;
  final Color color;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(
        horizontal: SSizes.sm,
        vertical: SSizes.xs,
      ),
      decoration: BoxDecoration(
        color: SHelperFunctions.withOpacity(color, SOpacities.placeholder),
        borderRadius: BorderRadius.circular(SSizes.tripsStatusChipRadius),
      ),
      child: Text(
        label,
        style: Theme.of(context).textTheme.labelSmall?.copyWith(
              color: color,
              fontWeight: FontWeight.w800,
            ),
      ),
    );
  }
}
