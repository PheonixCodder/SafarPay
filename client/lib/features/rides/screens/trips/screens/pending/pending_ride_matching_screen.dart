import 'package:flutter/material.dart';
import 'package:get/get.dart';

import '../../../../../../common/widgets/appbar/appbar.dart';
import '../../../../../../features/location/controllers/ride_search_controller.dart';
import '../../../../../../features/location/screens/ride_search/widgets/matching_ride_offers_content.dart';
import '../../../../../../features/rides/navigation/ride_navigation_destinations.dart';
import '../../../../../../utils/constants/colors.dart';
import '../../../../../../utils/constants/sizes.dart';

class PendingRideMatchingScreen extends StatefulWidget {
  const PendingRideMatchingScreen({
    super.key,
    required this.rideId,
  });

  final String rideId;

  @override
  State<PendingRideMatchingScreen> createState() =>
      _PendingRideMatchingScreenState();
}

class _PendingRideMatchingScreenState extends State<PendingRideMatchingScreen> {
  late final String _tag;
  late final SRideSearchController _controller;

  @override
  void initState() {
    super.initState();
    _tag = 'pending-ride-${widget.rideId}';
    _controller = Get.put(SRideSearchController(), tag: _tag);
    WidgetsBinding.instance.addPostFrameCallback((_) {
      _controller.resumeMatchingForRide(widget.rideId);
    });
  }

  @override
  void dispose() {
    if (Get.isRegistered<SRideSearchController>(tag: _tag)) {
      Get.delete<SRideSearchController>(tag: _tag, force: true);
    }
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: SColors.primaryBackground,
      appBar: const SAppBar(
        showBackArrow: true,
        title: Text('Finding driver'),
      ),
      body: SafeArea(
        child: Obx(
          () {
            final isInitialLoad = _controller.isLoading.value &&
                _controller.biddingSessionId.value.isEmpty &&
                _controller.driverBids.isEmpty;

            if (isInitialLoad) {
              return const Center(child: CircularProgressIndicator());
            }

            return RefreshIndicator(
              onRefresh: () => _controller.resumeMatchingForRide(widget.rideId),
              child: ListView(
                physics: const AlwaysScrollableScrollPhysics(),
                padding: const EdgeInsets.all(SSizes.defaultSpace),
                children: [
                  SMatchingRideOffersContent(
                    controller: _controller,
                    onAcceptedRideTrackingRequested: _openTracking,
                  ),
                  if (_controller.errorMessage.value.isNotEmpty) ...[
                    const SizedBox(height: SSizes.md),
                    Text(
                      _controller.errorMessage.value,
                      style: Theme.of(context).textTheme.bodySmall?.copyWith(
                            color: SColors.error,
                          ),
                    ),
                  ],
                ],
              ),
            );
          },
        ),
      ),
    );
  }

  void _openTracking(String rideId) {
    sReplaceWithRideDestination(
      context,
      sRideTrackingDestination(rideId),
    );
  }
}
