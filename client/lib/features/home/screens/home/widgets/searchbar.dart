import 'package:client/common/widgets/ride/search_result.dart';
import 'package:client/common/widgets/searchbar/searchbar.dart';
import 'package:client/data/rides/demi_rides.dart';
import 'package:client/data/rides/ride_models.dart';
import 'package:client/utils/constants/sizes.dart';
import 'package:flutter/material.dart';
import 'package:iconsax/iconsax.dart';

class SSearchContainer extends StatelessWidget {
  const SSearchContainer({
    super.key,
    required this.text,
    required this.icon,
    this.showBackground = true,
    this.showBorder = true,
    this.endIcon,
    this.onSearchPressed,
  });

  final String text;
  final IconData? icon;
  final IconData? endIcon;
  final VoidCallback? onSearchPressed;
  final bool showBackground, showBorder;

  @override
  Widget build(BuildContext context) {
    final recentRides = SDemoRides.items.take(2).toList();

    return Column(
      children: [
        SSearchBar(
          searchText: text,
          icon: icon,
          endIcon: endIcon,
          onPressed: onSearchPressed,
          showBackground: showBackground,
          showBorder: showBorder,
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
