import 'package:flutter/material.dart';

import '../../../../../utils/constants/colors.dart';
import '../../../../../utils/constants/sizes.dart';
import 'trips_tab_button.dart';

class STripsTabBar extends StatelessWidget {
  const STripsTabBar({
    super.key,
    required this.tabs,
    required this.selectedIndex,
    required this.onTabSelected,
  });

  static const Duration _duration = Duration(milliseconds: 260);
  static const Curve _curve = Curves.easeOutCubic;

  final List<String> tabs;
  final int selectedIndex;
  final ValueChanged<int> onTabSelected;

  @override
  Widget build(BuildContext context) {
    return Container(
      height: SSizes.tripsTabBarHeight,
      padding: const EdgeInsets.all(SSizes.tripsTabBarPadding),
      decoration: BoxDecoration(
        color: SColors.white,
        borderRadius: BorderRadius.circular(SSizes.tripsTabIndicatorRadius),
        border: Border.all(color: SColors.borderSecondary),
      ),
      child: LayoutBuilder(
        builder: (context, constraints) {
          final tabWidth = constraints.maxWidth / tabs.length;

          return Stack(
            children: [
              AnimatedPositioned(
                left: tabWidth * selectedIndex,
                top: 0,
                bottom: 0,
                width: tabWidth,
                duration: _duration,
                curve: _curve,
                child: Container(
                  decoration: BoxDecoration(
                    color: SColors.primary,
                    borderRadius: BorderRadius.circular(
                      SSizes.tripsTabIndicatorRadius -
                          SSizes.tripsTabBarPadding,
                    ),
                  ),
                ),
              ),
              Row(
                children: [
                  for (var index = 0; index < tabs.length; index++)
                    Expanded(
                      child: STripsTabButtonItem(
                        label: tabs[index],
                        isSelected: selectedIndex == index,
                        duration: _duration,
                        curve: _curve,
                        onTap: () => onTabSelected(index),
                      ),
                    ),
                ],
              ),
            ],
          );
        },
      ),
    );
  }
}
