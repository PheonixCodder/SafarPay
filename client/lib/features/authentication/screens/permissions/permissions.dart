import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'package:iconsax/iconsax.dart';

import '../../../../utils/constants/texts.dart';
import '../../controllers/permissions.dart';
import 'widgets/permission_page.dart';

class PermissionsScreen extends StatelessWidget {
  const PermissionsScreen({super.key});

  static const _duration = Duration(milliseconds: 350);

  @override
  Widget build(BuildContext context) {
    final controller = Get.put(SPermissionsController());

    return Obx(
      () => AnimatedSwitcher(
        duration: _duration,
        switchInCurve: Curves.easeOutCubic,
        switchOutCurve: Curves.easeInCubic,
        child: switch (controller.currentStep.value) {
          SPermissionStep.location => SPermissionPage(
              key: const ValueKey(SPermissionStep.location),
              icon: Iconsax.location,
              title: STexts.locationTitle,
              subTitle: STexts.locationSubTitle,
              buttonText: STexts.allowLocationAccess,
              onPressed: controller.requestLocationPermission,
              isRequesting: controller.isRequesting,
            ),
          SPermissionStep.notification => SPermissionPage(
              key: const ValueKey(SPermissionStep.notification),
              icon: Iconsax.notification,
              title: STexts.notificationsTitle,
              subTitle: STexts.notificationsSubTitle,
              buttonText: STexts.allowNotificationAccess,
              onPressed: controller.requestNotificationPermission,
              isRequesting: controller.isRequesting,
            ),
        },
      ),
    );
  }
}
