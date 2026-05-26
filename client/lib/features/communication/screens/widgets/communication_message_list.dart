import 'package:flutter/material.dart';
import 'package:get/get.dart';

import '../../../../utils/constants/sizes.dart';
import '../../controllers/ride_communication_controller.dart';
import 'communication_message_bubble.dart';

class SCommunicationMessageList extends StatelessWidget {
  const SCommunicationMessageList({
    super.key,
    required this.controller,
  });

  final SRideCommunicationController controller;

  @override
  Widget build(BuildContext context) {
    return Obx(
      () => ListView.separated(
        reverse: false,
        padding: const EdgeInsets.all(SSizes.defaultSpace),
        itemCount: controller.messages.length,
        separatorBuilder: (_, __) => const SizedBox(height: SSizes.sm),
        itemBuilder: (context, index) {
          final message = controller.messages[index];
          return SCommunicationMessageBubble(
            message: message,
            isMine: controller.ownParticipantIds.contains(
              message.senderParticipantId,
            ),
            onPlayVoiceNote: () => controller.playVoiceNote(message),
          );
        },
      ),
    );
  }
}
