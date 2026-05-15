import 'package:flutter/material.dart';
import 'package:iconsax/iconsax.dart';

import '../../../../common/widgets/ride/search_result.dart';
import '../../../../data/rides/demi_rides.dart';
import '../../../../data/rides/ride_models.dart';
import '../../../../utils/constants/colors.dart';
import '../../../../utils/constants/sizes.dart';
import '../../../../utils/device/utility.dart';

class SSearchContainer extends StatelessWidget {
  const SSearchContainer({
    super.key,
    required this.text,
    required this.icon,
    this.showBackground = true,
    this.showBorder = true,
    this.endIcon,
  });

  final String text;
  final IconData? icon;
  final IconData? endIcon;
  final bool showBackground, showBorder;

  @override
  Widget build(BuildContext context) {
    final recentRides = SDemoRides.items.take(2).toList();

    return Column(
      children: [
        Padding(
          padding: const EdgeInsets.symmetric(horizontal: SSizes.defaultSpace),
          child: Container(
            width: SDeviceUtils.getScreenWidth(context),
            padding: const EdgeInsets.all(SSizes.md),
            decoration: BoxDecoration(
              color: showBackground ? SColors.white : SColors.transparent,
              borderRadius: BorderRadius.circular(SSizes.cardRadiusLg),
              border: showBorder ? Border.all(color: SColors.grey) : null,
            ),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Row(
                  children: [
                    Icon(icon, color: SColors.darkerGrey),
                    const SizedBox(width: SSizes.spaceBtnItems),
                    Text(text, style: Theme.of(context).textTheme.bodySmall),
                  ],
                ),
                Icon(endIcon, color: SColors.darkerGrey),
              ],
            ),
          ),
        ),
        const SizedBox(height: SSizes.md),
        ...recentRides.indexed.map((entry) {
          final index = entry.$1;
          final ride = entry.$2;
          final dropoff = ride.dropoffStop;

          return SSearchResult(
            icon: Iconsax.location,
            title: dropoff?.placeName ?? 'Recent destination',
            address: _formatAddress(dropoff),
            duration: _recentDuration(index),
            showDivider: index != recentRides.length - 1,
          );
        }),
      ],
    );
  }

  String _formatAddress(StopResponse? stop) {
    if (stop == null) return 'Address unavailable';

    final parts = <String>[
      if (stop.addressLine1 != null && stop.addressLine1!.trim().isNotEmpty)
        stop.addressLine1!,
      if (stop.addressLine2 != null && stop.addressLine2!.trim().isNotEmpty)
        stop.addressLine2!,
      if (stop.city != null && stop.city!.trim().isNotEmpty) stop.city!,
      if (stop.state != null && stop.state!.trim().isNotEmpty) stop.state!,
    ];

    return parts.join(', ');
  }

  String _recentDuration(int index) {
    const durations = [
      '40 min',
      '29 min',
    ];

    return durations[index];
  }
}
