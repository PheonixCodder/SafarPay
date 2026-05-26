import 'package:client/common/widgets/appbar/appbar.dart';
import 'package:client/common/widgets/maps/map_models.dart';
import 'package:client/common/widgets/maps/map_view.dart';
import 'package:client/features/location/controllers/ride_preview_controller.dart';
import 'package:client/features/location/domain/location_models.dart';
import 'package:client/features/location/screens/ride_preview/widgets/route_summary.dart';
import 'package:client/features/location/screens/ride_tracking/ride_tracking_screen.dart';
import 'package:client/utils/constants/colors.dart';
import 'package:client/utils/constants/sizes.dart';
import 'package:client/utils/constants/texts.dart';
import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'package:iconsax/iconsax.dart';

class RidePreviewScreen extends StatelessWidget {
  const RidePreviewScreen({
    super.key,
    required this.pickup,
    required this.dropoff,
  });

  final SAddressResult pickup;
  final SAddressResult dropoff;

  @override
  Widget build(BuildContext context) {
    final controller = Get.put(
      SRidePreviewController(pickup: pickup, dropoff: dropoff),
    );

    return Scaffold(
      backgroundColor: SColors.primaryBackground,
      appBar: SAppBar(
        showBackArrow: true,
        title: Text(
          STexts.ridePreviewTitle,
          style: Theme.of(context).textTheme.titleLarge,
        ),
      ),
      body: SafeArea(
        child: Obx(
          () => ListView(
            padding: const EdgeInsets.all(SSizes.defaultSpace),
            children: [
              SizedBox(
                height: SSizes.rideMapPreviewHeight,
                child: SMapView(
                  initialCenter: pickup.coordinate,
                  cameraMode: SMapCameraMode.fitRoute,
                  fitPadding: const EdgeInsets.fromLTRB(48, 64, 48, 64),
                  isLoading: controller.isLoading.value,
                  errorMessage: controller.errorMessage.value.isEmpty
                      ? null
                      : controller.errorMessage.value,
                  route: controller.route.value,
                  showUserLocation: false,
                  markers: [
                    SMapMarker(
                      id: 'pickup',
                      coordinate: pickup.coordinate,
                      type: SMapMarkerType.pickup,
                      label: STexts.tripsPickup,
                    ),
                    SMapMarker(
                      id: 'dropoff',
                      coordinate: dropoff.coordinate,
                      type: SMapMarkerType.dropoff,
                      label: STexts.tripsDropoff,
                    ),
                  ],
                ),
              ),
              const SizedBox(height: SSizes.lg),
              SRouteSummary(
                pickup: pickup,
                dropoff: dropoff,
                route: controller.route.value,
                errorMessage: controller.errorMessage.value,
              ),
              const SizedBox(height: SSizes.lg),
              ElevatedButton.icon(
                onPressed: controller.pickupValid.value
                    ? () async {
                        final rideId = await controller.createRide();
                        if (rideId == null) return;
                        Get.to(() => RideTrackingScreen(rideId: rideId));
                      }
                    : null,
                icon: const Icon(Iconsax.car),
                label: Text(
                  controller.isCreatingRide.value
                      ? STexts.ridePreviewRequesting
                      : STexts.ridePreviewConfirm,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
