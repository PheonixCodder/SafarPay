import 'package:flutter/material.dart';

import '../../../../../../data/rides/demi_rides.dart';
import '../../../../../../data/rides/ride_models.dart';
import '../../../../../../utils/constants/colors.dart';
import '../../../../../../utils/constants/sizes.dart';
import '../../../../../../utils/constants/texts.dart';
import '../../widgets/ride_card.dart';
import '../../widgets/ride_display_utils.dart';
import '../../widgets/trips_empty_state.dart';

class ScheduledTripsScreen extends StatelessWidget {
  const ScheduledTripsScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final rides = SDemoRides.items
        .where(
          (ride) =>
              ride.isScheduled &&
              ride.status != RideStatus.completed &&
              ride.status != RideStatus.cancelled,
        )
        .toList(growable: false);

    if (rides.isEmpty) {
      return const STripsEmptyState(title: STexts.tripsNoScheduled);
    }

    return ListView.separated(
      padding: EdgeInsets.zero,
      shrinkWrap: true,
      physics: const NeverScrollableScrollPhysics(),
      itemCount: rides.length,
      separatorBuilder: (context, index) =>
          const SizedBox(height: SSizes.spaceBtnItems),
      itemBuilder: (context, index) {
        final ride = rides[index];
        return SRideCard(
          ride: ride,
          accentColor: SColors.info,
          statusText: STexts.tripsScheduled,
          highlightLabel: STexts.tripsScheduledFor,
          highlightValue: SRideDisplayUtils.dateTime(ride.scheduledAt),
        );
      },
    );
  }
}
