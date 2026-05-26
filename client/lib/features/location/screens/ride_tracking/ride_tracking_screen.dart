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
                  ),
                  child: Padding(
                    padding: const EdgeInsets.all(SSizes.lg),
                    child: Text(
                      controller.statusMessage.value,
                      style: Theme.of(context).textTheme.titleMedium?.copyWith(
                            color: SColors.textPrimary,
                            fontWeight: FontWeight.w700,
                          ),
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
}
