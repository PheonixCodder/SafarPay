import 'package:client/features/location/controllers/ride_search_controller.dart';
import 'package:client/features/location/screens/ride_search/widgets/ride_stepper_tile.dart';
import 'package:client/features/location/screens/ride_search/widgets/ride_switch_tile.dart';
import 'package:flutter/material.dart';

class SFreightRideOptionsForm extends StatelessWidget {
  const SFreightRideOptionsForm({super.key, required this.controller});

  final SRideSearchController controller;

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        TextField(
          controller: controller.freightCargoTypeController,
          decoration: const InputDecoration(labelText: 'Cargo type'),
        ),
        SRideStepperTile(
          label: 'Cargo weight kg',
          value: controller.freightCargoWeight.value.round(),
          onMinus: () => controller.freightCargoWeight.value =
              (controller.freightCargoWeight.value - 10)
                  .clamp(1, 10000)
                  .toDouble(),
          onPlus: () => controller.freightCargoWeight.value =
              (controller.freightCargoWeight.value + 10)
                  .clamp(1, 10000)
                  .toDouble(),
        ),
        SRideSwitchTile(
          label: 'Loader required',
          value: controller.freightRequiresLoader.value,
          onChanged: (value) => controller.freightRequiresLoader.value = value,
        ),
        SRideSwitchTile(
          label: 'Fragile cargo',
          value: controller.freightIsFragile.value,
          onChanged: (value) => controller.freightIsFragile.value = value,
        ),
        SRideSwitchTile(
          label: 'Temperature control',
          value: controller.freightRequiresTemperatureControl.value,
          onChanged: (value) =>
              controller.freightRequiresTemperatureControl.value = value,
        ),
      ],
    );
  }
}
