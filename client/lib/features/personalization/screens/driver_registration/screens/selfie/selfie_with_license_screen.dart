import 'package:client/common/widgets/appbar/appbar.dart';
import 'package:client/features/personalization/screens/driver_registration/controllers/selfie_with_license_controller.dart';
import 'package:client/features/personalization/screens/driver_registration/models/driver_registration_models.dart';
import 'package:client/features/personalization/screens/driver_registration/screens/selfie/widgets/selfie_camera_surface.dart';
import 'package:client/features/personalization/screens/driver_registration/screens/selfie/widgets/selfie_header.dart';
import 'package:client/features/personalization/screens/driver_registration/widgets/driver_registration_error_text.dart';
import 'package:client/utils/constants/colors.dart';
import 'package:client/utils/constants/sizes.dart';
import 'package:client/utils/constants/texts.dart';
import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'package:iconsax/iconsax.dart';

class SelfieWithLicenseScreen extends StatefulWidget {
  const SelfieWithLicenseScreen({
    super.key,
    required this.category,
    required this.vehicle,
  });

  final SDriverWorkCategory category;
  final SDriverVehicleOption vehicle;

  @override
  State<SelfieWithLicenseScreen> createState() =>
      _SelfieWithLicenseScreenState();
}

class _SelfieWithLicenseScreenState extends State<SelfieWithLicenseScreen> {
  late final SSelfieWithLicenseController controller;

  @override
  void initState() {
    super.initState();
    controller = Get.put(SSelfieWithLicenseController());
    controller.initializeCamera();
  }

  @override
  void dispose() {
    Get.delete<SSelfieWithLicenseController>();
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
          STexts.driverRegistrationSelfieTitle,
          style: textTheme.headlineSmall?.copyWith(
            color: SColors.textPrimary,
            fontWeight: FontWeight.w800,
          ),
        ),
      ),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(SSizes.defaultSpace),
          child: Center(
            child: ConstrainedBox(
              constraints: const BoxConstraints(maxWidth: 520),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  SSelfieHeader(
                    subtitle:
                        '${widget.category.title} - ${widget.vehicle.title}',
                  ),
                  const SizedBox(height: SSizes.lg),
                  Obx(() {
                    final capturedImage = controller.capturedImage.value;
                    final isInitializingCamera =
                        controller.isInitializingCamera.value;

                    return SSelfieCameraSurface(
                      capturedImage: capturedImage,
                      isInitializingCamera: isInitializingCamera,
                      cameraController: controller.cameraController,
                    );
                  }),
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
      bottomNavigationBar: SafeArea(
        minimum: const EdgeInsets.all(SSizes.defaultSpace),
        child: Obx(() {
          final isSubmitting = controller.isSubmitting.value;
          final capturedImage = controller.capturedImage.value;

          return Row(
            children: [
              if (capturedImage != null) ...[
                Expanded(
                  child: OutlinedButton(
                    onPressed: isSubmitting ? null : controller.retry,
                    child: const Text(STexts.driverRegistrationSelfieRetry),
                  ),
                ),
                const SizedBox(width: SSizes.md),
              ],
              Expanded(
                flex: 2,
                child: ElevatedButton.icon(
                  onPressed: isSubmitting
                      ? null
                      : capturedImage == null
                          ? controller.capture
                          : _submit,
                  icon: Icon(
                    capturedImage == null ? Iconsax.camera : Iconsax.tick_circle,
                    size: SSizes.iconSm,
                  ),
                  label: Text(
                    isSubmitting
                        ? STexts.driverRegistrationStepSaving
                        : capturedImage == null
                            ? STexts.driverRegistrationSelfieCaptureAction
                            : STexts.driverRegistrationSelfieUse,
                  ),
                ),
              ),
            ],
          );
        }),
      ),
    );
  }
}
