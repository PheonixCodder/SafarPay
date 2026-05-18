import 'package:client/common/navigation/right_slide_page_route.dart';
import 'package:client/common/widgets/appbar/appbar.dart';
import 'package:client/features/personalization/screens/driver_registration/models/driver_registration_models.dart';
import 'package:client/features/personalization/screens/driver_registration/screens/verification_status/verification_status_screen.dart';
import 'package:client/features/personalization/screens/driver_registration/widgets/driver_registration_option_tile.dart';
import 'package:client/utils/constants/colors.dart';
import 'package:client/utils/constants/sizes.dart';
import 'package:client/utils/constants/texts.dart';
import 'package:flutter/material.dart';

class DriverVehicleSelectionScreen extends StatelessWidget {
  const DriverVehicleSelectionScreen({
    super.key,
    required this.category,
  });

  final SDriverWorkCategory category;

  void _openVerificationStatus(
    BuildContext context,
    SDriverVehicleOption vehicle,
  ) {
    Navigator.of(context).push(
      SRightSlidePageRoute(
        page: DriverVerificationStatusScreen(
          category: category,
          vehicle: vehicle,
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final vehicles = SDriverRegistrationCatalog.vehiclesFor(category.type);
    final textTheme = Theme.of(context).textTheme;

    return Scaffold(
      backgroundColor: SColors.primaryBackground,
      appBar: SAppBar(
        showBackArrow: true,
        title: Text(
          STexts.driverVehicleSelectionTitle,
          style: textTheme.headlineSmall?.copyWith(
            color: SColors.textPrimary,
            fontWeight: FontWeight.w800,
          ),
        ),
      ),
      body: SafeArea(
        child: ListView.separated(
          padding: const EdgeInsets.all(SSizes.defaultSpace),
          itemCount: vehicles.length,
          separatorBuilder: (context, index) =>
              const SizedBox(height: SSizes.lg),
          itemBuilder: (context, index) {
            final vehicle = vehicles[index];
            return SDriverRegistrationOptionTile(
              title: vehicle.title,
              image: vehicle.image,
              compact: true,
              onTap: () => _openVerificationStatus(context, vehicle),
            );
          },
        ),
      ),
    );
  }
}
