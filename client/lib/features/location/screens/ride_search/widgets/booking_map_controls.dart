import 'package:client/features/location/controllers/ride_search_controller.dart';
import 'package:client/utils/constants/colors.dart';
import 'package:client/utils/constants/sizes.dart';
import 'package:client/utils/helpers/helpers.dart';
import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'package:iconsax/iconsax.dart';

class SBookingMapControls extends StatelessWidget {
  const SBookingMapControls({
    super.key,
    required this.controller,
  });

  final SRideSearchController controller;

  @override
  Widget build(BuildContext context) {
    return SafeArea(
      bottom: false,
      child: Padding(
        padding: const EdgeInsets.all(SSizes.md),
        child: Row(
          children: [
            _MapButton(
              icon: Iconsax.arrow_left,
              onPressed: Get.back,
            ),
            const Spacer(),
            Obx(
              () => _MapButton(
                icon: Iconsax.gps,
                isBusy: controller.isResolvingPin.value,
                onPressed: controller.confirmMapPin,
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _MapButton extends StatelessWidget {
  const _MapButton({
    required this.icon,
    required this.onPressed,
    this.isBusy = false,
  });

  final IconData icon;
  final VoidCallback onPressed;
  final bool isBusy;

  @override
  Widget build(BuildContext context) {
    return DecoratedBox(
      decoration: BoxDecoration(
        color: SColors.white,
        borderRadius: BorderRadius.circular(SSizes.radiusFull),
        boxShadow: [
          BoxShadow(
            color: SHelperFunctions.withOpacity(
              SColors.pureBlack,
              SOpacities.shadow,
            ),
            blurRadius: SSizes.shadowBlurLg,
            offset: const Offset(0, SSizes.sm),
          ),
        ],
      ),
      child: IconButton(
        tooltip: isBusy ? 'Resolving location' : null,
        onPressed: isBusy ? null : onPressed,
        icon: isBusy
            ? const SizedBox(
                width: SSizes.iconMd,
                height: SSizes.iconMd,
                child: CircularProgressIndicator(strokeWidth: 2),
              )
            : Icon(icon),
        color: SColors.textPrimary,
      ),
    );
  }
}
