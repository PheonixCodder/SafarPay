import 'package:flutter/material.dart';

import '../../../utils/constants/colors.dart';
import '../../../utils/constants/sizes.dart';

class SNavigationTab extends StatelessWidget {
  const SNavigationTab({
    super.key,
    required this.icon,
    required this.label,
    required this.isActive,
    required this.activeIcon,
    required this.onTap,
  });

  static const Duration _animationDuration = Duration(milliseconds: 180);

  final IconData icon;
  final IconData activeIcon;
  final String label;
  final bool isActive;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    final color = isActive ? SColors.gold : SColors.onSurfaceVariant;
    final labelStyle =
        Theme.of(context).textTheme.labelLarge ?? const TextStyle();

    return Expanded(
      child: Material(
        color: SColors.transparent,
        child: InkWell(
          onTap: onTap,
          splashColor: SColors.transparent,
          highlightColor: SColors.transparent,
          child: Padding(
            padding: const EdgeInsets.only(
              top: SSizes.md,
              bottom: SSizes.xs,
            ),
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                AnimatedScale(
                  scale: isActive
                      ? SSizes.navigationActiveScale
                      : SSizes.navigationInactiveScale,
                  duration: _animationDuration,
                  curve: Curves.easeOut,
                  child: Icon(
                    isActive ? activeIcon : icon,
                    color: color,
                    size: SSizes.iconMd,
                  ),
                ),
                const SizedBox(height: SSizes.xs),
                AnimatedDefaultTextStyle(
                  duration: _animationDuration,
                  curve: Curves.easeOut,
                  style: labelStyle.copyWith(
                    color: color,
                    fontWeight: FontWeight.w500,
                  ),
                  child: Text(
                    label,
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
