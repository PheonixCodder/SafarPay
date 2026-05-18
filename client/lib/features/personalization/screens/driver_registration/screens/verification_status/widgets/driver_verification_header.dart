import 'package:client/common/widgets/appbar/appbar.dart';
import 'package:client/common/widgets/containers/primary_header_container.dart';
import 'package:client/features/personalization/screens/driver_registration/models/driver_registration_models.dart';
import 'package:client/features/personalization/screens/driver_registration/screens/verification_status/widgets/driver_verification_header_copy.dart';
import 'package:client/utils/constants/colors.dart';
import 'package:client/utils/constants/sizes.dart';
import 'package:client/utils/constants/texts.dart';
import 'package:flutter/material.dart';

class SDriverVerificationHeader extends StatelessWidget {
  const SDriverVerificationHeader({
    super.key,
    required this.category,
    required this.vehicle,
  });

  final SDriverWorkCategory category;
  final SDriverVehicleOption vehicle;

  @override
  Widget build(BuildContext context) {
    final textTheme = Theme.of(context).textTheme;

    return SPrimaryHeaderContainer(
      height: SSizes.primaryHeaderHeight - 50,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          SAppBar(
            showBackArrow: true,
            title: Text(
              STexts.driverVerificationTitle,
              style: textTheme.headlineSmall?.copyWith(
                color: SColors.white,
                fontWeight: FontWeight.w800,
              ),
            ),
          ),
          Padding(
            padding: const EdgeInsets.fromLTRB(
              SSizes.defaultSpace,
              SSizes.md,
              SSizes.defaultSpace,
              0,
            ),
            child: SizedBox(
              height: 245,
              width: double.infinity,
              child: Stack(
                clipBehavior: Clip.none,
                children: [
                  Positioned(
                    left: 0,
                    top: SSizes.md,
                    right: 130,
                    child: SDriverVerificationHeaderCopy(
                      category: category,
                      vehicle: vehicle,
                    ),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
}
