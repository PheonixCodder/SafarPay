import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'package:iconsax/iconsax.dart';

import '../../../../../utils/constants/colors.dart';
import '../data/driver_verification_demo_data.dart';
import '../models/driver_registration_models.dart';
import '../repositories/driver_verification_repository.dart';

class SVerificationStepViewData {
  const SVerificationStepViewData({
    required this.step,
    required this.title,
    required this.group,
    required this.icon,
    required this.iconColor,
    required this.isEnabled,
    this.supportingText,
  });

  final SVerificationStep step;
  final String title;
  final SRequirementGroupStatus group;
  final IconData icon;
  final Color iconColor;
  final bool isEnabled;
  final String? supportingText;
}

class SDriverVerificationController extends GetxController {
  SDriverVerificationController({
    SDriverVerificationRepository repository =
        const SDriverVerificationRepository(),
  }) : _repository = repository;

  final SDriverVerificationRepository _repository;
  final RxBool isLoading = true.obs;
  final RxBool isSubmittingReview = false.obs;
  final RxnString errorMessage = RxnString();
  final Rxn<SVerificationStatusResponse> status = Rxn();

  @override
  void onInit() {
    super.onInit();
    loadStatus();
  }

  Future<void> loadStatus() async {
    isLoading.value = true;
    errorMessage.value = null;

    try {
      status.value = await _repository.getMyVerificationStatus();
    } catch (error) {
      errorMessage.value = error.toString();
    } finally {
      isLoading.value = false;
    }
  }

  bool get canSubmitForReview {
    final current = status.value;
    if (current == null) return false;

    return current.overallStatus == SVerificationOverallStatus.pending &&
        current.identity.status == SVerificationGroupStatus.pending &&
        current.license.status == SVerificationGroupStatus.pending &&
        current.selfie.status == SVerificationGroupStatus.pending &&
        current.vehicle.status == SVerificationGroupStatus.pending;
  }

  Future<void> submitForReview() async {
    if (!canSubmitForReview || isSubmittingReview.value) return;

    isSubmittingReview.value = true;
    errorMessage.value = null;

    try {
      await _repository.submitForReview();
      status.value = SVerificationStatusResponse.fromJson(
        SDriverVerificationDemoData.responseFor(
          SDriverVerificationDemoScenario.underReview,
        ),
      );
    } catch (error) {
      errorMessage.value = error.toString();
    } finally {
      isSubmittingReview.value = false;
    }
  }

  List<SVerificationStepViewData> stepCards() {
    final current = status.value;
    if (current == null) return const [];

    return [
      _viewDataFor(
        current,
        SVerificationStep.identity,
        'CNIC Info',
      ),
      _viewDataFor(
        current,
        SVerificationStep.license,
        "Driver's License",
      ),
      _viewDataFor(
        current,
        SVerificationStep.selfie,
        'Selfie with License',
      ),
      _viewDataFor(
        current,
        SVerificationStep.vehicle,
        'Vehicle Info',
      ),
    ];
  }

  SVerificationStepViewData _viewDataFor(
    SVerificationStatusResponse response,
    SVerificationStep step,
    String title,
  ) {
    final group = response.groupFor(step);
    final blocksEdits =
        response.overallStatus == SVerificationOverallStatus.underReview ||
            response.overallStatus == SVerificationOverallStatus.verified;

    return SVerificationStepViewData(
      step: step,
      title: title,
      group: group,
      icon: _iconFor(group.status, response.overallStatus),
      iconColor: _iconColorFor(group.status, response.overallStatus),
      isEnabled: !blocksEdits,
      supportingText: _supportingTextFor(group, response.overallStatus),
    );
  }

  IconData _iconFor(
    SVerificationGroupStatus groupStatus,
    SVerificationOverallStatus overallStatus,
  ) {
    if (overallStatus == SVerificationOverallStatus.underReview) {
      return Iconsax.timer_1;
    }
    if (overallStatus == SVerificationOverallStatus.verified ||
        groupStatus == SVerificationGroupStatus.verified) {
      return Iconsax.tick_circle;
    }
    return switch (groupStatus) {
      SVerificationGroupStatus.rejected => Iconsax.close_circle,
      SVerificationGroupStatus.pending => Iconsax.clock,
      SVerificationGroupStatus.notSubmitted => Iconsax.record_circle,
      SVerificationGroupStatus.verified => Iconsax.tick_circle,
    };
  }

  Color _iconColorFor(
    SVerificationGroupStatus groupStatus,
    SVerificationOverallStatus overallStatus,
  ) {
    if (overallStatus == SVerificationOverallStatus.underReview) {
      return SColors.warning;
    }
    if (overallStatus == SVerificationOverallStatus.verified ||
        groupStatus == SVerificationGroupStatus.verified) {
      return SColors.success;
    }
    return switch (groupStatus) {
      SVerificationGroupStatus.rejected => SColors.error,
      SVerificationGroupStatus.pending => SColors.warning,
      SVerificationGroupStatus.notSubmitted => SColors.secondary,
      SVerificationGroupStatus.verified => SColors.success,
    };
  }

  String? _supportingTextFor(
    SRequirementGroupStatus group,
    SVerificationOverallStatus overallStatus,
  ) {
    if (overallStatus == SVerificationOverallStatus.underReview) {
      return 'Under review';
    }
    if (overallStatus == SVerificationOverallStatus.verified) {
      return 'Approved';
    }
    if (group.status == SVerificationGroupStatus.rejected) {
      return group.rejectionReason ?? 'Needs correction';
    }
    if (group.status == SVerificationGroupStatus.pending) {
      return 'Submitted';
    }
    return null;
  }
}
