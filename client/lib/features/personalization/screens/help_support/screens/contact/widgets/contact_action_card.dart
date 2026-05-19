import 'package:flutter/material.dart';

import '../../../../../../../utils/constants/colors.dart';
import '../../../../../../../utils/constants/sizes.dart';
import '../../../../../../../utils/helpers/helpers.dart';

class SContactActionCard extends StatelessWidget {
  const SContactActionCard({
    super.key,
    required this.icon,
    required this.label,
    required this.color,
    required this.onTap,
  });

  final IconData icon;
  final String label;
  final Color color;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return Expanded(
      child: Material(
        color: SColors.white,
        borderRadius: BorderRadius.circular(SSizes.cardRadiusMd),
        elevation: SSizes.cardElevation,
        shadowColor: SHelperFunctions.withOpacity(
          SColors.pureBlack,
          SOpacities.placeholder,
        ),
        child: InkWell(
          onTap: onTap,
          borderRadius: BorderRadius.circular(SSizes.cardRadiusMd),
          child: Padding(
            padding: const EdgeInsets.symmetric(
              horizontal: SSizes.sm,
              vertical: SSizes.md,
            ),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                Container(
                  width: 42,
                  height: 42,
                  decoration: BoxDecoration(
                    color: SHelperFunctions.withOpacity(
                      color,
                      SOpacities.successTint,
                    ),
                    shape: BoxShape.circle,
                  ),
                  child: Icon(icon, color: color, size: SSizes.iconMd),
                ),
                const SizedBox(height: SSizes.sm),
                Text(
                  label,
                  style: Theme.of(context).textTheme.labelMedium?.copyWith(
                        color: color,
                        fontWeight: FontWeight.w700,
                      ),
                  textAlign: TextAlign.center,
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
