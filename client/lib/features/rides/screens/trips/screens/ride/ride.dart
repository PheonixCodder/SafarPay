import 'package:flutter/material.dart';

import '../../../../../../common/widgets/appbar/appbar.dart';
import '../../../../../../data/rides/ride_models.dart';
import '../../../../../../features/location/data/ride_repository.dart';
import '../../../../../../utils/constants/colors.dart';
import '../../../../../../utils/constants/sizes.dart';
import '../../../../../../utils/constants/texts.dart';
import '../../widgets/ride_display_utils.dart';
import '../../widgets/ride_route_summary.dart';
import 'widgets/ride_details_panel.dart';
import 'widgets/ride_details_row.dart';

class RideDetailsScreen extends StatefulWidget {
  const RideDetailsScreen({
    super.key,
    required this.rideId,
  });

  final String rideId;

  @override
  State<RideDetailsScreen> createState() => _RideDetailsScreenState();
}

class _RideDetailsScreenState extends State<RideDetailsScreen> {
  late Future<RideResponse> _rideFuture;
  final SRideRepository _repository = const SRideRepository();

  @override
  void initState() {
    super.initState();
    _rideFuture = _fetchRide();
  }

  Future<RideResponse> _fetchRide() async {
    return RideResponse.fromJson(await _repository.fetchRide(widget.rideId));
  }

  void _retry() {
    setState(() => _rideFuture = _fetchRide());
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: SColors.primaryBackground,
      appBar: const SAppBar(
        showBackArrow: true,
        title: Text(STexts.tripsRideDetails),
      ),
      body: FutureBuilder<RideResponse>(
        future: _rideFuture,
        builder: (context, snapshot) {
          if (snapshot.connectionState != ConnectionState.done) {
            return const Center(child: CircularProgressIndicator());
          }
          if (snapshot.hasError || snapshot.data == null) {
            return Center(
              child: Padding(
                padding: const EdgeInsets.all(SSizes.defaultSpace),
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Text(
                      'Unable to load ride details.',
                      textAlign: TextAlign.center,
                      style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                            color: SColors.textSecondary,
                          ),
                    ),
                    const SizedBox(height: SSizes.md),
                    OutlinedButton(
                      onPressed: _retry,
                      child: const Text('Try again'),
                    ),
                  ],
                ),
              ),
            );
          }

          final ride = snapshot.data!;
          return SingleChildScrollView(
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
                        value: SRideDisplayUtils.payment(
                          ride.passengerPaymentMethod,
                        ),
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
                          label:
                              '${stop.sequenceOrder}. ${stop.stopType.value}',
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
          );
        },
      ),
    );
  }
}
