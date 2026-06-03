import 'package:client/features/location/controllers/ride_search_controller.dart';
import 'package:client/utils/constants/colors.dart';
import 'package:client/utils/constants/sizes.dart';
import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'package:iconsax/iconsax.dart';

class SFareOfferPanel extends StatelessWidget {
  const SFareOfferPanel({
    super.key,
    required this.controller,
  });

  final SRideSearchController controller;

  @override
  Widget build(BuildContext context) {
    final textTheme = Theme.of(context).textTheme;

    return DecoratedBox(
      decoration: BoxDecoration(
        color: SColors.lightContainer,
        borderRadius: BorderRadius.circular(SSizes.cardRadiusLg),
        border: Border.all(color: SColors.borderSecondary),
      ),
      child: Padding(
        padding: const EdgeInsets.all(SSizes.md),
        child: Column(
          children: [
            Row(
              children: [
                _FareButton(
                  icon: Iconsax.minus,
                  onPressed: () => controller.adjustPassengerOffer(-25),
                ),
                Expanded(
                  child: Obx(
                    () => Column(
                      children: [
                        Text(
                          'PKR${controller.passengerOffer.value.round()}',
                          style: textTheme.headlineSmall?.copyWith(
                            color: SColors.textPrimary,
                            fontWeight: FontWeight.w900,
                          ),
                        ),
                        Text(
                          'Your offer',
                          style: textTheme.bodySmall?.copyWith(
                            color: SColors.textSecondary,
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
                _FareButton(
                  icon: Iconsax.add,
                  onPressed: () => controller.adjustPassengerOffer(25),
                ),
              ],
            ),
            const SizedBox(height: SSizes.sm),
            Obx(
              () => SwitchListTile(
                contentPadding: EdgeInsets.zero,
                value: controller.autoAcceptOffer.value,
                onChanged: (value) => controller.autoAcceptOffer.value = value,
                title: Text(
                  'Auto-accept matching driver',
                  style: textTheme.bodyMedium?.copyWith(
                    color: SColors.textPrimary,
                    fontWeight: FontWeight.w700,
                  ),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _FareButton extends StatelessWidget {
  const _FareButton({
    required this.icon,
    required this.onPressed,
  });

  final IconData icon;
  final VoidCallback onPressed;

  @override
  Widget build(BuildContext context) {
    return IconButton.filled(
      style: IconButton.styleFrom(
        backgroundColor: SColors.surfaceContainer,
        foregroundColor: SColors.textPrimary,
      ),
      onPressed: onPressed,
      icon: Icon(icon),
    );
  }
}
