import 'package:flutter/material.dart';
import 'package:get/get.dart';

import '../../../common/widgets/appbar/appbar.dart';
import '../../../utils/constants/colors.dart';
import '../controllers/ride_communication_controller.dart';
import 'ride_call_screen.dart';
import 'widgets/communication_composer.dart';
import 'widgets/communication_header.dart';
import 'widgets/communication_message_list.dart';
import 'widgets/communication_unavailable_state.dart';
import 'widgets/incoming_call_banner.dart';

class SRideCommunicationScreen extends StatelessWidget {
  const SRideCommunicationScreen({
    super.key,
    required this.rideId,
    this.notificationCallId,
    this.openCallOnLoad = false,
  });

  final String rideId;
  final String? notificationCallId;
  final bool openCallOnLoad;

  @override
  Widget build(BuildContext context) {
    final controller = Get.put(
      SRideCommunicationController(
        rideId: rideId,
        notificationCallId: notificationCallId,
        openCallOnLoad: openCallOnLoad,
      ),
      tag: rideId,
    );

    return Scaffold(
      backgroundColor: SColors.primaryBackground,
      appBar: SAppBar(
        showBackArrow: true,
        title: Text(
          'Ride Chat',
          style: Theme.of(context).textTheme.titleLarge,
        ),
      ),
      body: SafeArea(
        child: Obx(
          () {
            if (controller.isLoading.value) {
              return const Center(child: CircularProgressIndicator());
            }
            if (controller.errorMessage.value.isNotEmpty &&
                controller.conversation.value == null) {
              return SCommunicationUnavailableState(
                message: controller.errorMessage.value,
                onRetry: controller.connect,
              );
            }
            if (controller.shouldPresentCallScreen.value) {
              WidgetsBinding.instance.addPostFrameCallback((_) {
                if (!controller.shouldPresentCallScreen.value) {
                  return;
                }
                controller.markCallScreenPresented();
                Get.to(() => SRideCallScreen(controller: controller));
              });
            }
            return Column(
              children: [
                SCommunicationHeader(
                  statusText: controller.callStatusText.value,
                  callEnabled: controller.conversation.value != null,
                  onCallPressed: () {
                    controller.startVoiceCall();
                    Get.to(() => SRideCallScreen(controller: controller));
                  },
                ),
                if (controller.activeCall.value != null &&
                    !controller.isInCall.value &&
                    controller.callStatusText.value == 'Incoming call')
                  SIncomingCallBanner(controller: controller),
                Expanded(
                  child: SCommunicationMessageList(controller: controller),
                ),
                SCommunicationComposer(controller: controller),
              ],
            );
          },
        ),
      ),
    );
  }
}
