import 'package:client/common/widgets/appbar/appbar.dart';
import 'package:client/common/widgets/uploads/image_upload_tile.dart';
import 'package:client/features/personalization/screens/driver_registration/controllers/driver_license_registration_controller.dart';
import 'package:client/features/personalization/screens/driver_registration/models/driver_registration_models.dart';
import 'package:client/features/personalization/screens/driver_registration/widgets/driver_registration_date_field.dart';
import 'package:client/features/personalization/screens/driver_registration/widgets/driver_registration_error_text.dart';
import 'package:client/features/personalization/screens/driver_registration/widgets/driver_registration_step_header.dart';
import 'package:client/utils/constants/colors.dart';
import 'package:client/utils/constants/sizes.dart';
import 'package:client/utils/constants/texts.dart';
import 'package:client/utils/validators/validator.dart';
import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'package:iconsax/iconsax.dart';
import 'package:image_picker/image_picker.dart';

class DriverLicenseScreen extends StatefulWidget {
  const DriverLicenseScreen({
    super.key,
    required this.category,
    required this.vehicle,
  });

  final SDriverWorkCategory category;
  final SDriverVehicleOption vehicle;

  @override
  State<DriverLicenseScreen> createState() => _DriverLicenseScreenState();
}

class _DriverLicenseScreenState extends State<DriverLicenseScreen> {
  late final SDriverLicenseRegistrationController controller;

  @override
  void initState() {
    super.initState();
    controller = SDriverLicenseRegistrationController();
  }

  @override
  void dispose() {
    controller.dispose();
    super.dispose();
  }

  Future<void> _selectExpiryDate() async {
    final now = DateTime.now();
    final picked = await showDatePicker(
      context: context,
      firstDate: now,
      lastDate: DateTime(now.year + 25),
      initialDate: DateTime(now.year + 5),
    );
    if (picked != null) controller.expiryDate.value = picked;
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
          STexts.driverRegistrationLicenseTitle,
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
                    SDriverRegistrationStepHeader(
                      title: STexts.driverRegistrationLicenseTitle,
                      subtitle:
                          '${widget.category.title} - ${widget.vehicle.title}',
                    ),
                    const SizedBox(height: SSizes.lg),
                    TextFormField(
                      controller: controller.licenseNumberController,
                      decoration: const InputDecoration(
                        labelText: STexts.driverRegistrationLicenseNumber,
                        prefixIcon: Icon(Iconsax.card),
                      ),
                      validator: SValidator.validateLicenseNumber,
                    ),
                    const SizedBox(height: SSizes.spaceBtwInputFields),
                    Obx(
                      () => SDriverRegistrationDateField(
                        label: STexts.driverRegistrationExpiryDate,
                        value: controller.expiryDate.value,
                        error: controller.expiryError,
                        onTap: _selectExpiryDate,
                      ),
                    ),
                    const SizedBox(height: SSizes.lg),
                    Obx(
                      () => SImageUploadTile(
                        title: STexts.driverRegistrationLicenseFront,
                        subtitle: STexts.driverRegistrationFrontSideHelp,
                        imagePath: controller.frontImage.value?.path,
                        onTakePhoto: () =>
                            controller.pickFront(ImageSource.camera),
                        onPickImage: () =>
                            controller.pickFront(ImageSource.gallery),
                        onRemove: controller.removeFront,
                      ),
                    ),
                    const SizedBox(height: SSizes.md),
                    Obx(
                      () => SImageUploadTile(
                        title: STexts.driverRegistrationLicenseBack,
                        subtitle: STexts.driverRegistrationBackSideHelp,
                        imagePath: controller.backImage.value?.path,
                        onTakePhoto: () =>
                            controller.pickBack(ImageSource.camera),
                        onPickImage: () =>
                            controller.pickBack(ImageSource.gallery),
                        onRemove: controller.removeBack,
                      ),
                    ),
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
