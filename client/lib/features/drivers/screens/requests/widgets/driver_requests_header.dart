import 'package:flutter/material.dart';
import 'package:get/get.dart';

import '../../../../../utils/constants/colors.dart';
import '../../../../../utils/constants/sizes.dart';
import '../../../controllers/driver_requests_controller.dart';

class SDriverRequestsHeader extends StatelessWidget {
  const SDriverRequestsHeader({super.key, required this.controller});

  final SDriverRequestsController controller;

  @override
  Widget build(BuildContext context) {
    final textTheme = Theme.of(context).textTheme;

    return DecoratedBox(
      decoration: BoxDecoration(
        color: SColors.white,
        borderRadius: BorderRadius.circular(SSizes.cardRadiusMd),
        border: Border.all(color: SColors.borderSecondary),
      ),
      child: Padding(
        padding: const EdgeInsets.all(SSizes.md),
        child: Row(
          children: [
            Expanded(
              child: Obx(
                () => Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      controller.isOnline.value
                          ? 'You are Online'
                          : 'You are Offline',
                      style: textTheme.titleLarge?.copyWith(
                        fontWeight: FontWeight.w800,
                      ),
                    ),
                    const SizedBox(height: SSizes.xs),
                    Text(
                      controller.isOnline.value
                          ? '${controller.requests.length} requests nearby'
                          : 'Requests are paused',
                      style: textTheme.bodySmall?.copyWith(
                        color: SColors.textSecondary,
                      ),
                    ),
                  ],
                ),
              ),
            ),
            Obx(
              () => Switch(
                value: controller.isOnline.value,
                activeThumbColor: SColors.primary,
                onChanged: controller.isLoading.value
                    ? null
                    : (_) => controller.toggleOnline(),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
