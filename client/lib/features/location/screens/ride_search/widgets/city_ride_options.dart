import 'package:client/features/location/controllers/ride_search_controller.dart';
import 'package:client/features/location/domain/ride_booking_models.dart';
import 'package:client/features/location/screens/ride_search/widgets/ride_stepper_tile.dart';
import 'package:client/features/location/screens/ride_search/widgets/ride_switch_tile.dart';
import 'package:flutter/material.dart';
import 'package:get/get.dart';

class SCityRideOptionsForm extends StatelessWidget {
  const SCityRideOptionsForm({super.key, required this.controller});

  final SRideSearchController controller;

  @override
  Widget build(BuildContext context) {
    return Obx(
      () => Column(
        children: [
          SRideStepperTile(
            label: 'Passengers',
            value: controller.cityPassengerCount.value,
            onMinus: () => controller.cityPassengerCount.value =
                (controller.cityPassengerCount.value - 1).clamp(1, 8).toInt(),
            onPlus: () => controller.cityPassengerCount.value =
                (controller.cityPassengerCount.value + 1).clamp(1, 8).toInt(),
          ),
          DropdownButtonFormField<SDriverGenderPreference>(
            initialValue: controller.driverGenderPreference.value,
            decoration: const InputDecoration(labelText: 'Driver preference'),
            items: const [
              DropdownMenuItem(
                value: SDriverGenderPreference.noPreference,
                child: Text('No preference'),
              ),
              DropdownMenuItem(
                value: SDriverGenderPreference.female,
                child: Text('Female driver'),
              ),
              DropdownMenuItem(
                value: SDriverGenderPreference.male,
                child: Text('Male driver'),
              ),
            ],
            onChanged: (value) {
              if (value != null) {
                controller.driverGenderPreference.value = value;
              }
            },
          ),
          SRideSwitchTile(
            label: 'Dog or pet allowed',
            value: controller.isPetAllowed.value,
            onChanged: (value) => controller.isPetAllowed.value = value,
          ),
          SRideSwitchTile(
            label: 'Smoking allowed',
            value: controller.isSmokingAllowed.value,
            onChanged: (value) => controller.isSmokingAllowed.value = value,
          ),
          SRideSwitchTile(
            label: 'Wheelchair access required',
            value: controller.requiresWheelchairAccess.value,
            onChanged: (value) =>
                controller.requiresWheelchairAccess.value = value,
          ),
          SRideSwitchTile(
            label: 'Pickup verification code',
            value: controller.requiresOtpStart.value,
            onChanged: (value) => controller.requiresOtpStart.value = value,
          ),
          SRideSwitchTile(
            label: 'Completion verification code',
            value: controller.requiresOtpEnd.value,
            onChanged: (value) => controller.requiresOtpEnd.value = value,
          ),
        ],
      ),
    );
  }
}
