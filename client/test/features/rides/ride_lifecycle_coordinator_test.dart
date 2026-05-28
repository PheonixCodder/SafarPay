import 'package:client/data/rides/ride_models.dart';
import 'package:client/features/rides/controllers/ride_lifecycle_coordinator.dart';
import 'package:client/features/rides/domain/ride_lifecycle.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  test('stores and clears passenger and driver lifecycle state', () {
    final coordinator = SRideLifecycleCoordinator();

    coordinator.syncPassengerSnapshot(
      SRideLifecycleSnapshot(
        rideId: 'ride-passenger',
        pricingMode: PricingMode.hybrid,
        status: RideStatus.matching,
      ),
    );
    coordinator.syncDriverSnapshot(
      SRideLifecycleSnapshot(
        rideId: 'ride-driver',
        pricingMode: PricingMode.fixed,
        status: RideStatus.inProgress,
        assignedDriverId: 'driver-001',
      ),
    );

    expect(
      coordinator.passengerRide.value?.stage,
      SRideLifecycleStage.matchingForDriver,
    );
    expect(
      coordinator.driverRide.value?.stage,
      SRideLifecycleStage.tripInProgress,
    );

    coordinator.clearPassengerRide();
    coordinator.clearDriverRide();

    expect(coordinator.passengerRide.value, isNull);
    expect(coordinator.driverRide.value, isNull);
  });
}
