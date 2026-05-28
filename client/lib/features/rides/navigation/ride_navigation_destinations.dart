import 'package:flutter/material.dart';
import 'package:get/get.dart';

import '../../../common/navigation/right_slide_page_route.dart';
import '../../../data/rides/ride_models.dart';
import '../../communication/screens/ride_communication_screen.dart';
import '../../drivers/screens/requests/requests.dart';
import '../../location/data/ride_repository.dart';
import '../../location/screens/ride_tracking/ride_tracking_screen.dart';
import '../domain/ride_lifecycle.dart';
import '../screens/trips/screens/pending/fixed_ride_waiting_screen.dart';
import '../screens/trips/screens/pending/pending_ride_matching_screen.dart';
import '../screens/trips/screens/ride/ride.dart';
import 'ride_navigation_policy.dart';

enum SRideDestinationKind {
  rideDetails,
  fixedWaiting,
  hybridMatching,
  liveTracking,
  communication,
  driverRequests,
}

class SRideDestination {
  const SRideDestination({
    required this.kind,
    this.rideId,
    this.ride,
    this.callId,
    this.openCallOnLoad = false,
    this.requiresDriverMode = false,
  });

  final SRideDestinationKind kind;
  final String? rideId;
  final RideSummaryResponse? ride;
  final String? callId;
  final bool openCallOnLoad;
  final bool requiresDriverMode;

  Widget buildPage() {
    return switch (kind) {
      SRideDestinationKind.rideDetails =>
        RideDetailsScreen(rideId: rideId!),
      SRideDestinationKind.fixedWaiting =>
        FixedRideWaitingScreen(ride: ride!),
      SRideDestinationKind.hybridMatching =>
        PendingRideMatchingScreen(rideId: rideId!),
      SRideDestinationKind.liveTracking =>
        RideTrackingScreen(rideId: rideId!),
      SRideDestinationKind.communication => SRideCommunicationScreen(
          rideId: rideId!,
          notificationCallId: callId,
          openCallOnLoad: openCallOnLoad,
        ),
      SRideDestinationKind.driverRequests => const SDriverRequestsScreen(),
    };
  }
}

Future<SRideLifecycleSnapshot> sResolveLifecycleSnapshotForRouting({
  required RideSummaryResponse ride,
  SRideRepository repository = const SRideRepository(),
}) async {
  var snapshot = SRideLifecycleSnapshot.fromSummary(ride);
  if (snapshot.hasExplicitPricingMode) return snapshot;

  try {
    final response = RideResponse.fromJson(await repository.fetchRide(ride.id));
    snapshot = snapshot.copyWith(
      pricingMode: response.pricingMode,
      hasExplicitPricingMode: true,
    );
  } catch (_) {}
  return snapshot;
}

SRideDestination sPassengerRideDestination({
  required RideSummaryResponse ride,
  required SRideLifecycleSnapshot snapshot,
}) {
  final decision = sResolvePassengerRideEntry(snapshot);
  return switch (decision.surface) {
    SRideNavigationSurface.hybridMatching => SRideDestination(
        kind: SRideDestinationKind.hybridMatching,
        rideId: ride.id,
      ),
    SRideNavigationSurface.fixedWaiting => SRideDestination(
        kind: SRideDestinationKind.fixedWaiting,
        ride: ride,
        rideId: ride.id,
      ),
    SRideNavigationSurface.liveTracking => SRideDestination(
        kind: SRideDestinationKind.liveTracking,
        rideId: ride.id,
      ),
    SRideNavigationSurface.rideDetails => SRideDestination(
        kind: SRideDestinationKind.rideDetails,
        rideId: ride.id,
      ),
  };
}

SRideDestination sRideTrackingDestination(String rideId) {
  return SRideDestination(
    kind: SRideDestinationKind.liveTracking,
    rideId: rideId,
  );
}

SRideDestination sRideCommunicationDestination({
  required String rideId,
  String? callId,
  bool openCallOnLoad = false,
}) {
  return SRideDestination(
    kind: SRideDestinationKind.communication,
    rideId: rideId,
    callId: callId,
    openCallOnLoad: openCallOnLoad,
  );
}

SRideDestination sDriverRequestsDestination({String? rideId}) {
  return SRideDestination(
    kind: SRideDestinationKind.driverRequests,
    rideId: rideId,
    requiresDriverMode: true,
  );
}

SRideDestination? sDestinationFromNotificationIntent(
  SNotificationRouteIntent intent,
) {
  return switch (intent.kind) {
    SNotificationRouteKind.communication => sRideCommunicationDestination(
        rideId: intent.rideId!,
        callId: intent.callId,
        openCallOnLoad: intent.presentAsCall,
      ),
    SNotificationRouteKind.driverRequests ||
    SNotificationRouteKind.driverActiveRide =>
      sDriverRequestsDestination(rideId: intent.rideId),
    SNotificationRouteKind.passengerRide =>
      sRideTrackingDestination(intent.rideId!),
  };
}

void sPushRideDestination(BuildContext context, SRideDestination destination) {
  Navigator.of(context).push(
    SRightSlidePageRoute(page: destination.buildPage()),
  );
}

void sReplaceWithRideDestination(
  BuildContext context,
  SRideDestination destination,
) {
  Navigator.of(context).pushReplacement(
    SRightSlidePageRoute(page: destination.buildPage()),
  );
}

Future<void> sOpenDestinationWithGet(
  SRideDestination destination, {
  Future<void> Function()? ensureDriverMode,
}) async {
  if (destination.requiresDriverMode && ensureDriverMode != null) {
    await ensureDriverMode();
  }
  Get.to(() => destination.buildPage());
}
