import 'package:client/common/widgets/appbar/appbar.dart';
import 'package:client/common/widgets/maps/map_models.dart';
import 'package:client/common/widgets/maps/map_view.dart';
import 'package:client/features/communication/widgets/ride_communication_button.dart';
import 'package:client/features/location/controllers/ride_tracking_controller.dart';
import 'package:client/features/location/domain/location_models.dart';
import 'package:client/utils/constants/colors.dart';
import 'package:client/utils/constants/sizes.dart';
import 'package:client/utils/constants/texts.dart';
import 'package:flutter/material.dart';
import 'package:get/get.dart';

import 'package:iconsax/iconsax.dart';

import 'ride_destination_edit_screen.dart';
import 'widgets/ride_verification_code_card.dart';

class RideTrackingScreen extends StatelessWidget {
  const RideTrackingScreen({
    super.key,
    required this.rideId,
  });

  final String rideId;

  @override
  Widget build(BuildContext context) {
    final controller = Get.put(
      SRideTrackingController(rideId: rideId),
      tag: rideId,
    );

    return Scaffold(
      backgroundColor: SColors.primaryBackground,
      appBar: SAppBar(
        showBackArrow: true,
        title: Text(
          STexts.rideTrackingTitle,
          style: Theme.of(context).textTheme.titleLarge,
        ),
      ),
      body: SafeArea(
        child: Obx(
          () {
            final center = controller.driverLocation.value?.coordinate ??
                controller.passengerLocation.value?.coordinate ??
                const SCoordinate(latitude: 31.5204, longitude: 74.3587);

            return ListView(
              padding: const EdgeInsets.all(SSizes.defaultSpace),
              children: [
                SizedBox(
                  height: SSizes.rideMapTrackingHeight,
                  child: Stack(
                    children: [
                      Positioned.fill(
                        child: SMapView(
                          initialCenter: center,
                          cameraMode: SMapCameraMode.fitRoute,
                          fitPadding: const EdgeInsets.fromLTRB(56, 72, 56, 96),
                          maxFitZoom: 16,
                          isLoading: controller.isConnecting.value,
                          markers: controller.markers,
                          route: controller.route.value,
                          showUserLocation: false,
                        ),
                      ),
                      if (controller.rideStatus.value != 'IN_PROGRESS')
                        Positioned(
                          right: SSizes.md,
                          bottom: SSizes.md,
                          child: SRideCommunicationButton(rideId: rideId),
                        ),
                    ],
                  ),
                ),
                const SizedBox(height: SSizes.lg),
                if (controller.startVerificationCode.value.isNotEmpty &&
                    controller.rideStatus.value != 'IN_PROGRESS') ...[
                  SRideVerificationCodeCard(
                    title: 'Pickup code',
                    code: controller.startVerificationCode.value,
                  ),
                  const SizedBox(height: SSizes.lg),
                ],
                if (controller.endVerificationCode.value.isNotEmpty &&
                    controller.rideStatus.value == 'IN_PROGRESS') ...[
                  SRideVerificationCodeCard(
                    title: 'Completion code',
                    code: controller.endVerificationCode.value,
                  ),
                  const SizedBox(height: SSizes.lg),
                ],
                DecoratedBox(
                  decoration: BoxDecoration(
                    color: SColors.white,
                    borderRadius: BorderRadius.circular(SSizes.rideSheetRadius),
                    boxShadow: [
                      BoxShadow(
                        color: SColors.borderPrimary,
                        blurRadius: 8,
                        spreadRadius: 1,
                      ),
                    ],
                  ),
                  child: Padding(
                    padding: const EdgeInsets.all(SSizes.lg),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          controller.statusMessage.value,
                          style: Theme.of(context).textTheme.titleMedium?.copyWith(
                                color: SColors.textPrimary,
                                fontWeight: FontWeight.w800,
                              ),
                        ),
                        const Divider(height: SSizes.spaceBtwSections),
                        Row(
                          children: [
                            const Icon(Iconsax.flag, color: SColors.primary),
                            const SizedBox(width: SSizes.md),
                            Expanded(
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  Text(
                                    'Destination',
                                    style: Theme.of(context).textTheme.bodySmall?.copyWith(
                                          color: SColors.textSecondary,
                                        ),
                                  ),
                                  Text(
                                    controller.dropoffStop.value?.placeName ??
                                        controller.dropoffStop.value?.addressLine1 ??
                                        'Loading destination...',
                                    style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                                          color: SColors.textPrimary,
                                          fontWeight: FontWeight.w600,
                                        ),
                                    maxLines: 1,
                                    overflow: TextOverflow.ellipsis,
                                  ),
                                ],
                              ),
                            ),
                            if (controller.rideStatus.value != 'COMPLETED' &&
                                controller.rideStatus.value != 'CANCELLED')
                              IconButton(
                                icon: const Icon(Iconsax.edit, color: SColors.primary, size: 20),
                                onPressed: () => Get.to(
                                  () => RideDestinationEditScreen(
                                    trackingController: controller,
                                  ),
                                ),
                              ),
                          ],
                        ),
                        if (controller.rideStatus.value != 'COMPLETED' &&
                            controller.rideStatus.value != 'CANCELLED') ...[
                          const SizedBox(height: SSizes.lg),
                          SizedBox(
                            width: double.infinity,
                            child: OutlinedButton(
                              onPressed: () => _showCancelConfirmation(context, controller),
                              style: OutlinedButton.styleFrom(
                                side: const BorderSide(color: SColors.error),
                                foregroundColor: SColors.error,
                              ),
                              child: const Text('Cancel Ride'),
                            ),
                          ),
                        ],
                      ],
                    ),
                  ),
                ),
              ],
            );
          },
        ),
      ),
    );
  }

  void _showCancelConfirmation(BuildContext context, SRideTrackingController controller) {
    Get.dialog(
      AlertDialog(
        title: const Text('Cancel Ride'),
        content: const Text('Are you sure you want to cancel your ride?'),
        actions: [
          TextButton(
            onPressed: () => Get.back(),
            child: const Text('No, keep'),
          ),
          ElevatedButton(
            onPressed: () {
              Get.back();
              controller.cancelCurrentRide('Passenger requested cancellation');
            },
            style: ElevatedButton.styleFrom(
              backgroundColor: SColors.error,
              foregroundColor: SColors.white,
            ),
            child: const Text('Yes, Cancel'),
          ),
        ],
      ),
    );
  }
}
