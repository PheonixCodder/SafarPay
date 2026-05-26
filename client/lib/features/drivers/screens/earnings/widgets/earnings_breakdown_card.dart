import 'package:flutter/material.dart';

import '../../../../../utils/constants/colors.dart';
import '../../../../../utils/constants/sizes.dart';
import '../../../../../utils/constants/texts.dart';
import '../../../domain/earnings_models.dart';
import 'earnings_breakdown_row.dart';
import 'earnings_formatters.dart';

class SEarningsBreakdownCard extends StatelessWidget {
  const SEarningsBreakdownCard({super.key, required this.earnings});

  final SDriverEarnings earnings;

  @override
  Widget build(BuildContext context) {
    final summary = earnings.summary;

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
            STexts.earningsBreakdown,
            style: Theme.of(context).textTheme.titleLarge?.copyWith(
                  fontWeight: FontWeight.w800,
                ),
          ),
          const SizedBox(height: SSizes.md),
          SEarningsBreakdownRow(
            label: STexts.earningsGross,
            value: sFormatMoney(summary.grossFares, currency: earnings.currency),
          ),
          SEarningsBreakdownRow(
            label: STexts.earningsCashCollected,
            value: sFormatMoney(summary.cashCollected, currency: earnings.currency),
          ),
          SEarningsBreakdownRow(
            label: STexts.earningsPlatformCollected,
            value: sFormatMoney(
              summary.platformCollected,
              currency: earnings.currency,
            ),
          ),
          SEarningsBreakdownRow(
            label: STexts.earningsCommission,
            value:
                '- ${sFormatMoney(summary.commissionTotal, currency: earnings.currency)}',
            isNegative: summary.commissionTotal > 0,
          ),
          SEarningsBreakdownRow(
            label: STexts.earningsAvailableBalance,
            value: sFormatMoney(
              summary.availableBalance,
              currency: earnings.currency,
            ),
          ),
          SEarningsBreakdownRow(
            label: STexts.earningsReservedBalance,
            value: sFormatMoney(
              summary.reservedBalance,
              currency: earnings.currency,
            ),
          ),
          const Divider(height: SSizes.xl),
          SEarningsBreakdownRow(
            label: STexts.earningsTotal,
            value: sFormatMoney(
              summary.netEarnings,
              currency: earnings.currency,
            ),
            isEmphasis: true,
          ),
        ],
      ),
    );
  }
}
