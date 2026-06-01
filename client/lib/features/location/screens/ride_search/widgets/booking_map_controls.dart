import 'package:client/features/location/controllers/ride_search_controller.dart';
import 'package:client/utils/constants/colors.dart';
import 'package:client/utils/constants/sizes.dart';
import 'package:client/utils/helpers/helpers.dart';
import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'package:iconsax/iconsax.dart';

/// Map chrome for ride search: back (top-left), pin-confirm and my-location (right).
class SBookingMapControls extends StatelessWidget {
  const SBookingMapControls({
    super.key,
    required this.controller,
  });

  final SRideSearchController controller;

  static const double _actionButtonsBottom = 380;

  @override
  Widget build(BuildContext context) {
    return Stack(
      children: [
        SafeArea(
          bottom: false,
          child: Padding(
            padding: const EdgeInsets.all(SSizes.md),
            child: Align(
              alignment: Alignment.topLeft,
              child: _MapButton(
                icon: Iconsax.arrow_left,
                onPressed: Get.back,
              ),
            ),
          ),
        ),
        Positioned(
          right: SSizes.md,
          bottom: _actionButtonsBottom,
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Obx(
                () => _MapButton(
                  icon: Iconsax.gps,
                  isBusy: controller.isResolvingPin.value,
                  onPressed: controller.confirmMapPin,
                ),
              ),
              const SizedBox(height: SSizes.sm),
              Obx(
                () => _MapButton(
                  icon: Icons.my_location,
                  isBusy: controller.isLocating.value,
                  onPressed: controller.goToMyLocation,
                ),
              ),
            ],
          ),
        ),
      ],
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
        tooltip: isBusy ? 'Please wait' : null,
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
