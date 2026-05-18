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
  });

  final RideResponse ride;

  @override
  Widget build(BuildContext context) {
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
                  title: ride.pickupStop?.placeName ?? STexts.tripsPickup,
                  address: ride.pickupStop?.addressLine1,
                ),
                const SizedBox(height: SSizes.md),
                SRideRouteStop(
                  label: STexts.tripsDropoff,
                  title: ride.dropoffStop?.placeName ?? STexts.tripsDropoff,
                  address: ride.dropoffStop?.addressLine1,
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
