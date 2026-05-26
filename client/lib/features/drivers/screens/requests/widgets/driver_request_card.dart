import 'package:flutter/material.dart';

import '../../../../../utils/constants/colors.dart';
import '../../../../../utils/constants/sizes.dart';
import '../../../domain/driver_request_models.dart';

class SDriverRequestCard extends StatelessWidget {
  const SDriverRequestCard({
    super.key,
    required this.request,
    required this.onTap,
  });

  final SDriverRideRequest request;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    final textTheme = Theme.of(context).textTheme;
    final eta = request.driverToPickup?.durationMinutes.round();
    final distance = request.driverToPickup?.distanceKm;

    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(SSizes.cardRadiusMd),
      child: Ink(
        decoration: BoxDecoration(
          color: SColors.white,
          borderRadius: BorderRadius.circular(SSizes.cardRadiusMd),
          border: Border.all(color: SColors.borderSecondary),
        ),
        child: Padding(
          padding: const EdgeInsets.all(SSizes.md),
          child: Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              CircleAvatar(
                backgroundColor: SColors.lightContainer,
                foregroundColor: SColors.primary,
                child: Text(
                  request.passengerId.isEmpty
                      ? 'R'
                      : request.passengerId[0].toUpperCase(),
                ),
              ),
              const SizedBox(width: SSizes.md),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
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
                        if (distance != null)
                          Text(
                            '${distance.toStringAsFixed(1)} km',
                            style: textTheme.labelLarge?.copyWith(
                              color: SColors.textSecondary,
                              fontWeight: FontWeight.w700,
                            ),
                          ),
                      ],
                    ),
                    const SizedBox(height: SSizes.xs),
                    Text(
                      request.pickup?.displayName ?? 'Pickup unavailable',
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                      style: textTheme.titleMedium?.copyWith(
                        fontWeight: FontWeight.w800,
                      ),
                    ),
                    const SizedBox(height: SSizes.xs),
                    Text(
                      request.dropoff?.displayName ?? 'Dropoff unavailable',
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                      style: textTheme.bodyMedium?.copyWith(
                        color: SColors.textSecondary,
                      ),
                    ),
                    const SizedBox(height: SSizes.sm),
                    Wrap(
                      spacing: SSizes.sm,
                      runSpacing: SSizes.xs,
                      children: [
                        Chip(label: Text(request.paymentMethod)),
                        Chip(label: Text(_label(request.category))),
                        Chip(label: Text(request.pricingMode)),
                        if (eta != null) Chip(label: Text('$eta min')),
                      ],
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

String _label(String value) {
  return value.replaceAll('_', ' ');
}
