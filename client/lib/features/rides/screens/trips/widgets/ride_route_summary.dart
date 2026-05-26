import 'package:flutter/material.dart';

import '../../../../../data/rides/ride_models.dart';
import '../../../../../utils/constants/colors.dart';
import '../../../../../utils/constants/sizes.dart';
import '../../../../../utils/constants/texts.dart';
import 'ride_route_dot.dart';
import 'ride_route_stop.dart';

class SRideRouteSummary extends StatelessWidget {
  const SRideRouteSummary({
    super.key,
    required this.ride,
  })  : pickupStop = null,
        dropoffStop = null;

  const SRideRouteSummary.fromStops({
    super.key,
    required this.pickupStop,
    required this.dropoffStop,
  }) : ride = null;

  final RideResponse? ride;
  final StopResponse? pickupStop;
  final StopResponse? dropoffStop;

  @override
  Widget build(BuildContext context) {
    final pickup = pickupStop ?? ride?.pickupStop;
    final dropoff = dropoffStop ?? ride?.dropoffStop;

    return IntrinsicHeight(
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Column(
            children: [
              SRideRouteDot(color: SColors.primary),
              Expanded(
                child: Container(
                  width: SSizes.tripsRouteLineWidth,
                  color: SColors.borderSecondary,
                ),
              ),
              SRideRouteDot(color: SColors.textPrimary),
            ],
          ),
          const SizedBox(width: SSizes.md),
          Expanded(
            child: Column(
              children: [
                SRideRouteStop(
                  label: STexts.tripsPickup,
                  title: pickup?.placeName ?? STexts.tripsPickup,
                  address: pickup?.addressLine1,
                ),
                const SizedBox(height: SSizes.md),
                SRideRouteStop(
                  label: STexts.tripsDropoff,
                  title: dropoff?.placeName ?? STexts.tripsDropoff,
                  address: dropoff?.addressLine1,
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
