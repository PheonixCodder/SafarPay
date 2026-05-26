import 'package:flutter/material.dart';
import 'package:get/get.dart';

import '../../../../../common/widgets/maps/map_models.dart';
import '../../../../../common/widgets/maps/map_view.dart';
import '../../../../communication/widgets/ride_communication_button.dart';
import '../../../../../utils/constants/colors.dart';
import '../../../../../utils/constants/sizes.dart';
import '../../../controllers/driver_requests_controller.dart';
import '../../../domain/driver_request_models.dart';
import 'active_ride_panel.dart';

class SActiveRideView extends StatelessWidget {
  const SActiveRideView({
    super.key,
    required this.controller,
    required this.ride,
  });

  final SDriverRequestsController controller;
  final SDriverActiveRide ride;

  @override
  Widget build(BuildContext context) {
    final pickup = ride.pickup;
    final dropoff = ride.dropoff;

    return Stack(
      children: [
        Positioned.fill(
          child: Obx(
            () => SMapView(
              initialCenter: controller.mapCenter,
              cameraMode: SMapCameraMode.navigationFollow,
              zoom: 17.35,
              fitPadding: const EdgeInsets.fromLTRB(48, 112, 48, 260),
              fullBleed: true,
              showStatusPill: false,
              showUserLocation: false,
              markers: [
                if (controller.currentLocation.value != null)
                  SMapMarker(
                    id: 'driver',
                    coordinate: controller.currentLocation.value!,
                    type: SMapMarkerType.driver,
                    label: 'Driver',
                  ),
                if (pickup != null)
                  SMapMarker(
                    id: pickup.id,
                    coordinate: pickup.coordinate,
                    type: SMapMarkerType.pickup,
                    label: 'Pickup',
                  ),
                if (dropoff != null)
                  SMapMarker(
                    id: dropoff.id,
                    coordinate: dropoff.coordinate,
                    type: SMapMarkerType.dropoff,
                    label: 'Dropoff',
                  ),
              ],
              route: ride.isInProgress ? ride.tripRoute : ride.driverToPickup,
            ),
          ),
        ),
        Positioned(
          left: SSizes.md,
          right: SSizes.md,
          top: SSizes.md,
          child: DecoratedBox(
            decoration: BoxDecoration(
              color: SColors.primary,
              borderRadius: BorderRadius.circular(SSizes.cardRadiusMd),
            ),
            child: Padding(
              padding: const EdgeInsets.all(SSizes.md),
              child: Text(
                ride.isInProgress
                    ? 'Head to dropoff'
                    : ride.hasArrivedAtPickup
                        ? 'Ready to start trip'
                        : 'Head to pickup',
                style: Theme.of(context).textTheme.titleMedium?.copyWith(
                      color: SColors.white,
                      fontWeight: FontWeight.w900,
                    ),
              ),
            ),
          ),
        ),
        Positioned(
          left: SSizes.md,
          right: SSizes.md,
          bottom: SSizes.md,
          child: SActiveRidePanel(
            controller: controller,
            ride: ride,
          ),
        ),
        if (!ride.isInProgress)
          Positioned(
            right: SSizes.md,
            bottom: 226,
            child: SRideCommunicationButton(rideId: ride.id),
          ),
      ],
    );
  }
}
