import 'package:flutter/material.dart';
import 'package:get/get.dart';

import '../../../utils/constants/colors.dart';
import '../screens/ride_communication_screen.dart';

class SRideCommunicationButton extends StatelessWidget {
  const SRideCommunicationButton({
    super.key,
    required this.rideId,
  });

  final String rideId;

  @override
  Widget build(BuildContext context) {
    return FloatingActionButton(
      heroTag: 'ride-communication-$rideId',
      backgroundColor: SColors.primary,
      foregroundColor: SColors.white,
      onPressed: () => Get.to(
        () => SRideCommunicationScreen(rideId: rideId),
      ),
      child: const Icon(Icons.chat_bubble_outline),
    );
  }
}
