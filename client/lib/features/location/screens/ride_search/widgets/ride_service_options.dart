import 'package:client/data/rides/ride_models.dart';
import 'package:client/features/location/controllers/ride_search_controller.dart';
import 'package:client/features/location/screens/ride_search/widgets/city_ride_options.dart';
import 'package:client/features/location/screens/ride_search/widgets/courier_ride_options.dart';
import 'package:client/features/location/screens/ride_search/widgets/freight_ride_options.dart';
import 'package:client/features/location/screens/ride_search/widgets/intercity_ride_options.dart';
import 'package:client/features/location/screens/ride_search/widgets/ride_fuel_chips.dart';
import 'package:client/utils/constants/colors.dart';
import 'package:client/utils/constants/sizes.dart';
import 'package:flutter/material.dart';
import 'package:get/get.dart';

class SRideServiceOptions extends StatelessWidget {
  const SRideServiceOptions({super.key, required this.controller});

  final SRideSearchController controller;

  @override
  Widget build(BuildContext context) {
    return Obx(() {
      final offer = controller.selectedVehicle.value;
      if (offer == null) return const SizedBox.shrink();

      return Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Service details',
            style: Theme.of(context).textTheme.titleMedium?.copyWith(
                  color: SColors.textPrimary,
                  fontWeight: FontWeight.w900,
                ),
          ),
          const SizedBox(height: SSizes.sm),
          switch (offer.serviceType) {
            ServiceType.cityRide => SCityRideOptionsForm(
                controller: controller,
              ),
            ServiceType.intercity => SIntercityRideOptionsForm(
                controller: controller,
              ),
            ServiceType.freight => SFreightRideOptionsForm(
                controller: controller,
              ),
            ServiceType.courier => SCourierRideOptionsForm(
                controller: controller,
              ),
            ServiceType.grocery => const Text(
                'Store selection is required before grocery booking is enabled.',
              ),
          },
          const SizedBox(height: SSizes.sm),
          SRideFuelChips(controller: controller),
        ],
      );
    });
  }
}
