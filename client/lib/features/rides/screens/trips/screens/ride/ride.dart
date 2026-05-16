import 'package:flutter/material.dart';

import '../../../../../../common/widgets/appbar/appbar.dart';
import '../../../../../../data/rides/ride_models.dart';
import '../../../../../../utils/constants/colors.dart';
import '../../../../../../utils/constants/sizes.dart';
import '../../../../../../utils/constants/texts.dart';
import '../../widgets/ride_display_utils.dart';
import '../../widgets/ride_route_summary.dart';
import 'widgets/ride_details_panel.dart';
import 'widgets/ride_details_row.dart';

class RideDetailsScreen extends StatelessWidget {
  const RideDetailsScreen({
    super.key,
    required this.ride,
  });

  final RideResponse ride;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: SColors.primaryBackground,
      appBar: const SAppBar(
        showBackArrow: true,
        title: Text(STexts.tripsRideDetails),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(SSizes.defaultSpace),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            SRideDetailsPanel(
              title: STexts.tripsRoute,
              child: SRideRouteSummary(ride: ride),
            ),
            const SizedBox(height: SSizes.spaceBtnItems),
            SRideDetailsPanel(
              title: STexts.tripsRideSummary,
              child: Column(
                children: [
                  SRideDetailsRow(
                    label: STexts.tripsService,
                    value: SRideDisplayUtils.service(ride.serviceType),
                  ),
                  SRideDetailsRow(
                    label: STexts.tripsCategory,
                    value: SRideDisplayUtils.category(ride.category),
                  ),
                  SRideDetailsRow(
                    label: STexts.tripsPricing,
                    value: SRideDisplayUtils.pricing(ride.pricingMode),
                  ),
                  SRideDetailsRow(
                    label: STexts.tripsPaymentMethod,
                    value:
                        SRideDisplayUtils.payment(ride.passengerPaymentMethod),
                  ),
                  SRideDetailsRow(
                    label: STexts.tripsPrice,
                    value: SRideDisplayUtils.money(ride.finalPrice),
                  ),
                  SRideDetailsRow(
                    label: STexts.tripsCreated,
                    value: SRideDisplayUtils.dateTime(ride.createdAt),
                  ),
                  if (ride.scheduledAt != null)
                    SRideDetailsRow(
                      label: STexts.tripsScheduledFor,
                      value: SRideDisplayUtils.dateTime(ride.scheduledAt),
                    ),
                  if (ride.completedAt != null)
                    SRideDetailsRow(
                      label: STexts.tripsCompletedAt,
                      value: SRideDisplayUtils.dateTime(ride.completedAt),
                    ),
                  if (ride.cancelledAt != null)
                    SRideDetailsRow(
                      label: STexts.tripsCanceledAt,
                      value: SRideDisplayUtils.dateTime(ride.cancelledAt),
                    ),
                  if (ride.cancellationReason != null)
                    SRideDetailsRow(
                      label: STexts.tripsCancellationReason,
                      value: ride.cancellationReason!,
                    ),
                ],
              ),
            ),
            const SizedBox(height: SSizes.spaceBtnItems),
            SRideDetailsPanel(
              title: STexts.tripsStops,
              child: Column(
                children: [
                  for (final stop in ride.stops)
                    SRideDetailsRow(
                      label: '${stop.sequenceOrder}. ${stop.stopType.value}',
                      value: stop.placeName ?? stop.addressLine1 ?? 'Stop',
                    ),
                ],
              ),
            ),
            const SizedBox(height: SSizes.spaceBtnItems),
            SRideDetailsPanel(
              title: STexts.tripsOperational,
              child: Column(
                children: [
                  SRideDetailsRow(
                    label: STexts.tripsDriverAssigned,
                    value: ride.assignedDriverId == null ? 'No' : 'Yes',
                  ),
                  SRideDetailsRow(
                    label: STexts.tripsProofs,
                    value: ride.proofImages.length.toString(),
                  ),
                  SRideDetailsRow(
                    label: STexts.tripsVerificationCodes,
                    value: ride.verificationCodes.length.toString(),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}
