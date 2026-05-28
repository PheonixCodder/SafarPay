import 'package:client/features/location/controllers/ride_search_controller.dart';
import 'package:client/features/location/screens/ride_search/widgets/ride_stepper_tile.dart';
import 'package:client/features/location/screens/ride_search/widgets/ride_switch_tile.dart';
import 'package:flutter/material.dart';
import 'package:get/get.dart';

class SIntercityRideOptionsForm extends StatelessWidget {
  const SIntercityRideOptionsForm({super.key, required this.controller});

  final SRideSearchController controller;

  @override
  Widget build(BuildContext context) {
    return Obx(
      () => Column(
        children: [
          SRideStepperTile(
            label: 'Passengers',
            value: controller.intercityPassengerCount.value,
            onMinus: () => controller.intercityPassengerCount.value =
                (controller.intercityPassengerCount.value - 1)
                    .clamp(1, 12)
                    .toInt(),
            onPlus: () => controller.intercityPassengerCount.value =
                (controller.intercityPassengerCount.value + 1)
                    .clamp(1, 12)
                    .toInt(),
          ),
          SRideStepperTile(
            label: 'Luggage',
            value: controller.luggageCount.value,
            onMinus: () => controller.luggageCount.value =
                (controller.luggageCount.value - 1).clamp(0, 20).toInt(),
            onPlus: () => controller.luggageCount.value =
                (controller.luggageCount.value + 1).clamp(0, 20).toInt(),
          ),
          SRideSwitchTile(
            label: 'Shared intercity ride',
            value: controller.isSharedIntercityRide.value,
            onChanged: (value) =>
                controller.isSharedIntercityRide.value = value,
          ),
          if (controller.isSharedIntercityRide.value)
            SRideStepperTile(
              label: 'Max co-passengers',
              value: controller.maxCoPassengers.value,
              onMinus: () => controller.maxCoPassengers.value =
                  (controller.maxCoPassengers.value - 1).clamp(1, 8).toInt(),
              onPlus: () => controller.maxCoPassengers.value =
                  (controller.maxCoPassengers.value + 1).clamp(1, 8).toInt(),
            ),
          SRideSwitchTile(
            label: 'Round trip',
            value: controller.isRoundTrip.value,
            onChanged: (value) => controller.isRoundTrip.value = value,
          ),
          SRideSwitchTile(
            label: 'Luggage carrier required',
            value: controller.requiresLuggageCarrier.value,
            onChanged: (value) =>
                controller.requiresLuggageCarrier.value = value,
          ),
          SRideSwitchTile(
            label: 'Identity verification required',
            value: controller.requiresIdentityVerification.value,
            onChanged: (value) =>
                controller.requiresIdentityVerification.value = value,
          ),
          TextField(
            controller: controller.emergencyContactPhoneController,
            keyboardType: TextInputType.phone,
            decoration: const InputDecoration(labelText: 'Emergency phone'),
          ),
        ],
      ),
    );
  }
}
