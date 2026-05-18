import 'package:flutter/material.dart';

import '../../../../../utils/constants/colors.dart';
import '../../../../../utils/constants/sizes.dart';

class STripsTabButtonItem extends StatelessWidget {
  const STripsTabButtonItem({
    super.key,
    required this.label,
    required this.isSelected,
    required this.duration,
    required this.curve,
    required this.onTap,
  });

  final String label;
  final bool isSelected;
  final Duration duration;
  final Curve curve;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(SSizes.tripsTabIndicatorRadius),
      child: Center(
        child: AnimatedDefaultTextStyle(
          duration: duration,
          curve: curve,
          style: Theme.of(context).textTheme.labelMedium!.copyWith(
                color: isSelected ? SColors.white : SColors.textSecondary,
                fontWeight: FontWeight.w800,
              ),
          child: Text(label, maxLines: 1, overflow: TextOverflow.ellipsis),
        ),
      ),
    );
  }
}
