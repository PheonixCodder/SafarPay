import 'package:client/common/navigation/right_slide_page_route.dart';
import 'package:client/common/widgets/ride/recent_ride_destinations.dart';
import 'package:client/common/widgets/searchbar/searchbar.dart';
import 'package:client/features/location/data/device_location_service.dart';
import 'package:client/features/location/screens/ride_search/ride_search_screen.dart';
import 'package:client/utils/constants/sizes.dart';
import 'package:flutter/material.dart';

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
        SRecentRideDestinations(
          originFuture: const SDeviceLocationService().currentCoordinate(),
          onSelected: (destination) {
            Navigator.of(context).push(
              SRightSlidePageRoute(
                page: RideSearchScreen(initialDropoff: destination),
              ),
            );
          },
        ),
      ],
    );
  }
}
