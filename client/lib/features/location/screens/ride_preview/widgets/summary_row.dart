import 'package:client/utils/constants/colors.dart';
import 'package:client/utils/constants/sizes.dart';
import 'package:flutter/material.dart';

class SSummaryRow extends StatelessWidget {
  const SSummaryRow({
    super.key,
    required this.label,
    required this.value,
  });

  final String label;
  final String value;

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          label,
          style: Theme.of(context).textTheme.labelLarge?.copyWith(
                color: SColors.textSecondary,
              ),
        ),
        const SizedBox(height: SSizes.xs),
        Text(
          value,
          style: Theme.of(context).textTheme.titleMedium?.copyWith(
                color: SColors.textPrimary,
                fontWeight: FontWeight.w700,
              ),
        ),
      ],
    );
  }
}
