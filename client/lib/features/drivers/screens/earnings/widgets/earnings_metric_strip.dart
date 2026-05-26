import 'package:flutter/material.dart';
import 'package:iconsax/iconsax.dart';

import '../../../../../utils/constants/colors.dart';
import '../../../../../utils/constants/sizes.dart';
import '../../../../../utils/constants/texts.dart';
import '../../../domain/earnings_models.dart';
import 'earnings_metric_tile.dart';
import 'earnings_formatters.dart';

class SEarningsMetricStrip extends StatelessWidget {
  const SEarningsMetricStrip({super.key, required this.summary});

  final SDriverEarningsSummary summary;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(vertical: SSizes.md),
      decoration: BoxDecoration(
        color: SColors.white,
        borderRadius: BorderRadius.circular(SSizes.borderRadiusMd),
        border: Border.all(color: SColors.borderSecondary),
      ),
      child: Row(
        children: [
          Expanded(
            child: SEarningsMetricTile(
              icon: Iconsax.routing_2,
              value: summary.completedTrips.toString(),
              label: STexts.earningsTrips,
            ),
          ),
          const SizedBox(
            height: 52,
            child: VerticalDivider(color: SColors.borderSecondary),
          ),
          Expanded(
            child: SEarningsMetricTile(
              icon: Iconsax.clock,
              value: sFormatMinutes(summary.activeMinutes),
              label: STexts.earningsOnline,
            ),
          ),
          const SizedBox(
            height: 52,
            child: VerticalDivider(color: SColors.borderSecondary),
          ),
          Expanded(
            child: SEarningsMetricTile(
              icon: Iconsax.star1,
              value: summary.ratingAvg?.toStringAsFixed(1) ?? '-',
              label: STexts.earningsRating,
            ),
          ),
        ],
      ),
    );
  }
}
