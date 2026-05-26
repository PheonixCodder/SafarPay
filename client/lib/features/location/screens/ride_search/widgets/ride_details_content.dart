import 'package:client/features/location/controllers/ride_search_controller.dart';
import 'package:client/features/location/domain/ride_booking_models.dart';
import 'package:client/features/location/screens/ride_search/widgets/fare_offer_panel.dart';
import 'package:client/features/location/screens/ride_search/widgets/ride_option_section.dart';
import 'package:client/features/location/screens/ride_search/widgets/ride_option_stepper.dart';
import 'package:client/features/location/screens/ride_search/widgets/ride_pricing_options.dart';
import 'package:client/features/location/screens/ride_search/widgets/ride_service_options.dart';
import 'package:client/utils/constants/colors.dart';
import 'package:client/utils/constants/sizes.dart';
import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'package:iconsax/iconsax.dart';

class SRideDetailsContent extends StatelessWidget {
  const SRideDetailsContent({super.key, required this.controller});

  final SRideSearchController controller;

  @override
  Widget build(BuildContext context) {
    final textTheme = Theme.of(context).textTheme;

    return Obx(() {
      final errorMessage = controller.errorMessage.value;

      return Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              IconButton(
                onPressed: () =>
                    controller.sheetMode.value = SBookingSheetMode.vehicles,
                icon: const Icon(Iconsax.arrow_left),
              ),
              Expanded(
                child: Text(
                  'Ride details',
                  style: textTheme.titleLarge?.copyWith(
                    color: SColors.textPrimary,
                    fontWeight: FontWeight.w900,
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: SSizes.sm),
          const SRideOptionStepper(mode: SBookingSheetMode.details),
          const SizedBox(height: SSizes.md),
          SRideOptionSection(
            icon: Iconsax.setting_4,
            title: 'Service requirements',
            subtitle: 'Set passenger, vehicle, safety and delivery needs.',
            child: SRideServiceOptions(controller: controller),
          ),
          const SizedBox(height: SSizes.md),
          SRideOptionSection(
            icon: Iconsax.wallet_2,
            title: 'Fare and payment',
            subtitle: 'Choose fixed or offer-based pricing before review.',
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                SRidePricingOptions(controller: controller),
                const SizedBox(height: SSizes.sm),
                SFareOfferPanel(controller: controller),
              ],
            ),
          ),
          if (errorMessage.isNotEmpty) ...[
            const SizedBox(height: SSizes.sm),
            Text(
              errorMessage,
              style: textTheme.bodySmall?.copyWith(color: SColors.error),
            ),
          ],
          const SizedBox(height: SSizes.md),
          SizedBox(
            width: double.infinity,
            child: ElevatedButton.icon(
              onPressed: controller.showRideReview,
              icon: const Icon(Iconsax.tick_circle),
              label: const Text('Review ride'),
            ),
          ),
        ],
      );
    });
  }
}
