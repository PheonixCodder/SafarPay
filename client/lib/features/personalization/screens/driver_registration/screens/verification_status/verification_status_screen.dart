import 'package:client/common/navigation/right_slide_page_route.dart';
import 'package:client/features/personalization/screens/driver_registration/controllers/driver_verification_controller.dart';
import 'package:client/features/personalization/screens/driver_registration/models/driver_registration_models.dart';
import 'package:client/features/personalization/screens/driver_registration/screens/cnic/cnic_info_screen.dart';
import 'package:client/features/personalization/screens/driver_registration/screens/license/driver_license_screen.dart';
import 'package:client/features/personalization/screens/driver_registration/screens/selfie/selfie_with_license_screen.dart';
import 'package:client/features/personalization/screens/driver_registration/screens/vechicle_info/vehicle_info_screen.dart';
import 'package:client/features/personalization/screens/driver_registration/screens/verification_status/widgets/driver_verification_header.dart';
import 'package:client/features/personalization/screens/driver_registration/screens/verification_status/widgets/driver_verification_status_body.dart';
import 'package:client/utils/constants/colors.dart';
import 'package:client/utils/constants/sizes.dart';
import 'package:flutter/material.dart';

class DriverVerificationStatusScreen extends StatefulWidget {
  const DriverVerificationStatusScreen({
    super.key,
    required this.category,
    required this.vehicle,
  });

  final SDriverWorkCategory category;
  final SDriverVehicleOption vehicle;

  @override
  State<DriverVerificationStatusScreen> createState() =>
      _DriverVerificationStatusScreenState();
}

class _DriverVerificationStatusScreenState
    extends State<DriverVerificationStatusScreen> {
  late final SDriverVerificationController controller;

  @override
  void initState() {
    super.initState();
    controller = SDriverVerificationController()..loadStatus();
  }

  @override
  void dispose() {
    controller.dispose();
    super.dispose();
  }

  Future<void> _openStep(BuildContext context, SVerificationStep step) async {
    final Widget page = switch (step) {
      SVerificationStep.identity => CnicInfoScreen(
          category: widget.category,
          vehicle: widget.vehicle,
        ),
      SVerificationStep.license => DriverLicenseScreen(
          category: widget.category,
          vehicle: widget.vehicle,
        ),
      SVerificationStep.selfie => SelfieWithLicenseScreen(
          category: widget.category,
          vehicle: widget.vehicle,
        ),
      SVerificationStep.vehicle => VehicleInfoScreen(
          category: widget.category,
          vehicle: widget.vehicle,
        ),
    };

    final didSubmit = await Navigator.of(context).push<bool>(
      SRightSlidePageRoute(page: page),
    );
    if (didSubmit == true) {
      await controller.loadStatus();
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: SColors.primaryBackground,
      body: RefreshIndicator(
        color: SColors.primary,
        onRefresh: controller.loadStatus,
        child: CustomScrollView(
          slivers: [
            SliverToBoxAdapter(
              child: SDriverVerificationHeader(
                category: widget.category,
                vehicle: widget.vehicle,
              ),
            ),
            SliverToBoxAdapter(
              child: Padding(
                padding: const EdgeInsets.all(SSizes.defaultSpace),
                child: SDriverVerificationStatusBody(
                  controller: controller,
                  onStepTap: (step) => _openStep(context, step),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
