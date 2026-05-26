import 'package:flutter/material.dart';
import 'package:get/get.dart';

import '../../../../utils/constants/colors.dart';
import '../../../../utils/constants/sizes.dart';
import '../../controllers/ride_communication_controller.dart';
import '../ride_call_screen.dart';

class SIncomingCallBanner extends StatelessWidget {
  const SIncomingCallBanner({
    super.key,
    required this.controller,
  });

  final SRideCommunicationController controller;

  @override
  Widget build(BuildContext context) {
    return Material(
      color: SColors.primary,
      child: Padding(
        padding: const EdgeInsets.all(SSizes.md),
        child: Row(
          children: [
            const Icon(Icons.call, color: SColors.white),
            const SizedBox(width: SSizes.sm),
            Expanded(
              child: Text(
                'Incoming ride call',
                style: Theme.of(context).textTheme.titleSmall?.copyWith(
                      color: SColors.white,
                      fontWeight: FontWeight.w800,
                    ),
              ),
            ),
            TextButton(
              onPressed: controller.rejectIncomingCall,
              child: const Text(
                'Decline',
                style: TextStyle(color: SColors.white),
              ),
            ),
            ElevatedButton(
              onPressed: () async {
                await controller.acceptIncomingCall();
                Get.to(() => SRideCallScreen(controller: controller));
              },
              child: const Text('Answer'),
            ),
          ],
        ),
      ),
    );
  }
}
