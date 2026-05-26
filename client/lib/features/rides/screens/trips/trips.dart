import 'package:flutter/material.dart';
import 'package:get/get.dart';

import '../../../../common/widgets/appbar/appbar.dart';
import '../../../../utils/constants/colors.dart';
import '../../../../utils/constants/sizes.dart';
import '../../../../utils/constants/texts.dart';
import '../../controllers/trips_controller.dart';
import 'screens/canceled/canceled.dart';
import 'screens/completed/completed.dart';
import 'screens/ongoing/ongoing.dart';
import 'screens/scheduled/scheduled.dart';
import 'widgets/trips_error_state.dart';
import 'widgets/trips_tab_bar.dart';

class TripsScreen extends StatelessWidget {
  const TripsScreen({super.key});

  static const List<String> _tabs = [
    STexts.tripsOngoing,
    STexts.tripsScheduled,
    STexts.tripsCanceled,
    STexts.tripsCompleted,
  ];

  @override
  Widget build(BuildContext context) {
    final controller = Get.put(STripsController());

    return Scaffold(
      backgroundColor: SColors.primaryBackground,
      appBar: SAppBar(
        title: Text(
          STexts.tripsTitle,
          style: Theme.of(context).textTheme.headlineMedium,
        ),
      ),
      body: Obx(
        () => RefreshIndicator(
          onRefresh: controller.refreshTrips,
          child: SingleChildScrollView(
            physics: const AlwaysScrollableScrollPhysics(),
            padding: const EdgeInsets.all(SSizes.defaultSpace),
            child: Column(
              children: [
                STripsTabBar(
                  tabs: _tabs,
                  selectedIndex: controller.selectedIndex.value,
                  onTabSelected: (index) =>
                      controller.selectedIndex.value = index,
                ),
                const SizedBox(height: SSizes.spaceBtnItems),
                if (controller.isLoading.value)
                  const Padding(
                    padding: EdgeInsets.only(top: SSizes.xl),
                    child: Center(child: CircularProgressIndicator()),
                  )
                else if (controller.errorMessage.value.isNotEmpty)
                  STripsErrorState(
                    message: controller.errorMessage.value,
                    onRetry: controller.loadTrips,
                  )
                else
                  IndexedStack(
                    index: controller.selectedIndex.value,
                    children: [
                      OngoingTripsScreen(
                        rides: controller.ridesFor(STripsFilter.ongoing),
                      ),
                      ScheduledTripsScreen(
                        rides: controller.ridesFor(STripsFilter.scheduled),
                      ),
                      CanceledTripsScreen(
                        rides: controller.ridesFor(STripsFilter.canceled),
                      ),
                      CompletedTripsScreen(
                        rides: controller.ridesFor(STripsFilter.completed),
                      ),
                    ],
                  ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
