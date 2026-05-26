import 'package:flutter/material.dart';
import 'package:get/get.dart';

import '../../../../common/widgets/appbar/appbar.dart';
import '../../../../utils/constants/colors.dart';
import '../../../../utils/constants/sizes.dart';
import '../../../../utils/constants/texts.dart';
import '../../controllers/driver_requests_controller.dart';
import 'widgets/active_ride_view.dart';
import 'widgets/driver_request_list.dart';
import 'widgets/driver_requests_header.dart';
import 'widgets/incoming_request_sheet.dart';
import 'widgets/requests_empty_state.dart';

class SDriverRequestsScreen extends StatelessWidget {
  const SDriverRequestsScreen({super.key, this.controller});

  final SDriverRequestsController? controller;

  @override
  Widget build(BuildContext context) {
    final requestsController = Get.put(
      controller ?? SDriverRequestsController(),
    );

    return Scaffold(
      backgroundColor: SColors.primaryBackground,
      appBar: SAppBar(
        title: Text(
          STexts.driverNavRequests,
          style: Theme.of(context).textTheme.headlineMedium,
        ),
      ),
      body: Obx(() {
        final activeRide = requestsController.activeRide.value;
        if (activeRide != null) {
          return SActiveRideView(
            controller: requestsController,
            ride: activeRide,
          );
        }

        return Stack(
          children: [
            RefreshIndicator(
              color: SColors.primary,
              onRefresh: requestsController.refreshAll,
              child: ListView(
                padding: const EdgeInsets.all(SSizes.defaultSpace),
                children: [
                  SDriverRequestsHeader(controller: requestsController),
                  const SizedBox(height: SSizes.spaceBtwSections),
                  if (!requestsController.isOnline.value)
                    const SRequestsEmptyState(
                      title: 'You are offline',
                      subtitle: 'Go online to receive nearby ride requests.',
                    )
                  else if (requestsController.requests.isEmpty)
                    const SRequestsEmptyState(
                      title: 'No nearby requests',
                      subtitle: 'New passenger requests will appear here.',
                    )
                  else
                    SDriverRequestList(controller: requestsController),
                ],
              ),
            ),
            if (requestsController.incomingRequest.value != null)
              SIncomingRequestSheet(controller: requestsController),
          ],
        );
      }),
    );
  }
}
