import 'package:client/common/widgets/uploads/image_upload_tile.dart';
import 'package:client/features/personalization/screens/driver_registration/controllers/vehicle_info_registration_controller.dart';
import 'package:client/utils/constants/sizes.dart';
import 'package:client/utils/constants/texts.dart';
import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'package:image_picker/image_picker.dart';

class SVehicleUploads extends StatelessWidget {
  const SVehicleUploads({
    super.key,
    required this.controller,
  });

  final SVehicleInfoRegistrationController controller;

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        Obx(
          () => SImageUploadTile(
            title: STexts.driverRegistrationRegistrationFront,
            subtitle: STexts.driverRegistrationRegistrationFrontHelp,
            imagePath: controller.registrationFrontImage.value?.path,
            onTakePhoto: () =>
                controller.pickRegistrationFront(ImageSource.camera),
            onPickImage: () =>
                controller.pickRegistrationFront(ImageSource.gallery),
            onRemove: controller.removeRegistrationFront,
          ),
        ),
        const SizedBox(height: SSizes.md),
        Obx(
          () => SImageUploadTile(
            title: STexts.driverRegistrationRegistrationBack,
            subtitle: STexts.driverRegistrationRegistrationBackHelp,
            imagePath: controller.registrationBackImage.value?.path,
            onTakePhoto: () =>
                controller.pickRegistrationBack(ImageSource.camera),
            onPickImage: () =>
                controller.pickRegistrationBack(ImageSource.gallery),
            onRemove: controller.removeRegistrationBack,
          ),
        ),
        const SizedBox(height: SSizes.md),
        Obx(
          () => SImageUploadTile(
            title: STexts.driverRegistrationVehiclePhotoFront,
            subtitle: STexts.driverRegistrationVehicleFrontHelp,
            imagePath: controller.vehicleFrontImage.value?.path,
            onTakePhoto: () => controller.pickVehicleFront(ImageSource.camera),
            onPickImage: () => controller.pickVehicleFront(ImageSource.gallery),
            onRemove: controller.removeVehicleFront,
          ),
        ),
        const SizedBox(height: SSizes.md),
        Obx(
          () => SImageUploadTile(
            title: STexts.driverRegistrationVehiclePhotoBack,
            subtitle: STexts.driverRegistrationVehicleBackHelp,
            imagePath: controller.vehicleBackImage.value?.path,
            onTakePhoto: () => controller.pickVehicleBack(ImageSource.camera),
            onPickImage: () => controller.pickVehicleBack(ImageSource.gallery),
            onRemove: controller.removeVehicleBack,
          ),
        ),
      ],
    );
  }
}
