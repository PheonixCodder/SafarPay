import 'package:client/common/navigation/right_slide_page_route.dart';
import 'package:client/common/widgets/appbar/appbar.dart';
import 'package:client/features/personalization/screens/driver_registration/models/driver_registration_models.dart';
import 'package:client/features/personalization/screens/driver_registration/screens/vehicle_selection/vehicle_selection_screen.dart';
import 'package:client/features/personalization/screens/driver_registration/widgets/driver_registration_option_tile.dart';
import 'package:client/utils/constants/colors.dart';
import 'package:client/utils/constants/sizes.dart';
import 'package:client/utils/constants/texts.dart';
import 'package:flutter/material.dart';

class DriverRegistrationScreen extends StatelessWidget {
  const DriverRegistrationScreen({super.key});

  void _openVehicleSelection(
    BuildContext context,
    SDriverWorkCategory category,
  ) {
    Navigator.of(context).push(
      SRightSlidePageRoute(
        page: DriverVehicleSelectionScreen(category: category),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final textTheme = Theme.of(context).textTheme;

    return Scaffold(
      backgroundColor: SColors.primaryBackground,
      appBar: SAppBar(
        showBackArrow: true,
        title: Text(
          STexts.driverRegistrationTitle,
          style: textTheme.headlineSmall?.copyWith(
            color: SColors.textPrimary,
            fontWeight: FontWeight.w800,
          ),
        ),
      ),
      body: SafeArea(
        child: ListView.separated(
          padding: const EdgeInsets.all(SSizes.defaultSpace),
          itemCount: SDriverRegistrationCatalog.categories.length,
          separatorBuilder: (context, index) =>
              const SizedBox(height: SSizes.md),
          itemBuilder: (context, index) {
            final category = SDriverRegistrationCatalog.categories[index];
            return SDriverRegistrationOptionTile(
              title: category.title,
              subtitle: category.subtitle,
              image: category.image,
              onTap: () => _openVehicleSelection(context, category),
            );
          },
        ),
      ),
    );
  }
}
