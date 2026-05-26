import 'package:client/utils/constants/colors.dart';
import 'package:client/utils/constants/sizes.dart';
import 'package:flutter/material.dart';

class SRideOptionSection extends StatelessWidget {
  const SRideOptionSection({
    super.key,
    required this.title,
    required this.child,
    this.subtitle,
    this.icon,
  });

  final String title;
  final String? subtitle;
  final IconData? icon;
  final Widget child;

  @override
  Widget build(BuildContext context) {
    final textTheme = Theme.of(context).textTheme;

    return DecoratedBox(
      decoration: BoxDecoration(
        color: SColors.white,
        borderRadius: BorderRadius.circular(SSizes.cardRadiusLg),
        border: Border.all(color: SColors.borderSecondary),
      ),
      child: Padding(
        padding: const EdgeInsets.all(SSizes.md),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                if (icon != null) ...[
                  Icon(icon, color: SColors.primary, size: SSizes.iconMd),
                  const SizedBox(width: SSizes.sm),
                ],
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        title,
                        style: textTheme.titleSmall?.copyWith(
                          color: SColors.textPrimary,
                          fontWeight: FontWeight.w900,
                        ),
                      ),
                      if (subtitle != null) ...[
                        const SizedBox(height: SSizes.xs),
                        Text(
                          subtitle!,
                          style: textTheme.bodySmall?.copyWith(
                            color: SColors.textSecondary,
                          ),
                        ),
                      ],
                    ],
                  ),
                ),
              ],
            ),
            const SizedBox(height: SSizes.md),
            child,
          ],
        ),
      ),
    );
  }
}
