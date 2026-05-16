import 'package:flutter/material.dart';

import '../../../../../../data/rides/demi_rides.dart';
import '../../../../../../data/rides/ride_models.dart';
import '../../../../../../utils/constants/colors.dart';
import '../../../../../../utils/constants/sizes.dart';
import '../../../../../../utils/constants/texts.dart';
import '../../widgets/ride_card.dart';
import '../../widgets/trips_empty_state.dart';

class CanceledTripsScreen extends StatelessWidget {
  const CanceledTripsScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final rides = SDemoRides.items
        .where((ride) => ride.status == RideStatus.cancelled)
        .toList(growable: false);

    if (rides.isEmpty) {
      return const STripsEmptyState(title: STexts.tripsNoCanceled);
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
          accentColor: SColors.error,
          statusText: STexts.tripsCanceled,
          highlightLabel: STexts.tripsCancellationReason,
          highlightValue: ride.cancellationReason ?? 'Not provided',
        );
      },
    );
  }
}
