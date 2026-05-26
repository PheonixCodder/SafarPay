import 'package:flutter/material.dart';
import 'package:get/get.dart';

import '../../../../../common/widgets/maps/map_models.dart';
import '../../../../../common/widgets/maps/map_view.dart';
import '../../../../../utils/constants/colors.dart';
import '../../../../../utils/constants/sizes.dart';
import '../../../controllers/driver_requests_controller.dart';

class SIncomingRequestSheet extends StatelessWidget {
  const SIncomingRequestSheet({super.key, required this.controller});

  final SDriverRequestsController controller;

  @override
  Widget build(BuildContext context) {
    final request = controller.incomingRequest.value;
    if (request == null) return const SizedBox.shrink();
    final pickup = request.pickup;
    final dropoff = request.dropoff;
    final textTheme = Theme.of(context).textTheme;

    return Positioned(
      left: SSizes.md,
      right: SSizes.md,
      bottom: SSizes.md,
      child: Material(
        color: SColors.white,
        borderRadius: BorderRadius.circular(SSizes.cardRadiusLg),
        elevation: 12,
        child: Padding(
          padding: const EdgeInsets.all(SSizes.md),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Expanded(
                    child: Text(
                      request.isHybrid ? 'Send your offer' : 'New ride request',
                      style: textTheme.titleLarge?.copyWith(
                        fontWeight: FontWeight.w900,
                      ),
                    ),
                  ),
                  IconButton(
                    onPressed: controller.dismissIncoming,
                    icon: const Icon(Icons.close),
                  ),
                ],
              ),
              if (pickup != null && dropoff != null)
                SizedBox(
                  height: 150,
                  child: SMapView(
                    initialCenter: pickup.coordinate,
                    cameraMode: SMapCameraMode.fitRoute,
                    fitPadding: const EdgeInsets.all(28),
                    maxFitZoom: 15,
                    markers: [
                      SMapMarker(
                        id: pickup.id,
                        coordinate: pickup.coordinate,
                        type: SMapMarkerType.pickup,
                        label: 'Pickup',
                      ),
                      SMapMarker(
                        id: dropoff.id,
                        coordinate: dropoff.coordinate,
                        type: SMapMarkerType.dropoff,
                        label: 'Dropoff',
                      ),
                    ],
                    route: request.tripRoute,
                    showRecenterButton: false,
                    showStatusPill: false,
                    showUserLocation: false,
                  ),
                ),
              const SizedBox(height: SSizes.md),
              Text(pickup?.displayName ?? 'Pickup unavailable'),
              const SizedBox(height: SSizes.xs),
              Text(
                dropoff?.displayName ?? 'Dropoff unavailable',
                style: textTheme.bodyMedium?.copyWith(
                  color: SColors.textSecondary,
                ),
              ),
              const SizedBox(height: SSizes.md),
              Row(
                children: [
                  Expanded(
                    child: Text(
                      'PKR ${request.displayFare.round()}',
                      style: textTheme.headlineSmall?.copyWith(
                        fontWeight: FontWeight.w900,
                      ),
                    ),
                  ),
                  Text(
                    '${request.tripRoute?.distanceKm.toStringAsFixed(1) ?? '--'} km',
                    style: textTheme.labelLarge,
                  ),
                  const SizedBox(width: SSizes.md),
                  Text(
                    '${request.tripRoute?.durationMinutes.round() ?? '--'} min',
                    style: textTheme.labelLarge,
                  ),
                ],
              ),
              if (request.isHybrid) ...[
                const SizedBox(height: SSizes.md),
                Obx(
                  () => DecoratedBox(
                    decoration: BoxDecoration(
                      border: Border.all(color: SColors.borderSecondary),
                      borderRadius: BorderRadius.circular(SSizes.cardRadiusSm),
                    ),
                    child: Padding(
                      padding: const EdgeInsets.all(SSizes.md),
                      child: Row(
                        children: [
                          Expanded(
                            child: Text(
                              'PKR ${controller.offerAmount.value.round()}',
                              style: textTheme.titleLarge?.copyWith(
                                fontWeight: FontWeight.w900,
                              ),
                            ),
                          ),
                          IconButton(
                            onPressed: () => controller.adjustOffer(-50),
                            icon: const Icon(Icons.remove),
                          ),
                          IconButton(
                            onPressed: () => controller.adjustOffer(50),
                            icon: const Icon(Icons.add),
                          ),
                        ],
                      ),
                    ),
                  ),
                ),
              ],
              const SizedBox(height: SSizes.md),
              Row(
                children: [
                  Expanded(
                    child: OutlinedButton(
                      onPressed: controller.dismissIncoming,
                      child: const Text('Decline'),
                    ),
                  ),
                  const SizedBox(width: SSizes.md),
                  Expanded(
                    child: Obx(
                      () => ElevatedButton(
                        onPressed: controller.isSubmitting.value
                            ? null
                            : () => request.isHybrid
                                ? controller.submitHybridOffer(request)
                                : controller.acceptFixedRide(request),
                        child: Text(
                          request.isHybrid ? 'Submit Offer' : 'Accept',
                        ),
                      ),
                    ),
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }
}
