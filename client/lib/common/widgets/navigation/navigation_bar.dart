import 'package:flutter/material.dart';
import 'package:iconsax/iconsax.dart';

import '../../../utils/constants/colors.dart';
import '../../../utils/constants/sizes.dart';
import '../../../utils/constants/texts.dart';
import 'navigation_tab.dart';

class SNavigationBar extends StatelessWidget {
  const SNavigationBar({
    super.key,
    required this.selectedIndex,
    required this.onDestinationSelected,
  });

  static const Duration _animationDuration = Duration(milliseconds: 260);
  static const Curve _animationCurve = Curves.easeOutCubic;

  final int selectedIndex;
  final ValueChanged<int> onDestinationSelected;

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
            final tabWidth =
                constraints.maxWidth / SSizes.navigationDestinationCount;
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
                  children: [
                    SNavigationTab(
                      icon: Iconsax.home_2,
                      activeIcon: Iconsax.home_25,
                      label: STexts.navHome,
                      isActive: selectedIndex == 0,
                      onTap: () => onDestinationSelected(0),
                    ),
                    SNavigationTab(
                      icon: Iconsax.clock,
                      activeIcon: Iconsax.clock5,
                      label: STexts.navTrips,
                      isActive: selectedIndex == 1,
                      onTap: () => onDestinationSelected(1),
                    ),
                    SNavigationTab(
                      icon: Iconsax.car,
                      activeIcon: Iconsax.car5,
                      label: STexts.navRent,
                      isActive: selectedIndex == 2,
                      onTap: () => onDestinationSelected(2),
                    ),
                    SNavigationTab(
                      icon: Iconsax.profile_circle,
                      activeIcon: Iconsax.profile_circle5,
                      label: STexts.navProfile,
                      isActive: selectedIndex == 3,
                      onTap: () => onDestinationSelected(3),
                    ),
                  ],
                ),
              ],
            );
          },
        ),
      ),
    );
  }
}
