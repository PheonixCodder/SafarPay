import 'package:flutter/material.dart';

import '../../../../../utils/constants/colors.dart';
import '../../../../../utils/constants/sizes.dart';
import '../../../../../utils/constants/texts.dart';
import '../../../domain/earnings_models.dart';
import 'earnings_recent_trip_tile.dart';

class SEarningsRecentTripsCard extends StatelessWidget {
  const SEarningsRecentTripsCard({super.key, required this.trips});

  final List<SDriverEarningsTrip> trips;

  @override
  Widget build(BuildContext context) {
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
            STexts.earningsRecentTrips,
            style: Theme.of(context).textTheme.titleLarge?.copyWith(
                  fontWeight: FontWeight.w800,
                ),
          ),
          const SizedBox(height: SSizes.md),
          if (trips.isEmpty)
            Text(
              STexts.earningsEmptySubTitle,
              style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                    color: SColors.textSecondary,
                  ),
            )
          else
            for (final trip in trips) SEarningsRecentTripTile(trip: trip),
        ],
      ),
    );
  }
}
