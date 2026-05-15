import 'package:flutter/material.dart';
import 'package:get/get.dart';

import 'common/widgets/navigation/navigation_bar.dart';
import 'navigation_controller.dart';
import 'utils/constants/colors.dart';

class NavigationMenu extends StatelessWidget {
  const NavigationMenu({super.key});

  @override
  Widget build(BuildContext context) {
    final controller = Get.put(SNavigationController());

    return Scaffold(
      backgroundColor: SColors.primaryBackground,
      bottomNavigationBar: Obx(
        () => SNavigationBar(
          selectedIndex: controller.selectedIndex.value,
          onDestinationSelected: controller.changeTab,
        ),
      ),
      body: Obx(
        () => IndexedStack(
          index: controller.selectedIndex.value,
          children: controller.screens,
        ),
      ),
    );
  }
}
