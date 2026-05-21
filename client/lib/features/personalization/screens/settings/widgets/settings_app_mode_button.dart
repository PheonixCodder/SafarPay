import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'package:iconsax/iconsax.dart';

import '../../../../../app_mode_controller.dart';
import '../../../../../utils/constants/colors.dart';
import '../../../../../utils/constants/texts.dart';

class SSettingsAppModeButton extends StatelessWidget {
  const SSettingsAppModeButton({super.key});

  @override
  Widget build(BuildContext context) {
    final controller = SAppModeController.instance;

    return Obx(
      () {
        if (!controller.canUseDriverMode) return const SizedBox.shrink();

        final isDriverMode = controller.isDriverMode;
        final label = isDriverMode
            ? STexts.switchToPassengerMode
            : STexts.switchToDriverMode;
        final icon = isDriverMode ? Iconsax.user : Iconsax.car;

        return SizedBox(
          width: double.infinity,
          child: ElevatedButton.icon(
            onPressed: controller.toggleMode,
            icon: Icon(icon, color: Colors.white), // White icon
            label: Text(label, style: const TextStyle(color: Colors.white)), // White text
            style: ElevatedButton.styleFrom(
              backgroundColor: SColors.primary, // Primary background
              side: const BorderSide(color: SColors.primary), // Keeps the outline look
              elevation: 0, // Set to 0 if you want it flat like an OutlinedButton
            ),
          ),

        );
      },
    );
  }
}
