import 'package:client/features/personalization/screens/driver_registration/models/driver_registration_models.dart';
import 'package:client/utils/constants/colors.dart';
import 'package:client/utils/constants/sizes.dart';
import 'package:client/utils/constants/texts.dart';
import 'package:client/utils/helpers/helpers.dart';
import 'package:flutter/material.dart';
import 'package:iconsax/iconsax.dart';

class SDriverVerificationOverallStatusNotice extends StatelessWidget {
  const SDriverVerificationOverallStatusNotice({
    super.key,
    required this.status,
  });

  final SVerificationOverallStatus status;

  @override
  Widget build(BuildContext context) {
    final textTheme = Theme.of(context).textTheme;
    final data = _noticeData(status);

    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(SSizes.md),
      decoration: BoxDecoration(
        color: SHelperFunctions.withOpacity(data.color, SOpacities.tinted),
        borderRadius: BorderRadius.circular(SSizes.cardRadiusLg),
        border: Border.all(
          color: SHelperFunctions.withOpacity(data.color, SOpacities.border),
        ),
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Icon(data.icon, color: data.color, size: SSizes.iconMd),
          const SizedBox(width: SSizes.md),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  data.title,
                  style: textTheme.titleMedium?.copyWith(
                    color: SColors.textPrimary,
                    fontWeight: FontWeight.w800,
                  ),
                ),
                const SizedBox(height: SSizes.xs),
                Text(
                  data.message,
                  style: textTheme.bodyMedium?.copyWith(
                    color: SColors.textSecondary,
                    height: 1.35,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  _NoticeData _noticeData(SVerificationOverallStatus status) {
    return switch (status) {
      SVerificationOverallStatus.underReview => const _NoticeData(
          icon: Iconsax.timer_1,
          color: SColors.warning,
          title: STexts.driverVerificationUnderReviewTitle,
          message: STexts.driverVerificationUnderReviewMessage,
        ),
      SVerificationOverallStatus.verified => const _NoticeData(
          icon: Iconsax.tick_circle,
          color: SColors.success,
          title: STexts.driverVerificationVerifiedTitle,
          message: STexts.driverVerificationVerifiedMessage,
        ),
      SVerificationOverallStatus.rejected => const _NoticeData(
          icon: Iconsax.close_circle,
          color: SColors.error,
          title: STexts.driverVerificationRejectedTitle,
          message: STexts.driverVerificationRejectedMessage,
        ),
      SVerificationOverallStatus.pending => const _NoticeData(
          icon: Iconsax.document_upload,
          color: SColors.primary,
          title: STexts.driverVerificationPendingTitle,
          message: STexts.driverVerificationPendingMessage,
        ),
      SVerificationOverallStatus.notStarted => const _NoticeData(
          icon: Iconsax.document_text,
          color: SColors.primary,
          title: STexts.driverVerificationNotStartedTitle,
          message: STexts.driverVerificationNotStartedMessage,
        ),
    };
  }
}

class _NoticeData {
  const _NoticeData({
    required this.icon,
    required this.color,
    required this.title,
    required this.message,
  });

  final IconData icon;
  final Color color;
  final String title;
  final String message;
}
