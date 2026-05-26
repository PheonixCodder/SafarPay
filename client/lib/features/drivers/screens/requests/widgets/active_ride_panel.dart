import 'package:flutter/material.dart';
import 'package:get/get.dart';

import '../../../../../utils/constants/colors.dart';
import '../../../../../utils/constants/sizes.dart';
import '../../../controllers/driver_requests_controller.dart';
import '../../../domain/driver_request_models.dart';
import 'trip_otp_dialog.dart';

class SActiveRidePanel extends StatelessWidget {
  const SActiveRidePanel({
    super.key,
    required this.controller,
    required this.ride,
  });

  final SDriverRequestsController controller;
  final SDriverActiveRide ride;

  @override
  Widget build(BuildContext context) {
    final textTheme = Theme.of(context).textTheme;

    return Material(
      color: SColors.white,
      borderRadius: BorderRadius.circular(SSizes.cardRadiusLg),
      elevation: 12,
      child: Padding(
        padding: const EdgeInsets.all(SSizes.md),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'PKR ${ride.displayFare.round()}',
              style: textTheme.headlineSmall?.copyWith(
                fontWeight: FontWeight.w900,
              ),
            ),
            const SizedBox(height: SSizes.sm),
            Text(
              'Pickup',
              style: textTheme.labelMedium?.copyWith(
                color: SColors.textSecondary,
              ),
            ),
            Text(
              ride.pickup?.displayName ?? 'Pickup unavailable',
              maxLines: 1,
              overflow: TextOverflow.ellipsis,
            ),
            const SizedBox(height: SSizes.sm),
            Text(
              'Dropoff',
              style: textTheme.labelMedium?.copyWith(
                color: SColors.textSecondary,
              ),
            ),
            Text(
              ride.dropoff?.displayName ?? 'Dropoff unavailable',
              maxLines: 1,
              overflow: TextOverflow.ellipsis,
            ),
            const SizedBox(height: SSizes.md),
            if (ride.isInProgress) ...[
              Obx(() {
                final distance = controller.metersToDropoff;
                final text = distance == null
                    ? 'Waiting for driver location'
                    : controller.canCompleteTrip
                        ? 'You can complete this trip'
                        : '${distance.round()} m from dropoff';
                return Text(
                  text,
                  style: textTheme.labelLarge?.copyWith(
                    color: controller.canCompleteTrip
                        ? SColors.success
                        : SColors.textSecondary,
                    fontWeight: FontWeight.w700,
                  ),
                );
              }),
              const SizedBox(height: SSizes.sm),
            ],
            Obx(
              () => SizedBox(
                width: double.infinity,
                child: ElevatedButton(
                  onPressed: controller.isSubmitting.value
                      ? null
                      : _onPressed(context, controller, ride),
                  child: Text(_label(controller, ride)),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

VoidCallback? _onPressed(
  BuildContext context,
  SDriverRequestsController controller,
  SDriverActiveRide ride,
) {
  if (ride.isInProgress) {
    if (!controller.canCompleteTrip) return null;
    return () async {
      final code = await _verificationCode(
        context,
        isRequired: ride.requiresOtpEnd,
        title: 'Complete trip',
        subtitle: 'Ask the passenger for the trip completion code.',
      );
      if (ride.requiresOtpEnd && code == null) return;
      await controller.completeTrip(verificationCode: code);
    };
  }
  if (ride.hasArrivedAtPickup) {
    return () async {
      final code = await _verificationCode(
        context,
        isRequired: ride.requiresOtpStart,
        title: 'Start trip',
        subtitle: 'Ask the passenger for the pickup verification code.',
      );
      if (ride.requiresOtpStart && code == null) return;
      await controller.startTrip(verificationCode: code);
    };
  }
  if (controller.canArriveAtPickup) return controller.markArrivedAtPickup;
  return null;
}

Future<String?> _verificationCode(
  BuildContext context, {
  required bool isRequired,
  required String title,
  required String subtitle,
}) {
  if (!isRequired) return Future<String?>.value();
  return showDialog<String>(
    context: context,
    barrierDismissible: false,
    builder: (context) => STripOtpDialog(
      title: title,
      subtitle: subtitle,
    ),
  );
}

String _label(SDriverRequestsController controller, SDriverActiveRide ride) {
  if (ride.isInProgress) {
    return controller.canCompleteTrip
        ? 'Complete Trip'
        : 'Reach dropoff to complete';
  }
  if (ride.hasArrivedAtPickup) return 'Start Trip';
  return controller.canArriveAtPickup
      ? "I've Arrived at Pickup"
      : 'Arrive at pickup';
}
