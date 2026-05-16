import 'package:flutter/material.dart';

import '../../../../../../../utils/constants/colors.dart';
import '../../../../../../../utils/constants/sizes.dart';

class SRideDetailsRow extends StatelessWidget {
  const SRideDetailsRow({
    super.key,
    required this.label,
    required this.value,
  });

  final String label;
  final String value;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(bottom: SSizes.sm),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Expanded(
            flex: 3,
            child: Text(
              label,
              style: Theme.of(context).textTheme.bodySmall?.copyWith(
                    color: SColors.textSecondary,
                    fontWeight: FontWeight.w700,
                  ),
            ),
          ),
          const SizedBox(width: SSizes.md),
          Expanded(
            flex: 5,
            child: Text(
              value,
              style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                    color: SColors.textPrimary,
                    fontWeight: FontWeight.w700,
                  ),
              textAlign: TextAlign.right,
            ),
          ),
        ],
      ),
    );
  }
}
