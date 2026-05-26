import 'package:flutter/material.dart';
import 'package:get/get.dart';

import '../../../../utils/constants/colors.dart';
import '../../../../utils/constants/sizes.dart';
import '../../controllers/ride_communication_controller.dart';

class SCommunicationComposer extends StatelessWidget {
  const SCommunicationComposer({
    super.key,
    required this.controller,
  });

  final SRideCommunicationController controller;

  @override
  Widget build(BuildContext context) {
    final textController = TextEditingController(text: controller.draft.value);

    return DecoratedBox(
      decoration: const BoxDecoration(color: SColors.white),
      child: SafeArea(
        top: false,
        child: Padding(
          padding: const EdgeInsets.all(SSizes.sm),
          child: Row(
            children: [
              IconButton(
                onPressed: controller.sendImage,
                icon: const Icon(Icons.attach_file),
              ),
              Expanded(
                child: TextField(
                  controller: textController,
                  minLines: 1,
                  maxLines: 4,
                  onChanged: controller.updateDraft,
                  decoration: InputDecoration(
                    hintText: 'Message',
                    filled: true,
                    fillColor: SColors.lightContainer,
                    border: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(SSizes.radiusFull),
                      borderSide: BorderSide.none,
                    ),
                    contentPadding: const EdgeInsets.symmetric(
                      horizontal: SSizes.md,
                      vertical: SSizes.sm,
                    ),
                  ),
                ),
              ),
              Obx(
                () => IconButton(
                  onPressed: controller.draft.value.trim().isEmpty
                      ? controller.toggleRecording
                      : controller.sendText,
                  color: controller.isRecording.value
                      ? SColors.error
                      : SColors.primary,
                  icon: Icon(
                    controller.draft.value.trim().isEmpty
                        ? controller.isRecording.value
                            ? Icons.stop_circle
                            : Icons.mic
                        : Icons.send,
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
