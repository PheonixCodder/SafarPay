import 'package:flutter/widgets.dart';
import 'package:get/get.dart';

import '../../features/rides/controllers/ride_lifecycle_coordinator.dart';
import '../../features/rides/domain/ride_lifecycle.dart';
import 'app_lifecycle_controller.dart';
import 'runtime_mode.dart';

enum SRuntimeRealtimeChannel {
  passengerRide,
  passengerLocation,
  passengerBidding,
  driverRide,
  driverLocation,
  driverBidding,
  communication,
}

class SRuntimeDiagnosticsSnapshot {
  const SRuntimeDiagnosticsSnapshot({
    required this.appLifecycleState,
    required this.locationDataSource,
    this.realtimeChannels = const {},
    this.passengerRideId,
    this.passengerRideStage,
    this.driverRideId,
    this.driverRideStage,
    this.foregroundRuntimeRideId,
    this.foregroundRuntimeStatus,
    this.isForegroundRuntimeRunning = false,
  });

  final AppLifecycleState appLifecycleState;
  final SRuntimeDataSource locationDataSource;
  final Map<SRuntimeRealtimeChannel, bool> realtimeChannels;
  final String? passengerRideId;
  final SRideLifecycleStage? passengerRideStage;
  final String? driverRideId;
  final SRideLifecycleStage? driverRideStage;
  final String? foregroundRuntimeRideId;
  final String? foregroundRuntimeStatus;
  final bool isForegroundRuntimeRunning;
}

class SRuntimeDiagnosticsController extends GetxController {
  SRuntimeDiagnosticsController({
    SAppLifecycleController? appLifecycleController,
    SRideLifecycleCoordinator? lifecycleCoordinator,
    SRuntimeModeConfig runtimeModeConfig = SRuntimeModeConfig.current,
  })  : _appLifecycleController =
            appLifecycleController ?? SAppLifecycleController.instance,
        _lifecycleCoordinator =
            lifecycleCoordinator ?? SRideLifecycleCoordinator.instance,
        _runtimeModeConfig = runtimeModeConfig;

  static SRuntimeDiagnosticsController get instance {
    if (Get.isRegistered<SRuntimeDiagnosticsController>()) {
      return Get.find<SRuntimeDiagnosticsController>();
    }
    return Get.put(SRuntimeDiagnosticsController());
  }

  final SAppLifecycleController _appLifecycleController;
  final SRideLifecycleCoordinator _lifecycleCoordinator;
  final SRuntimeModeConfig _runtimeModeConfig;
  final RxnString foregroundRuntimeRideId = RxnString();
  final RxnString foregroundRuntimeStatus = RxnString();
  final RxBool isForegroundRuntimeRunning = false.obs;
  final RxMap<SRuntimeRealtimeChannel, bool> realtimeChannels =
      <SRuntimeRealtimeChannel, bool>{}.obs;

  SRuntimeDiagnosticsSnapshot get snapshot {
    final passenger = _lifecycleCoordinator.passengerRide.value?.snapshot;
    final driver = _lifecycleCoordinator.driverRide.value?.snapshot;
    return SRuntimeDiagnosticsSnapshot(
      appLifecycleState: _appLifecycleController.state.value,
      locationDataSource: _runtimeModeConfig.locationDataSource,
      realtimeChannels: Map.unmodifiable(realtimeChannels),
      passengerRideId: passenger?.rideId,
      passengerRideStage: passenger?.stage,
      driverRideId: driver?.rideId,
      driverRideStage: driver?.stage,
      foregroundRuntimeRideId: foregroundRuntimeRideId.value,
      foregroundRuntimeStatus: foregroundRuntimeStatus.value,
      isForegroundRuntimeRunning: isForegroundRuntimeRunning.value,
    );
  }

  void updateForegroundRuntime({
    required String? rideId,
    required String? status,
    required bool isRunning,
  }) {
    foregroundRuntimeRideId.value = rideId;
    foregroundRuntimeStatus.value = status;
    isForegroundRuntimeRunning.value = isRunning;
  }

  void updateRealtimeChannel(
    SRuntimeRealtimeChannel channel, {
    required bool isConnected,
  }) {
    realtimeChannels[channel] = isConnected;
  }
}
