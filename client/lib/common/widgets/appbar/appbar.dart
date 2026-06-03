import 'package:flutter/material.dart';
import 'package:get/get_core/src/get_main.dart';
import 'package:get/get_navigation/src/extension_navigation.dart';
import 'package:iconsax/iconsax.dart';

import '../../../utils/constants/colors.dart';
import '../../../utils/constants/sizes.dart';
import '../../../utils/device/utility.dart';

class SAppBar extends StatelessWidget implements PreferredSizeWidget {
  const SAppBar({
    super.key,
    this.title,
    this.actions,
    this.leadingIcon,
    this.leadingOnPressed,
    this.showBackArrow = false,
    this.showCircularBack = false,
    this.centerTitle,
  });

  final Widget? title;
  final IconData? leadingIcon;
  final bool showBackArrow;
  final bool showCircularBack;
  final List<Widget>? actions;
  final VoidCallback? leadingOnPressed;
  final bool? centerTitle;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: SSizes.md),
      child: AppBar(
        automaticallyImplyLeading: false,
        leading: showCircularBack
            ? Center(
                child: Container(
                  width: 40,
                  height: 40,
                  decoration: const BoxDecoration(
                    color: SColors.surfaceContainerHigh,
                    shape: BoxShape.circle,
                  ),
                  child: IconButton(
                    onPressed: leadingOnPressed ?? () => Get.back(),
                    icon: const Icon(
                      Iconsax.arrow_left,
                      color: SColors.onSurface,
                      size: 20,
                    ),
                    padding: EdgeInsets.zero,
                    constraints: const BoxConstraints(),
                  ),
                ),
              )
            : showBackArrow
                ? IconButton(
                    onPressed: () => Get.back(),
                    icon: const Icon(Iconsax.arrow_left))
                : leadingIcon != null
                    ? IconButton(
                        onPressed: leadingOnPressed, icon: Icon(leadingIcon))
                    : null,
        title: title,
        centerTitle: centerTitle,
        actions: actions,
      ),
    );
  }

  @override
  Size get preferredSize => Size.fromHeight(SDeviceUtils.getAppBarHeight());
}
