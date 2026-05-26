import 'package:client/features/location/domain/ride_booking_models.dart';
import 'package:client/utils/constants/colors.dart';
import 'package:client/utils/constants/sizes.dart';
import 'package:flutter/material.dart';

class SRideOptionStepper extends StatelessWidget {
  const SRideOptionStepper({super.key, required this.mode});

  final SBookingSheetMode mode;

  @override
  Widget build(BuildContext context) {
    final steps = [
      ('Ride', SBookingSheetMode.vehicles),
      ('Details', SBookingSheetMode.details),
      ('Review', SBookingSheetMode.review),
    ];
    final activeIndex = steps.indexWhere((step) => step.$2 == mode);

    return Row(
      children: [
        for (var index = 0; index < steps.length; index++) ...[
          Expanded(
            child: DecoratedBox(
              decoration: BoxDecoration(
                color: index <= activeIndex
                    ? SColors.primary
                    : SColors.borderSecondary,
                borderRadius: BorderRadius.circular(SSizes.radiusFull),
              ),
              child: Padding(
                padding: const EdgeInsets.symmetric(vertical: SSizes.xs),
                child: Text(
                  steps[index].$1,
                  textAlign: TextAlign.center,
                  style: Theme.of(context).textTheme.labelSmall?.copyWith(
                        color: index <= activeIndex
                            ? SColors.white
                            : SColors.textSecondary,
                        fontWeight: FontWeight.w800,
                      ),
                ),
              ),
            ),
          ),
          if (index != steps.length - 1) const SizedBox(width: SSizes.xs),
        ],
      ],
    );
  }
}
