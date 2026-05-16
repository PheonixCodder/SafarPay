import 'package:flutter/material.dart';

import '../../../../../../data/rides/demi_rides.dart';
import '../../../../../../data/rides/ride_models.dart';
import '../../../../../../utils/constants/colors.dart';
import '../../../../../../utils/constants/sizes.dart';
import '../../../../../../utils/constants/texts.dart';
import '../../widgets/ride_card.dart';
import '../../widgets/ride_display_utils.dart';
import '../../widgets/trips_empty_state.dart';

class OngoingTripsScreen extends StatelessWidget {
  const OngoingTripsScreen({super.key});

  static const Set<RideStatus> _ongoingStatuses = {
    RideStatus.created,
    RideStatus.matching,
    RideStatus.accepted,
    RideStatus.arriving,
    RideStatus.inProgress,
  };

  @override
  Widget build(BuildContext context) {
    final rides = SDemoRides.items
        .where((ride) =>
            _ongoingStatuses.contains(ride.status) && !ride.isScheduled)
        .toList(growable: false);

    if (rides.isEmpty) {
      return const STripsEmptyState(title: STexts.tripsNoOngoing);
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
          accentColor: SColors.primary,
          statusText: SRideDisplayUtils.status(ride.status),
          highlightLabel: ride.assignedDriverId == null
              ? STexts.tripsDriverPending
              : STexts.tripsDriverAssigned,
          highlightValue: SRideDisplayUtils.dateTime(
            ride.acceptedAt ?? ride.createdAt,
          ),
        );
      },
    );
  }
}
