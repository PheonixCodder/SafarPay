import 'package:get/get.dart';

import '../controllers/ride_lifecycle_coordinator.dart';
import '../domain/ride_lifecycle.dart';

class SRideRealtimeOrchestrator extends GetxController {
  SRideRealtimeOrchestrator({
    SRideLifecycleCoordinator? lifecycleCoordinator,
  }) : _lifecycleCoordinator =
            lifecycleCoordinator ?? SRideLifecycleCoordinator.instance;

  static SRideRealtimeOrchestrator get instance {
    if (Get.isRegistered<SRideRealtimeOrchestrator>()) {
      return Get.find<SRideRealtimeOrchestrator>();
    }
    return Get.put(SRideRealtimeOrchestrator());
  }

  final SRideLifecycleCoordinator _lifecycleCoordinator;

  bool shouldConnectPassengerRideLifecycleSocket(
    SRideLifecycleSnapshot snapshot,
  ) {
    return !_isTerminal(snapshot.stage);
  }

  bool shouldConnectPassengerLiveLocationSocket(
    SRideLifecycleSnapshot snapshot,
  ) {
    if (!snapshot.hasAssignedDriver) return false;
    return _isAssignedOrActive(snapshot.stage);
  }

  bool shouldConnectBiddingSocket(SRideLifecycleSnapshot snapshot) {
    return snapshot.isBidDriven &&
        snapshot.stage == SRideLifecycleStage.matchingForDriver;
  }

  bool shouldConnectCommunicationSocket(SRideLifecycleSnapshot snapshot) {
    return _isAssignedOrActive(snapshot.stage);
  }

  bool shouldConnectCommunicationSocketForRide(String rideId) {
    final snapshot = _lifecycleCoordinator.snapshotForRide(rideId);
    if (snapshot == null) return true;
    return shouldConnectCommunicationSocket(snapshot);
  }

  bool shouldRunDriverForegroundRuntime(SRideLifecycleSnapshot snapshot) {
    return _isAssignedOrActive(snapshot.stage);
  }

  bool shouldSuppressDriverRequests(SRideLifecycleSnapshot? activeDriverRide) {
    if (activeDriverRide == null) return false;
    return !_isTerminal(activeDriverRide.stage);
  }

  bool shouldRefreshDriverMarketplace({
    required bool isOnline,
    required SRideLifecycleSnapshot? activeDriverRide,
  }) {
    return isOnline && !shouldSuppressDriverRequests(activeDriverRide);
  }
}

bool _isAssignedOrActive(SRideLifecycleStage stage) {
  return stage == SRideLifecycleStage.driverAssigned ||
      stage == SRideLifecycleStage.driverEnRouteToPickup ||
      stage == SRideLifecycleStage.driverArrivedAtPickup ||
      stage == SRideLifecycleStage.tripInProgress;
}

bool _isTerminal(SRideLifecycleStage stage) {
  return stage == SRideLifecycleStage.completed ||
      stage == SRideLifecycleStage.cancelled;
}
