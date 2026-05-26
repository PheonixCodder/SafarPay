import 'package:flutter/material.dart';

import '../../../../utils/constants/colors.dart';
import '../../../../utils/constants/sizes.dart';

class SCallControlButton extends StatelessWidget {
  const SCallControlButton({
    super.key,
    required this.icon,
    required this.label,
    required this.onPressed,
    this.color,
  });

  final IconData icon;
  final String label;
  final VoidCallback onPressed;
  final Color? color;

  @override
  Widget build(BuildContext context) {
    final foreground = color ?? SColors.white;
    return Column(
      mainAxisSize: MainAxisSize.min,
      children: [
        IconButton.filled(
          style: IconButton.styleFrom(
            backgroundColor: color ?? SColors.black,
            foregroundColor: SColors.white,
            fixedSize: const Size(64, 64),
          ),
          onPressed: onPressed,
          icon: Icon(icon),
        ),
        const SizedBox(height: SSizes.sm),
        Text(
          label,
          style: Theme.of(context).textTheme.labelMedium?.copyWith(
                color: foreground,
                fontWeight: FontWeight.w700,
              ),
        ),
      ],
    );
  }
}
