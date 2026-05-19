import 'package:flutter/material.dart';

import '../../../../../../../utils/constants/colors.dart';
import '../../../../../../../utils/constants/sizes.dart';

class STermsLastUpdatedLabel extends StatelessWidget {
  const STermsLastUpdatedLabel({
    super.key,
    required this.lastUpdated,
  });

  final String lastUpdated;

  @override
  Widget build(BuildContext context) {
    return Text(
      'Last Updated: $lastUpdated',
      textAlign: TextAlign.center,
      style: Theme.of(context).textTheme.labelSmall?.copyWith(
            color: SColors.primary,
            fontSize: SSizes.iconXs,
            fontWeight: FontWeight.w700,
          ),
    );
  }
}
