import 'package:client/features/personalization/screens/settings/settings.dart';
import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'package:iconsax/iconsax.dart';

import 'common/widgets/navigation/navigation_placeholder_screen.dart';
import 'features/home/screens/home/home.dart';
import 'features/rides/screens/trips/trips.dart';
import 'utils/constants/texts.dart';

class SNavigationController extends GetxController {
  final Rx<int> selectedIndex = 0.obs;

  final List<Widget> screens = [
    const HomeScreen(),
    const TripsScreen(),
    const SNavigationPlaceholderScreen(
      icon: Iconsax.car,
      title: STexts.rentTabTitle,
      subtitle: STexts.rentTabSubTitle,
    ),
    const SettingsScreen(),
  ];

  void changeTab(int index) {
    if (index == selectedIndex.value) return;
    selectedIndex.value = index;
  }
}
