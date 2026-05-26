import 'package:flutter/material.dart';

import '../../../../../utils/constants/colors.dart';
import '../../../../../utils/constants/sizes.dart';
import '../../../../../utils/constants/texts.dart';
import '../../../../../utils/helpers/helpers.dart';
import '../../../domain/earnings_models.dart';

class SEarningsOverviewChart extends StatelessWidget {
  const SEarningsOverviewChart({super.key, required this.items});

  final List<SDriverEarningsBreakdownItem> items;

  @override
  Widget build(BuildContext context) {
    final maxValue = items.fold<double>(
      0,
      (value, item) => item.netEarnings > value ? item.netEarnings : value,
    );

    return Container(
      padding: const EdgeInsets.all(SSizes.lg),
      decoration: BoxDecoration(
        color: SColors.white,
        borderRadius: BorderRadius.circular(SSizes.borderRadiusMd),
        border: Border.all(color: SColors.borderSecondary),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            STexts.earningsOverview,
            style: Theme.of(context).textTheme.titleLarge?.copyWith(
                  fontWeight: FontWeight.w800,
                ),
          ),
          const SizedBox(height: SSizes.lg),
          SizedBox(
            height: 190,
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.end,
              children: [
                for (final item in items)
                  Expanded(
                    child: Padding(
                      padding: const EdgeInsets.symmetric(horizontal: 4),
                      child: Column(
                        mainAxisAlignment: MainAxisAlignment.end,
                        children: [
                          Expanded(
                            child: Align(
                              alignment: Alignment.bottomCenter,
                              child: FractionallySizedBox(
                                heightFactor: maxValue <= 0
                                    ? 0.04
                                    : (item.netEarnings / maxValue)
                                        .clamp(0.04, 1),
                                child: Container(
                                  width: 24,
                                  decoration: BoxDecoration(
                                    color: item.netEarnings > 0
                                        ? SColors.primary
                                        : SHelperFunctions.withOpacity(
                                            SColors.primary,
                                            SOpacities.placeholder,
                                          ),
                                    borderRadius: BorderRadius.circular(
                                      SSizes.borderRadiusSm,
                                    ),
                                  ),
                                ),
                              ),
                            ),
                          ),
                          const SizedBox(height: SSizes.sm),
                          FittedBox(
                            fit: BoxFit.scaleDown,
                            child: Text(
                              item.label,
                              style:
                                  Theme.of(context).textTheme.bodySmall?.copyWith(
                                        color: SColors.textSecondary,
                                        fontWeight: FontWeight.w700,
                                      ),
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
