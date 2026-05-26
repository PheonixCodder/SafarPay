import 'package:client/features/location/controllers/ride_search_controller.dart';
import 'package:client/features/location/screens/ride_search/widgets/ride_stepper_tile.dart';
import 'package:client/features/location/screens/ride_search/widgets/ride_switch_tile.dart';
import 'package:flutter/material.dart';

class SCourierRideOptionsForm extends StatelessWidget {
  const SCourierRideOptionsForm({super.key, required this.controller});

  final SRideSearchController controller;

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        TextField(
          controller: controller.courierItemController,
          decoration: const InputDecoration(labelText: 'Item description'),
        ),
        TextField(
          controller: controller.courierRecipientNameController,
          decoration: const InputDecoration(labelText: 'Recipient name'),
        ),
        TextField(
          controller: controller.courierRecipientPhoneController,
          keyboardType: TextInputType.phone,
          decoration: const InputDecoration(labelText: 'Recipient phone'),
        ),
        SRideStepperTile(
          label: 'Parcels',
          value: controller.courierParcelCount.value,
          onMinus: () => controller.courierParcelCount.value =
              (controller.courierParcelCount.value - 1).clamp(1, 20).toInt(),
          onPlus: () => controller.courierParcelCount.value =
              (controller.courierParcelCount.value + 1).clamp(1, 20).toInt(),
        ),
        SRideSwitchTile(
          label: 'Fragile item',
          value: controller.courierIsFragile.value,
          onChanged: (value) => controller.courierIsFragile.value = value,
        ),
        SRideSwitchTile(
          label: 'Signature required',
          value: controller.courierRequiresSignature.value,
          onChanged: (value) =>
              controller.courierRequiresSignature.value = value,
        ),
      ],
    );
  }
}
