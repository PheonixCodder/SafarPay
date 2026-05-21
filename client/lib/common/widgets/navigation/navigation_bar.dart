import 'package:flutter/material.dart';
import 'package:iconsax/iconsax.dart';

import '../../../utils/constants/colors.dart';
import '../../../utils/constants/sizes.dart';
import '../../../utils/constants/texts.dart';
import 'navigation_destination_data.dart';
import 'navigation_tab.dart';

class SNavigationBar extends StatelessWidget {
  const SNavigationBar({
    super.key,
    required this.selectedIndex,
    required this.onDestinationSelected,
    this.destinations = _passengerDestinations,
  });

  static const Duration _animationDuration = Duration(milliseconds: 260);
  static const Curve _animationCurve = Curves.easeOutCubic;
  static const List<SNavigationDestinationData> _passengerDestinations = [
    SNavigationDestinationData(
      icon: Iconsax.home_2,
      activeIcon: Iconsax.home_25,
      label: STexts.navHome,
    ),
    SNavigationDestinationData(
      icon: Iconsax.clock,
      activeIcon: Iconsax.clock5,
      label: STexts.navTrips,
    ),
    SNavigationDestinationData(
      icon: Iconsax.car,
      activeIcon: Iconsax.car5,
      label: STexts.navRent,
    ),
    SNavigationDestinationData(
      icon: Iconsax.profile_circle,
      activeIcon: Iconsax.profile_circle5,
      label: STexts.navProfile,
    ),
  ];

  final int selectedIndex;
  final ValueChanged<int> onDestinationSelected;
  final List<SNavigationDestinationData> destinations;

  @override
  Widget build(BuildContext context) {
    return SafeArea(
      top: false,
      child: Container(
        height: SSizes.navigationBarHeight,
        decoration: const BoxDecoration(
          color: SColors.white,
          border: Border(
            top: BorderSide(color: SColors.borderSecondary),
          ),
        ),
        child: LayoutBuilder(
          builder: (context, constraints) {
            final tabWidth = constraints.maxWidth / destinations.length;
            final indicatorLeft = (tabWidth * selectedIndex) +
                ((tabWidth - SSizes.navigationIndicatorWidth) / 2);

            return Stack(
              alignment: Alignment.topCenter,
              children: [
                AnimatedPositioned(
                  left: indicatorLeft,
                  top: 0,
                  duration: _animationDuration,
                  curve: _animationCurve,
                  child: Container(
                    width: SSizes.navigationIndicatorWidth,
                    height: SSizes.navigationIndicatorHeight,
                    decoration: const BoxDecoration(
                      color: SColors.primary,
                      borderRadius: BorderRadius.vertical(
                        bottom: Radius.circular(SSizes.cardRadiusXs),
                      ),
                    ),
                  ),
                ),
                Row(
                  children: List.generate(destinations.length, (index) {
                    final destination = destinations[index];
                    return SNavigationTab(
                      icon: destination.icon,
                      activeIcon: destination.activeIcon,
                      label: destination.label,
                      isActive: selectedIndex == index,
                      onTap: () => onDestinationSelected(index),
                    );
                  }),
                ),
              ],
            );
          },
        ),
      ),
    );
  }
}
