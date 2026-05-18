import 'package:client/common/widgets/appbar/appbar.dart';
import 'package:client/features/personalization/screens/driver_registration/controllers/vehicle_info_registration_controller.dart';
import 'package:client/features/personalization/screens/driver_registration/models/driver_registration_models.dart';
import 'package:client/features/personalization/screens/driver_registration/screens/vechicle_info/widgets/vehicle_header.dart';
import 'package:client/features/personalization/screens/driver_registration/screens/vechicle_info/widgets/vehicle_uploads.dart';
import 'package:client/features/personalization/screens/driver_registration/widgets/driver_registration_error_text.dart';
import 'package:client/utils/constants/colors.dart';
import 'package:client/utils/constants/sizes.dart';
import 'package:client/utils/constants/texts.dart';
import 'package:client/utils/validators/validator.dart';
import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'package:iconsax/iconsax.dart';

class VehicleInfoScreen extends StatefulWidget {
  const VehicleInfoScreen({
    super.key,
    required this.category,
    required this.vehicle,
  });

  final SDriverWorkCategory category;
  final SDriverVehicleOption vehicle;

  @override
  State<VehicleInfoScreen> createState() => _VehicleInfoScreenState();
}

class _VehicleInfoScreenState extends State<VehicleInfoScreen> {
  late final SVehicleInfoRegistrationController controller;

  @override
  void initState() {
    super.initState();
    controller = SVehicleInfoRegistrationController(vehicle: widget.vehicle);
  }

  @override
  void dispose() {
    controller.dispose();
    super.dispose();
  }

  Future<void> _submit() async {
    final submitted = await controller.submit();
    if (!mounted) return;
    if (submitted) Navigator.of(context).pop(true);
  }

  @override
  Widget build(BuildContext context) {
    final textTheme = Theme.of(context).textTheme;

    return Scaffold(
      backgroundColor: SColors.primaryBackground,
      appBar: SAppBar(
        showBackArrow: true,
        title: Text(
          STexts.driverRegistrationVehicleInfoTitle,
          style: textTheme.headlineSmall?.copyWith(
            color: SColors.textPrimary,
            fontWeight: FontWeight.w800,
          ),
        ),
      ),
      bottomNavigationBar: SafeArea(
        minimum: const EdgeInsets.all(SSizes.defaultSpace),
        child: Obx(
          () => ElevatedButton(
            onPressed: controller.isSubmitting.value ? null : _submit,
            child: Text(
              controller.isSubmitting.value
                  ? STexts.driverRegistrationStepSaving
                  : STexts.driverRegistrationStepSave,
            ),
          ),
        ),
      ),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(SSizes.defaultSpace),
          child: Center(
            child: ConstrainedBox(
              constraints: const BoxConstraints(maxWidth: 520),
              child: Form(
                key: controller.formKey,
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    SVehicleHeader(
                      category: widget.category,
                      vehicle: widget.vehicle,
                    ),
                    const SizedBox(height: SSizes.lg),
                    TextFormField(
                      controller: controller.brandController,
                      decoration: const InputDecoration(
                        labelText: STexts.driverRegistrationBrand,
                        prefixIcon: Icon(Iconsax.car),
                      ),
                      validator: (value) => SValidator.validateMaxLength(
                        value,
                        50,
                        fieldName: STexts.driverRegistrationBrand,
                      ),
                    ),
                    const SizedBox(height: SSizes.spaceBtwInputFields),
                    TextFormField(
                      controller: controller.modelController,
                      decoration: const InputDecoration(
                        labelText: STexts.driverRegistrationModel,
                        prefixIcon: Icon(Iconsax.car),
                      ),
                      validator: (value) => SValidator.validateMaxLength(
                        value,
                        50,
                        fieldName: STexts.driverRegistrationModel,
                      ),
                    ),
                    const SizedBox(height: SSizes.spaceBtwInputFields),
                    TextFormField(
                      controller: controller.colorController,
                      decoration: const InputDecoration(
                        labelText: STexts.driverRegistrationColor,
                        prefixIcon: Icon(Iconsax.colorfilter),
                      ),
                      validator: (value) => SValidator.validateMaxLength(
                        value,
                        30,
                        fieldName: STexts.driverRegistrationColor,
                      ),
                    ),
                    const SizedBox(height: SSizes.spaceBtwInputFields),
                    Obx(
                      () => DropdownButtonFormField<SVerificationVehicleType>(
                        initialValue: controller.selectedVehicleType.value,
                        decoration: const InputDecoration(
                          labelText: STexts.driverRegistrationVehicleType,
                          prefixIcon: Icon(Iconsax.category),
                        ),
                        items: SVerificationVehicleType.values
                            .map(
                              (type) => DropdownMenuItem(
                                value: type,
                                child: Text(type.label),
                              ),
                            )
                            .toList(),
                        onChanged: (value) {
                          if (value != null) {
                            controller.selectedVehicleType.value = value;
                          }
                        },
                      ),
                    ),
                    const SizedBox(height: SSizes.spaceBtwInputFields),
                    TextFormField(
                      controller: controller.passengersController,
                      keyboardType: TextInputType.number,
                      decoration: const InputDecoration(
                        labelText: STexts.driverRegistrationMaxPassengers,
                        prefixIcon: Icon(Iconsax.profile_2user),
                      ),
                      validator: (value) => SValidator.validateIntegerRange(
                        value,
                        fieldName: STexts.driverRegistrationMaxPassengers,
                        min: 1,
                        max: 10,
                      ),
                    ),
                    const SizedBox(height: SSizes.spaceBtwInputFields),
                    TextFormField(
                      controller: controller.plateNumberController,
                      decoration: const InputDecoration(
                        labelText: STexts.driverRegistrationPlateNumber,
                        prefixIcon: Icon(Iconsax.card),
                      ),
                      validator: (value) => SValidator.validateMaxLength(
                        value,
                        20,
                        fieldName: STexts.driverRegistrationPlateNumber,
                      ),
                    ),
                    const SizedBox(height: SSizes.spaceBtwInputFields),
                    TextFormField(
                      controller: controller.productionYearController,
                      keyboardType: TextInputType.number,
                      decoration: const InputDecoration(
                        labelText: STexts.driverRegistrationProductionYear,
                        prefixIcon: Icon(Iconsax.calendar),
                      ),
                      validator: (value) => SValidator.validateIntegerRange(
                        value,
                        fieldName: STexts.driverRegistrationProductionYear,
                        min: 1980,
                        max: 2100,
                      ),
                    ),
                    const SizedBox(height: SSizes.lg),
                    SVehicleUploads(controller: controller),
                    Obx(
                      () => SDriverRegistrationErrorText(
                        message: controller.errorMessage.value,
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ),
        ),
      ),
    );
  }
}
