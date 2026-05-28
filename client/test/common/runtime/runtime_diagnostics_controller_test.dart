import 'package:client/common/runtime/app_lifecycle_controller.dart';
import 'package:client/common/runtime/runtime_diagnostics_controller.dart';
import 'package:client/common/runtime/runtime_mode.dart';
import 'package:client/data/rides/ride_models.dart';
import 'package:client/features/rides/controllers/ride_lifecycle_coordinator.dart';
import 'package:client/features/rides/domain/ride_lifecycle.dart';
import 'package:flutter/widgets.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  test('builds a diagnostic snapshot from runtime and lifecycle state', () {
    final appLifecycle = SAppLifecycleController();
    final lifecycleCoordinator = SRideLifecycleCoordinator();
    const runtimeMode = SRuntimeModeConfig(useLocationDemoData: true);
    final diagnostics = SRuntimeDiagnosticsController(
      appLifecycleController: appLifecycle,
      lifecycleCoordinator: lifecycleCoordinator,
      runtimeModeConfig: runtimeMode,
    );

    appLifecycle.setStateForTest(AppLifecycleState.paused);
    lifecycleCoordinator.syncPassengerSnapshot(
      const SRideLifecycleSnapshot(
        rideId: 'passenger-ride',
        pricingMode: PricingMode.hybrid,
        status: RideStatus.matching,
      ),
    );
    lifecycleCoordinator.syncDriverSnapshot(
      const SRideLifecycleSnapshot(
        rideId: 'driver-ride',
        pricingMode: PricingMode.fixed,
        status: RideStatus.inProgress,
        assignedDriverId: 'driver-001',
      ),
    );
    diagnostics.updateForegroundRuntime(
      rideId: 'driver-ride',
      status: 'IN_PROGRESS',
      isRunning: true,
    );
    diagnostics.updateRealtimeChannel(
      SRuntimeRealtimeChannel.passengerRide,
      isConnected: true,
    );
    diagnostics.updateRealtimeChannel(
      SRuntimeRealtimeChannel.driverLocation,
      isConnected: false,
    );

    final snapshot = diagnostics.snapshot;

    expect(snapshot.appLifecycleState, AppLifecycleState.paused);
    expect(snapshot.locationDataSource, SRuntimeDataSource.demo);
    expect(snapshot.passengerRideId, 'passenger-ride');
    expect(snapshot.passengerRideStage, SRideLifecycleStage.matchingForDriver);
    expect(snapshot.driverRideId, 'driver-ride');
    expect(snapshot.driverRideStage, SRideLifecycleStage.tripInProgress);
    expect(snapshot.foregroundRuntimeRideId, 'driver-ride');
    expect(snapshot.isForegroundRuntimeRunning, isTrue);
    expect(
      snapshot.realtimeChannels[SRuntimeRealtimeChannel.passengerRide],
      isTrue,
    );
    expect(
      snapshot.realtimeChannels[SRuntimeRealtimeChannel.driverLocation],
      isFalse,
    );
  });
}
