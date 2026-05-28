import 'package:client/features/location/controllers/ride_search_controller.dart';
import 'package:client/features/location/domain/ride_booking_models.dart';
import 'package:client/utils/constants/sizes.dart';
import 'package:flutter/material.dart';
import 'package:get/get.dart';

class SRideFuelChips extends StatelessWidget {
  const SRideFuelChips({super.key, required this.controller});

  final SRideSearchController controller;

  @override
  Widget build(BuildContext context) {
    return Obx(
      () => Wrap(
        spacing: SSizes.xs,
        runSpacing: SSizes.xs,
        children: [
          for (final type in SFuelType.values)
            FilterChip(
              label: Text(type.value),
              selected: controller.allowedFuelTypes.contains(type),
              onSelected: (_) => controller.toggleFuelType(type),
            ),
        ],
      ),
    );
  }
}
