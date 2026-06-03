import 'package:client/common/navigation/right_slide_page_route.dart';
import 'package:client/common/widgets/appbar/appbar.dart';
import 'package:client/features/personalization/screens/driver_registration/controllers/vehicle_selection_controller.dart';
import 'package:client/features/personalization/screens/driver_registration/models/driver_registration_models.dart';
import 'package:client/features/personalization/screens/driver_registration/screens/verification_status/verification_status_screen.dart';
import 'package:client/features/personalization/screens/driver_registration/widgets/driver_registration_option_tile.dart';
import 'package:client/utils/constants/colors.dart';
import 'package:client/utils/constants/sizes.dart';
import 'package:client/utils/constants/texts.dart';
import 'package:flutter/material.dart';
import 'package:get/get.dart';

class DriverVehicleSelectionScreen extends StatefulWidget {
  const DriverVehicleSelectionScreen({
    super.key,
    required this.category,
  });

  final SDriverWorkCategory category;

  @override
  State<DriverVehicleSelectionScreen> createState() =>
      _DriverVehicleSelectionScreenState();
}

class _DriverVehicleSelectionScreenState
    extends State<DriverVehicleSelectionScreen> {
  late final SDriverVehicleSelectionController controller;

  @override
  void initState() {
    super.initState();
    controller = SDriverVehicleSelectionController(
      serviceType: SVerificationServiceType.fromWorkCategory(
        widget.category.type,
      ),
    )..loadSummary();
  }

  @override
  void dispose() {
    controller.dispose();
    super.dispose();
  }

  Future<void> _openVerificationStatus(
    BuildContext context,
    SDriverVehicleOption vehicle,
  ) async {
    final item = controller.itemFor(vehicle);
    final shouldConfirmReuse = item != null &&
        item.vehicleId != null &&
        !item.isRegisteredForService;

    if (shouldConfirmReuse) {
      final confirmed = await _confirmVehicleReuse(context, vehicle, item);
      if (confirmed != true) return;

      try {
        await controller.attachExistingVehicleIfNeeded(vehicle);
      } catch (_) {
        return;
      }
    }

    if (!context.mounted) return;
    Navigator.of(context).push(
      SRightSlidePageRoute(
        page: DriverVerificationStatusScreen(
          category: widget.category,
          vehicle: vehicle,
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final vehicles = SDriverRegistrationCatalog.vehiclesFor(
      widget.category.type,
    );
    final textTheme = Theme.of(context).textTheme;

    return Scaffold(
      backgroundColor: SColors.primaryBackground,
      appBar: SAppBar(
        showBackArrow: true,
        title: Text(
          STexts.driverVehicleSelectionTitle,
          style: textTheme.headlineSmall?.copyWith(
            color: SColors.textPrimary,
            fontWeight: FontWeight.w800,
          ),
        ),
      ),
      body: SafeArea(
        child: Obx(() {
          if (controller.isLoading.value) {
            return const Center(
              child: CircularProgressIndicator(color: SColors.primary),
            );
          }

          final error = controller.errorMessage.value;
          if (error != null) {
            return ListView(
              padding: const EdgeInsets.all(SSizes.defaultSpace),
              children: [
                Text(
                  error,
                  style: textTheme.bodyMedium?.copyWith(
                    color: SColors.error,
                  ),
                ),
                const SizedBox(height: SSizes.md),
                FilledButton(
                  onPressed: controller.loadSummary,
                  child: const Text('Retry'),
                ),
              ],
            );
          }

          return ListView.separated(
            padding: const EdgeInsets.all(SSizes.defaultSpace),
            itemCount: vehicles.length,
            separatorBuilder: (context, index) =>
                const SizedBox(height: SSizes.lg),
            itemBuilder: (context, index) {
              final vehicle = vehicles[index];
              return SDriverRegistrationOptionTile(
                title: vehicle.title,
                image: vehicle.image,
                compact: true,
                isCompleted:
                    controller.isRegisteredForSelectedService(vehicle),
                onTap: () => _openVerificationStatus(context, vehicle),
              );
            },
          );
        }),
      ),
    );
  }

  Future<bool?> _confirmVehicleReuse(
    BuildContext context,
    SDriverVehicleOption vehicle,
    SDriverVehicleSummaryItem item,
  ) {
    final textTheme = Theme.of(context).textTheme;
    final vehicleLabel = _vehicleLabel(vehicle, item);
    final message = STexts.driverVehicleReuseDialogMessage
        .replaceFirst('{vehicle}', vehicleLabel)
        .replaceFirst('{service}', widget.category.title);

    return showDialog<bool>(
      context: context,
      builder: (context) {
        return AlertDialog(
          backgroundColor: SColors.surfaceContainer,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(SSizes.cardRadiusLg),
          ),
          title: Text(
            STexts.driverVehicleReuseDialogTitle,
            style: textTheme.titleLarge?.copyWith(
              color: SColors.textPrimary,
              fontWeight: FontWeight.w800,
            ),
          ),
          content: Text(
            message,
            style: textTheme.bodyMedium?.copyWith(
              color: SColors.textSecondary,
              height: 1.35,
            ),
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.of(context).pop(false),
              child: const Text(STexts.driverVehicleReuseCancel),
            ),
            FilledButton(
              onPressed: () => Navigator.of(context).pop(true),
              child: const Text(STexts.driverVehicleReuseConfirm),
            ),
          ],
        );
      },
    );
  }

  String _vehicleLabel(
    SDriverVehicleOption vehicle,
    SDriverVehicleSummaryItem item,
  ) {
    final nameParts = [
      item.brand,
      item.model,
    ].whereType<String>().where((value) => value.trim().isNotEmpty).toList();

    final name = nameParts.isEmpty ? vehicle.title : nameParts.join(' ');
    final plateNumber = item.plateNumber?.trim();
    if (plateNumber == null || plateNumber.isEmpty) return name;

    return '$name ($plateNumber)';
  }
}
