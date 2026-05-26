import 'package:flutter/material.dart';
import 'package:iconsax/iconsax.dart';

import '../../../../../utils/constants/colors.dart';
import '../../../../../utils/constants/sizes.dart';
import '../../../../../utils/helpers/helpers.dart';
import '../../../domain/earnings_models.dart';
import 'earnings_formatters.dart';

class SEarningsRecentTripTile extends StatelessWidget {
  const SEarningsRecentTripTile({super.key, required this.trip});

  final SDriverEarningsTrip trip;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(bottom: SSizes.md),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Container(
            width: 42,
            height: 42,
            decoration: BoxDecoration(
              color: SHelperFunctions.withOpacity(
                SColors.primary,
                SOpacities.tinted,
              ),
              borderRadius: BorderRadius.circular(SSizes.borderRadiusMd),
            ),
            child: const Icon(Iconsax.routing_2, color: SColors.primary),
          ),
          const SizedBox(width: SSizes.md),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  '${trip.pickupLabel} to ${trip.dropoffLabel}',
                  maxLines: 2,
                  overflow: TextOverflow.ellipsis,
                  style: Theme.of(context).textTheme.titleSmall?.copyWith(
                        fontWeight: FontWeight.w800,
                      ),
                ),
                const SizedBox(height: SSizes.xs),
                Text(
                  '${sFormatServiceType(trip.serviceType)} · ${trip.collectionMode.replaceAll('_', ' ')}',
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                  style: Theme.of(context).textTheme.bodySmall?.copyWith(
                        color: SColors.textSecondary,
                        fontWeight: FontWeight.w600,
                      ),
                ),
              ],
            ),
          ),
          const SizedBox(width: SSizes.md),
          Text(
            sFormatMoney(trip.netEarning),
            style: Theme.of(context).textTheme.titleSmall?.copyWith(
                  color: SColors.primary,
                  fontWeight: FontWeight.w800,
                ),
          ),
        ],
      ),
    );
  }
}
