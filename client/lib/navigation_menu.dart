import 'package:flutter/material.dart';
import 'package:get/get.dart';

import 'app_mode_controller.dart';
import 'common/widgets/navigation/navigation_bar.dart';
import 'navigation_controller.dart';
import 'utils/constants/colors.dart';

class NavigationMenu extends StatelessWidget {
  const NavigationMenu({super.key});

  @override
  Widget build(BuildContext context) {
    final controller = Get.put(SNavigationController());
    final appModeController = SAppModeController.instance;

    return Obx(
      () {
        final mode = appModeController.currentMode.value;
        final screens = controller.screensFor(mode);

        return Scaffold(
          backgroundColor: SColors.primaryBackground,
          bottomNavigationBar: SNavigationBar(
            selectedIndex: controller.selectedIndex.value,
            onDestinationSelected: controller.changeTab,
            destinations: controller.destinationsFor(mode),
          ),
          body: IndexedStack(
            index: controller.selectedIndex.value,
            children: screens,
          ),
        );
      },
    );
  }
}
