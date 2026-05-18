import 'package:client/features/location/domain/location_models.dart';
import 'package:client/features/location/screens/ride_preview/widgets/summary_row.dart';
import 'package:client/utils/constants/colors.dart';
import 'package:client/utils/constants/sizes.dart';
import 'package:client/utils/constants/texts.dart';
import 'package:flutter/material.dart';

class SRouteSummary extends StatelessWidget {
  const SRouteSummary({
    super.key,
    required this.pickup,
    required this.dropoff,
    required this.route,
    required this.errorMessage,
  });

  final SAddressResult pickup;
  final SAddressResult dropoff;
  final SRoutePreview? route;
  final String errorMessage;

  @override
  Widget build(BuildContext context) {
    return DecoratedBox(
      decoration: BoxDecoration(
        color: SColors.white,
        borderRadius: BorderRadius.circular(SSizes.rideSheetRadius),
      ),
      child: Padding(
        padding: const EdgeInsets.all(SSizes.lg),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            SSummaryRow(label: STexts.tripsPickup, value: pickup.formatted),
            const SizedBox(height: SSizes.md),
            SSummaryRow(label: STexts.tripsDropoff, value: dropoff.formatted),
            const SizedBox(height: SSizes.md),
            if (route != null)
              SSummaryRow(
                label: STexts.tripsRoute,
                value:
                    '${route!.distanceKm.toStringAsFixed(1)} km - ${route!.durationMinutes.round()} min',
              )
            else
              SSummaryRow(
                label: STexts.tripsRoute,
                value: errorMessage.isEmpty
                    ? STexts.ridePreviewUnavailable
                    : errorMessage,
              ),
          ],
        ),
      ),
    );
  }
}
