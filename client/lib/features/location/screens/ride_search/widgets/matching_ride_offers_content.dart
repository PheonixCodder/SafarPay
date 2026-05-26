import 'package:client/features/location/controllers/ride_search_controller.dart';
import 'package:client/features/location/domain/bidding_models.dart';
import 'package:client/utils/constants/colors.dart';
import 'package:client/utils/constants/sizes.dart';
import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'package:iconsax/iconsax.dart';

class SMatchingRideOffersContent extends StatelessWidget {
  const SMatchingRideOffersContent({
    super.key,
    required this.controller,
    required this.onAcceptedRideTrackingRequested,
  });

  final SRideSearchController controller;
  final ValueChanged<String>? onAcceptedRideTrackingRequested;

  @override
  Widget build(BuildContext context) {
    final textTheme = Theme.of(context).textTheme;

    return Obx(() {
      final hasSession = controller.biddingSessionId.value.isNotEmpty;
      final acceptedBid = controller.acceptedBid.value;
      final driverBids = controller.driverBids.toList();
      final isCreatingRide = controller.isCreatingRide.value;
      final passengerOffer = controller.passengerOffer.value;
      final createdRideId = controller.createdRideId.value;

      return Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Finding driver offers',
            style: textTheme.titleLarge?.copyWith(
              color: SColors.textPrimary,
              fontWeight: FontWeight.w900,
            ),
          ),
          const SizedBox(height: SSizes.sm),
          Text(
            acceptedBid != null
                ? 'Offer accepted. Preparing ride tracking.'
                : hasSession
                    ? 'Live bidding session connected.'
                    : 'Ride created. Waiting for backend bidding session id.',
            style: textTheme.bodyMedium?.copyWith(
              color: SColors.textSecondary,
            ),
          ),
          const SizedBox(height: SSizes.md),
          LinearProgressIndicator(
            color: SColors.primary,
            backgroundColor: SColors.borderSecondary,
          ),
          const SizedBox(height: SSizes.md),
          Text(
            createdRideId.isEmpty
                ? 'No ride id returned yet.'
                : 'Ride $createdRideId',
            style: textTheme.bodySmall?.copyWith(color: SColors.textSecondary),
          ),
          if (driverBids.isNotEmpty) ...[
            const SizedBox(height: SSizes.md),
            for (final bid in driverBids)
              Padding(
                padding: const EdgeInsets.only(bottom: SSizes.sm),
                child: DecoratedBox(
                  decoration: BoxDecoration(
                    color: SColors.white,
                    borderRadius: BorderRadius.circular(SSizes.cardRadiusLg),
                    border: Border.all(color: SColors.borderSecondary),
                  ),
                  child: ListTile(
                    leading: const Icon(Iconsax.car, color: SColors.primary),
                    title: Text(
                      'PKR${bid.bidAmount.round()}',
                      style: textTheme.titleMedium?.copyWith(
                        color: SColors.textPrimary,
                        fontWeight: FontWeight.w900,
                      ),
                    ),
                    subtitle: Text(
                      '${bid.etaMinutes ?? '-'} min pickup'
                      '${bid.message == null ? '' : ' - ${bid.message}'}',
                    ),
                    trailing: TextButton(
                      onPressed: isCreatingRide ? null : () => _acceptBid(bid),
                      child: const Text('Accept'),
                    ),
                  ),
                ),
              ),
          ],
          if (hasSession && acceptedBid == null) ...[
            const SizedBox(height: SSizes.md),
            SizedBox(
              width: double.infinity,
              child: OutlinedButton.icon(
                onPressed: controller.sendCounterOffer,
                icon: const Icon(Iconsax.refresh),
                label: Text(
                  'Send counter offer PKR${passengerOffer.round()}',
                ),
              ),
            ),
          ],
        ],
      );
    });
  }

  Future<void> _acceptBid(SBid bid) async {
    final accepted = await controller.acceptDriverBid(bid);
    if (!accepted) return;

    final rideId = controller.createdRideId.value;
    if (rideId.isEmpty) {
      controller.errorMessage.value =
          'Ride accepted, but tracking could not open without a ride id.';
      return;
    }

    onAcceptedRideTrackingRequested?.call(rideId);
  }
}
