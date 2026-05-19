import 'package:client/features/location/domain/ride_booking_models.dart';
import 'package:client/utils/constants/colors.dart';
import 'package:client/utils/constants/sizes.dart';
import 'package:flutter/material.dart';
import 'package:iconsax/iconsax.dart';

class SLocationInputBar extends StatelessWidget {
  const SLocationInputBar({
    super.key,
    required this.label,
    required this.value,
    required this.target,
    required this.isActive,
    required this.onTap,
    required this.onPinTap,
  });

  final String label;
  final String value;
  final SBookingLocationTarget target;
  final bool isActive;
  final VoidCallback onTap;
  final VoidCallback onPinTap;

  @override
  Widget build(BuildContext context) {
    final textTheme = Theme.of(context).textTheme;
    final icon = target == SBookingLocationTarget.pickup
        ? Iconsax.location_tick
        : Iconsax.flag;

    return DecoratedBox(
      decoration: BoxDecoration(
        color: isActive ? SColors.lightContainer : SColors.white,
        borderRadius: BorderRadius.circular(SSizes.inputFieldRadius),
        border: Border.all(
          color: isActive ? SColors.primary : SColors.borderSecondary,
        ),
      ),
      child: Row(
        children: [
          Expanded(
            child: InkWell(
              borderRadius: BorderRadius.circular(SSizes.inputFieldRadius),
              onTap: onTap,
              child: Padding(
                padding: const EdgeInsets.symmetric(
                  horizontal: SSizes.md,
                  vertical: SSizes.md,
                ),
                child: Row(
                  children: [
                    Icon(icon, color: SColors.primary, size: SSizes.iconMd),
                    const SizedBox(width: SSizes.sm),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            label,
                            style: textTheme.labelMedium?.copyWith(
                              color: SColors.textSecondary,
                              fontWeight: FontWeight.w700,
                            ),
                          ),
                          const SizedBox(height: SSizes.xs),
                          Text(
                            value,
                            maxLines: 1,
                            overflow: TextOverflow.ellipsis,
                            style: textTheme.titleSmall?.copyWith(
                              color: SColors.textPrimary,
                              fontWeight: FontWeight.w800,
                            ),
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ),
          IconButton(
            tooltip: 'Select on map',
            onPressed: onPinTap,
            icon: const Icon(Iconsax.map_1),
            color: SColors.primary,
          ),
        ],
      ),
    );
  }
}
