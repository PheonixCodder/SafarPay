import 'package:flutter/material.dart';

import '../../../../../utils/constants/sizes.dart';
import '../../../domain/earnings_models.dart';
import 'earnings_breakdown_card.dart';
import 'earnings_empty_state.dart';
import 'earnings_metric_strip.dart';
import 'earnings_overview_chart.dart';
import 'earnings_recent_trips_card.dart';
import 'earnings_summary_card.dart';
import 'earnings_withdraw_button.dart';

class SEarningsBody extends StatelessWidget {
  const SEarningsBody({
    super.key,
    required this.earnings,
    required this.isLoading,
    required this.errorMessage,
  });

  final SDriverEarnings? earnings;
  final bool isLoading;
  final String errorMessage;

  @override
  Widget build(BuildContext context) {
    if (isLoading && earnings == null) {
      return const Center(child: CircularProgressIndicator());
    }

    final data = earnings;
    if (data == null) {
      return SEarningsEmptyState(message: errorMessage);
    }

    return ListView(
      padding: const EdgeInsets.all(SSizes.defaultSpace),
      children: [
        SEarningsSummaryCard(earnings: data),
        const SizedBox(height: SSizes.spaceBtnItems),
        SEarningsMetricStrip(summary: data.summary),
        const SizedBox(height: SSizes.spaceBtnItems),
        SEarningsOverviewChart(items: data.dailyBreakdown),
        const SizedBox(height: SSizes.spaceBtnItems),
        SEarningsBreakdownCard(earnings: data),
        const SizedBox(height: SSizes.spaceBtnItems),
        SEarningsRecentTripsCard(trips: data.recentTrips),
        const SizedBox(height: SSizes.spaceBtnItems),
        SEarningsWithdrawButton(earnings: data),
      ],
    );
  }
}
