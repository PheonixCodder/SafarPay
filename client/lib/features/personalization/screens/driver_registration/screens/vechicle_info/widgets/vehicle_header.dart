import 'package:client/features/personalization/screens/driver_registration/models/driver_registration_models.dart';
import 'package:client/utils/constants/colors.dart';
import 'package:client/utils/constants/sizes.dart';
import 'package:flutter/material.dart';

class SVehicleHeader extends StatelessWidget {
  const SVehicleHeader({
    super.key,
    required this.category,
    required this.vehicle,
  });

  final SDriverWorkCategory category;
  final SDriverVehicleOption vehicle;

  @override
  Widget build(BuildContext context) {
    final textTheme = Theme.of(context).textTheme;

    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(SSizes.lg),
      decoration: BoxDecoration(
        color: SColors.white,
        borderRadius: BorderRadius.circular(SSizes.cardRadiusLg),
        border: Border.all(color: SColors.borderSecondary),
      ),
      child: Row(
        children: [
          ClipRRect(
            borderRadius: BorderRadius.circular(SSizes.cardRadiusMd),
            child: Image.asset(
              vehicle.image,
              width: 64,
              height: 64,
              fit: BoxFit.contain,
            ),
          ),
          const SizedBox(width: SSizes.md),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  vehicle.title,
                  style: textTheme.titleLarge?.copyWith(
                    color: SColors.textPrimary,
                    fontWeight: FontWeight.w800,
                  ),
                ),
                const SizedBox(height: SSizes.xs),
                Text(
                  category.title,
                  style: textTheme.bodyMedium?.copyWith(
                    color: SColors.primary,
                    fontWeight: FontWeight.w700,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
