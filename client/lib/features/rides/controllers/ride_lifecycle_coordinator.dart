import 'package:get/get.dart';

import '../domain/ride_lifecycle.dart';

class SRideLifecycleState {
  const SRideLifecycleState(this.snapshot);

  final SRideLifecycleSnapshot snapshot;

  SRideLifecycleStage get stage => snapshot.stage;
  String get rideId => snapshot.rideId;
}

class SRideLifecycleCoordinator extends GetxController {
  static SRideLifecycleCoordinator get instance {
    if (Get.isRegistered<SRideLifecycleCoordinator>()) {
      return Get.find<SRideLifecycleCoordinator>();
    }
    return Get.put(SRideLifecycleCoordinator());
  }

  final Rxn<SRideLifecycleState> passengerRide = Rxn<SRideLifecycleState>();
  final Rxn<SRideLifecycleState> driverRide = Rxn<SRideLifecycleState>();

  void syncPassengerSnapshot(SRideLifecycleSnapshot snapshot) {
    passengerRide.value = SRideLifecycleState(snapshot);
  }

  void syncDriverSnapshot(SRideLifecycleSnapshot snapshot) {
    driverRide.value = SRideLifecycleState(snapshot);
  }

  SRideLifecycleSnapshot? snapshotForRide(String rideId) {
    final passenger = passengerRide.value?.snapshot;
    if (passenger?.rideId == rideId) return passenger;
    final driver = driverRide.value?.snapshot;
    if (driver?.rideId == rideId) return driver;
    return null;
  }

  void clearPassengerRide([String? rideId]) {
    if (rideId == null || passengerRide.value?.rideId == rideId) {
      passengerRide.value = null;
    }
  }

  void clearDriverRide([String? rideId]) {
    if (rideId == null || driverRide.value?.rideId == rideId) {
      driverRide.value = null;
    }
  }
}
