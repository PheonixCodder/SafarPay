import 'package:client/data/rides/ride_models.dart';
import 'package:client/features/location/controllers/ride_search_controller.dart';
import 'package:client/utils/constants/colors.dart';
import 'package:client/utils/constants/sizes.dart';
import 'package:flutter/material.dart';
import 'package:get/get.dart';

class SRideReviewSummary extends StatelessWidget {
  const SRideReviewSummary({super.key, required this.controller});

  final SRideSearchController controller;

  @override
  Widget build(BuildContext context) {
    final textTheme = Theme.of(context).textTheme;

    return Obx(() {
      final offer = controller.selectedVehicle.value;
      final route = controller.route.value;
      final rideId = controller.createdRideId.value;

      return DecoratedBox(
        decoration: BoxDecoration(
          color: SColors.white,
          borderRadius: BorderRadius.circular(SSizes.cardRadiusLg),
          border: Border.all(color: SColors.borderSecondary),
        ),
        child: Padding(
          padding: const EdgeInsets.all(SSizes.md),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                rideId.isEmpty ? 'Review ride' : 'Ride created',
                style: textTheme.titleMedium?.copyWith(
                  color: SColors.textPrimary,
                  fontWeight: FontWeight.w900,
                ),
              ),
              const SizedBox(height: SSizes.sm),
              _row('Ride', offer?.title ?? '-'),
              _row(
                'Route',
                route == null
                    ? 'Route preview unavailable'
                    : '${route.distanceKm.toStringAsFixed(1)} km - ${route.durationMinutes.round()} min',
              ),
              _row('Pricing', _pricingLabel(controller.pricingMode.value)),
              _row('Payment', controller.paymentMethod.value.value),
              _row('Offer', 'PKR${controller.passengerOffer.value.round()}'),
              if (controller.scheduledAt.value != null)
                _row('Schedule', 'About 1 hour from now'),
              if (rideId.isNotEmpty) _row('Ride id', rideId),
            ],
          ),
        ),
      );
    });
  }

  Widget _row(String label, String value) {
    return Padding(
      padding: const EdgeInsets.only(bottom: SSizes.xs),
      child: Row(
        children: [
          SizedBox(
            width: 84,
            child: Text(
              label,
              style: const TextStyle(color: SColors.textSecondary),
            ),
          ),
          Expanded(
            child: Text(
              value,
              style: const TextStyle(
                color: SColors.textPrimary,
                fontWeight: FontWeight.w700,
              ),
            ),
          ),
        ],
      ),
    );
  }

  String _pricingLabel(PricingMode mode) {
    return switch (mode) {
      PricingMode.fixed => 'Fixed fare',
      PricingMode.hybrid => 'Hybrid offers',
      PricingMode.bidBased => 'Bid based',
    };
  }
}
