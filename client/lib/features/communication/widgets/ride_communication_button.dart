import 'package:flutter/material.dart';

import '../../rides/navigation/ride_navigation_destinations.dart';
import '../../../utils/constants/colors.dart';

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
      onPressed: () => sOpenDestinationWithGet(
        sRideCommunicationDestination(rideId: rideId),
      ),
      child: const Icon(Icons.chat_bubble_outline),
    );
  }
}
