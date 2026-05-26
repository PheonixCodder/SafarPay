import 'package:flutter/material.dart';

import '../../../../../utils/constants/colors.dart';
import '../../../../../utils/constants/sizes.dart';

class SEarningsBreakdownRow extends StatelessWidget {
  const SEarningsBreakdownRow({
    super.key,
    required this.label,
    required this.value,
    this.isNegative = false,
    this.isEmphasis = false,
  });

  final String label;
  final String value;
  final bool isNegative;
  final bool isEmphasis;

  @override
  Widget build(BuildContext context) {
    final style = isEmphasis
        ? Theme.of(context).textTheme.titleLarge
        : Theme.of(context).textTheme.bodyLarge;

    return Padding(
      padding: const EdgeInsets.symmetric(vertical: SSizes.sm),
      child: Row(
        children: [
          Expanded(
            child: Text(
              label,
              style: style?.copyWith(
                color: SColors.textPrimary,
                fontWeight: isEmphasis ? FontWeight.w800 : FontWeight.w600,
              ),
            ),
          ),
          const SizedBox(width: SSizes.md),
          Flexible(
            child: Text(
              value,
              textAlign: TextAlign.right,
              style: style?.copyWith(
                color: isNegative ? SColors.error : SColors.textPrimary,
                fontWeight: isEmphasis ? FontWeight.w800 : FontWeight.w700,
              ),
            ),
          ),
        ],
      ),
    );
  }
}
