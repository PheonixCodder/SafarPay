import 'package:client/features/personalization/screens/driver_registration/models/driver_registration_models.dart';
import 'package:client/utils/constants/colors.dart';
import 'package:client/utils/constants/sizes.dart';
import 'package:client/utils/constants/texts.dart';
import 'package:client/utils/helpers/helpers.dart';
import 'package:flutter/material.dart';

class SDriverVerificationHeaderCopy extends StatelessWidget {
  const SDriverVerificationHeaderCopy({
    super.key,
    required this.category,
    required this.vehicle,
  });

  final SDriverWorkCategory category;
  final SDriverVehicleOption vehicle;

  @override
  Widget build(BuildContext context) {
    final textTheme = Theme.of(context).textTheme;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Container(
          padding: const EdgeInsets.symmetric(
            horizontal: SSizes.md,
            vertical: SSizes.sm,
          ),
          decoration: BoxDecoration(
            color: SHelperFunctions.withOpacity(
              SColors.white,
              SOpacities.successTint,
            ),
            borderRadius: BorderRadius.circular(SSizes.radiusFull),
          ),
          child: Text(
            vehicle.title,
            style: textTheme.labelLarge?.copyWith(
              color: SColors.white,
              fontWeight: FontWeight.w700,
            ),
          ),
        ),
        const SizedBox(height: SSizes.md),
        Text(
          category.title,
          maxLines: 2,
          overflow: TextOverflow.ellipsis,
          style: textTheme.headlineSmall?.copyWith(
            color: SColors.white,
            fontWeight: FontWeight.w800,
            height: 1.1,
          ),
        ),
        const SizedBox(height: SSizes.sm),
        Text(
          STexts.driverVerificationHeaderSubtitle,
          maxLines: 3,
          overflow: TextOverflow.ellipsis,
          style: textTheme.bodyMedium?.copyWith(
            color: SHelperFunctions.withOpacity(
              SColors.white,
              SOpacities.stronger,
            ),
            height: 1.35,
          ),
        ),
      ],
    );
  }
}
