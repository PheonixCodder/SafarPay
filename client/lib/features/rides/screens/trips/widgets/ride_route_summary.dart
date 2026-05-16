import 'package:flutter/material.dart';

import '../../../../../data/rides/ride_models.dart';
import '../../../../../utils/constants/colors.dart';
import '../../../../../utils/constants/sizes.dart';
import '../../../../../utils/constants/texts.dart';

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
              _RouteDot(color: SColors.primary),
              Expanded(
                child: Container(
                  width: SSizes.tripsRouteLineWidth,
                  color: SColors.borderSecondary,
                ),
              ),
              _RouteDot(color: SColors.textPrimary),
            ],
          ),
          const SizedBox(width: SSizes.md),
          Expanded(
            child: Column(
              children: [
                _RouteStop(
                  label: STexts.tripsPickup,
                  title: ride.pickupStop?.placeName ?? STexts.tripsPickup,
                  address: ride.pickupStop?.addressLine1,
                ),
                const SizedBox(height: SSizes.md),
                _RouteStop(
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

class _RouteDot extends StatelessWidget {
  const _RouteDot({required this.color});

  final Color color;

  @override
  Widget build(BuildContext context) {
    return Container(
      width: SSizes.tripsRouteDotSize,
      height: SSizes.tripsRouteDotSize,
      decoration: BoxDecoration(color: color, shape: BoxShape.circle),
    );
  }
}

class _RouteStop extends StatelessWidget {
  const _RouteStop({
    required this.label,
    required this.title,
    this.address,
  });

  final String label;
  final String title;
  final String? address;

  @override
  Widget build(BuildContext context) {
    return Align(
      alignment: Alignment.centerLeft,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            label,
            style: Theme.of(context).textTheme.labelMedium?.copyWith(
                  color: SColors.textSecondary,
                  fontWeight: FontWeight.w700,
                ),
          ),
          const SizedBox(height: SSizes.xs),
          Text(
            title,
            style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                  color: SColors.textPrimary,
                  fontWeight: FontWeight.w700,
                ),
            maxLines: 1,
            overflow: TextOverflow.ellipsis,
          ),
          if (address != null) ...[
            const SizedBox(height: SSizes.xs),
            Text(
              address!,
              style: Theme.of(context).textTheme.bodySmall?.copyWith(
                    color: SColors.textSecondary,
                    height: 1.25,
                  ),
              maxLines: 1,
              overflow: TextOverflow.ellipsis,
            ),
          ],
        ],
      ),
    );
  }
}
