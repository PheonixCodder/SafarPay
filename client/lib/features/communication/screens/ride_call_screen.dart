import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'package:iconsax/iconsax.dart';

import '../../../utils/constants/colors.dart';
import '../../../utils/constants/sizes.dart';
import '../controllers/ride_communication_controller.dart';
import 'widgets/call_control_button.dart';

class SRideCallScreen extends StatelessWidget {
  const SRideCallScreen({
    super.key,
    required this.controller,
  });

  final SRideCommunicationController controller;

  @override
  Widget build(BuildContext context) {
    final textTheme = Theme.of(context).textTheme;

    return Scaffold(
      backgroundColor: SColors.pureBlack,
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(SSizes.defaultSpace),
          child: Obx(
            () => Column(
              children: [
                Row(
                  children: [
                    IconButton(
                      onPressed: () => Get.back<void>(),
                      color: SColors.white,
                      icon: const Icon(Iconsax.arrow_left),
                    ),
                    const Spacer(),
                    Container(
                      padding: const EdgeInsets.symmetric(
                        horizontal: SSizes.md,
                        vertical: SSizes.xs,
                      ),
                      decoration: BoxDecoration(
                        color: SColors.black,
                        borderRadius: BorderRadius.circular(SSizes.radiusFull),
                      ),
                      child: Text(
                        controller.callStatusText.value,
                        style: textTheme.labelLarge?.copyWith(
                          color: SColors.white,
                          fontWeight: FontWeight.w800,
                        ),
                      ),
                    ),
                  ],
                ),
                const Spacer(),
                Container(
                  width: 112,
                  height: 112,
                  decoration: BoxDecoration(
                    color: SColors.primary,
                    borderRadius: BorderRadius.circular(SSizes.radiusFull),
                    border: Border.all(color: SColors.white, width: 3),
                  ),
                  child: Center(
                    child: Text(
                      'SP',
                      style: textTheme.headlineMedium?.copyWith(
                        color: SColors.white,
                        fontWeight: FontWeight.w900,
                      ),
                    ),
                  ),
                ),
                const SizedBox(height: SSizes.lg),
                Text(
                  'Ride voice call',
                  style: textTheme.headlineSmall?.copyWith(
                    color: SColors.white,
                    fontWeight: FontWeight.w900,
                  ),
                ),
                const SizedBox(height: SSizes.sm),
                Text(
                  'Audio stays inside this ride conversation.',
                  textAlign: TextAlign.center,
                  style: textTheme.bodyMedium?.copyWith(
                    color: SColors.textWhite,
                  ),
                ),
                const Spacer(),
                if (controller.activeCall.value != null &&
                    !controller.isInCall.value &&
                    controller.callStatusText.value == 'Incoming call') ...[
                  Row(
                    children: [
                      Expanded(
                        child: OutlinedButton.icon(
                          onPressed: controller.rejectIncomingCall,
                          icon: const Icon(Icons.call_end),
                          label: const Text('Decline'),
                        ),
                      ),
                      const SizedBox(width: SSizes.md),
                      Expanded(
                        child: ElevatedButton.icon(
                          onPressed: controller.acceptIncomingCall,
                          icon: const Icon(Iconsax.call),
                          label: const Text('Accept'),
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: SSizes.lg),
                ],
                Row(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    SCallControlButton(
                      icon:
                          controller.isMuted.value ? Icons.mic_off : Icons.mic,
                      label: controller.isMuted.value ? 'Muted' : 'Mute',
                      onPressed: controller.toggleMute,
                    ),
                    const SizedBox(width: SSizes.xl),
                    SCallControlButton(
                      icon: Icons.call_end,
                      label: 'End',
                      color: SColors.error,
                      onPressed: () async {
                        await controller.endCall();
                        if (Get.isOverlaysOpen) return;
                        Get.back<void>();
                      },
                    ),
                  ],
                ),
                const SizedBox(height: SSizes.lg),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
