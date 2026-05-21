import 'package:client/features/personalization/screens/settings/settings.dart';
import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'package:iconsax/iconsax.dart';

import 'common/widgets/navigation/navigation_destination_data.dart';
import 'common/widgets/navigation/navigation_placeholder_screen.dart';
import 'features/home/screens/home/home.dart';
import 'features/rides/screens/trips/trips.dart';
import 'utils/constants/app_mode.dart';
import 'utils/constants/texts.dart';

class SNavigationController extends GetxController {
  final Rx<int> selectedIndex = 0.obs;

  final List<Widget> passengerScreens = [
    const HomeScreen(),
    const TripsScreen(),
    const SNavigationPlaceholderScreen(
      icon: Iconsax.car,
      title: STexts.rentTabTitle,
      subtitle: STexts.rentTabSubTitle,
    ),
    const SettingsScreen(),
  ];

  final List<Widget> driverScreens = [
    const SNavigationPlaceholderScreen(
      icon: Iconsax.car,
      title: STexts.driverNavHomeTitle,
      subtitle: STexts.driverNavHomeSubTitle,
    ),
    const SNavigationPlaceholderScreen(
      icon: Iconsax.routing_2,
      title: STexts.driverNavRequestsTitle,
      subtitle: STexts.driverNavRequestsSubTitle,
    ),
    const SNavigationPlaceholderScreen(
      icon: Iconsax.wallet_3,
      title: STexts.driverNavEarningsTitle,
      subtitle: STexts.driverNavEarningsSubTitle,
    ),
    const SettingsScreen(),
  ];

  final List<SNavigationDestinationData> passengerDestinations = const [
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

  final List<SNavigationDestinationData> driverDestinations = const [
    SNavigationDestinationData(
      icon: Iconsax.car,
      activeIcon: Iconsax.car5,
      label: STexts.driverNavHome,
    ),
    SNavigationDestinationData(
      icon: Iconsax.routing_2,
      activeIcon: Iconsax.routing_25,
      label: STexts.driverNavRequests,
    ),
    SNavigationDestinationData(
      icon: Iconsax.wallet_3,
      activeIcon: Iconsax.wallet_3,
      label: STexts.driverNavEarnings,
    ),
    SNavigationDestinationData(
      icon: Iconsax.profile_circle,
      activeIcon: Iconsax.profile_circle5,
      label: STexts.navProfile,
    ),
  ];

  void changeTab(int index) {
    if (index == selectedIndex.value) return;
    selectedIndex.value = index;
  }

  List<Widget> screensFor(SAppMode mode) {
    return mode == SAppMode.driver ? driverScreens : passengerScreens;
  }

  List<SNavigationDestinationData> destinationsFor(SAppMode mode) {
    return mode == SAppMode.driver ? driverDestinations : passengerDestinations;
  }
}
