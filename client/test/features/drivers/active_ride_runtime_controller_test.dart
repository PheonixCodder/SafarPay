import 'package:client/features/drivers/data/active_ride_runtime_controller.dart';
import 'package:client/features/drivers/domain/active_ride_runtime_models.dart';
import 'package:client/common/runtime/runtime_diagnostics_controller.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  group('SActiveRideRuntimeController', () {
    test('starts runtime for an active driver ride', () async {
      final service = _RuntimeServiceSpy();
      final controller = _controller(service);

      await controller.syncActiveRide(
        driverId: 'driver-001',
        rideId: 'ride-001',
        status: 'ACCEPTED',
      );

      expect(service.started.length, 1);
      expect(service.started.single.driverId, 'driver-001');
      expect(service.started.single.rideId, 'ride-001');
      expect(service.stops, 0);
    });

    test('updates runtime when the same active ride status changes',
        () async {
      final service = _RuntimeServiceSpy();
      final controller = _controller(service);

      await controller.syncActiveRide(
        driverId: 'driver-001',
        rideId: 'ride-001',
        status: 'ACCEPTED',
      );
      await controller.syncActiveRide(
        driverId: 'driver-001',
        rideId: 'ride-001',
        status: 'IN_PROGRESS',
      );

      expect(service.started.length, 2);
      expect(service.started.map((config) => config.status), [
        'ACCEPTED',
        'IN_PROGRESS',
      ]);
      expect(service.stops, 1);
    });

    test('does not restart when same active ride status is already running',
        () async {
      final service = _RuntimeServiceSpy();
      final controller = _controller(service);

      await controller.syncActiveRide(
        driverId: 'driver-001',
        rideId: 'ride-001',
        status: 'ACCEPTED',
      );
      await controller.syncActiveRide(
        driverId: 'driver-001',
        rideId: 'ride-001',
        status: 'ACCEPTED',
      );

      expect(service.started.length, 1);
      expect(service.stops, 0);
    });

    test('restarts when the active ride changes', () async {
      final service = _RuntimeServiceSpy();
      final controller = _controller(service);

      await controller.syncActiveRide(
        driverId: 'driver-001',
        rideId: 'ride-001',
        status: 'ACCEPTED',
      );
      await controller.syncActiveRide(
        driverId: 'driver-001',
        rideId: 'ride-002',
        status: 'ACCEPTED',
      );

      expect(service.stops, 1);
      expect(service.started.map((config) => config.rideId), [
        'ride-001',
        'ride-002',
      ]);
    });

    test('stops runtime when there is no active ride', () async {
      final service = _RuntimeServiceSpy();
      final controller = _controller(service);

      await controller.syncActiveRide(
        driverId: 'driver-001',
        rideId: 'ride-001',
        status: 'ACCEPTED',
      );
      await controller.stop();

      expect(service.stops, 1);
      expect(controller.currentRideId, isNull);
    });

    test('does not start runtime for terminal ride statuses', () async {
      final service = _RuntimeServiceSpy();
      final controller = _controller(service);

      await controller.syncActiveRide(
        driverId: 'driver-001',
        rideId: 'ride-001',
        status: 'COMPLETED',
      );

      expect(service.started, isEmpty);
      expect(service.stops, 1);
    });

    test('publishes foreground runtime diagnostics', () async {
      final service = _RuntimeServiceSpy();
      final diagnostics = SRuntimeDiagnosticsController();
      final controller = _controller(service, diagnostics: diagnostics);

      await controller.syncActiveRide(
        driverId: 'driver-001',
        rideId: 'ride-001',
        status: 'IN_PROGRESS',
      );

      expect(diagnostics.snapshot.foregroundRuntimeRideId, 'ride-001');
      expect(diagnostics.snapshot.foregroundRuntimeStatus, 'IN_PROGRESS');
      expect(diagnostics.snapshot.isForegroundRuntimeRunning, isTrue);

      await controller.stop();

      expect(diagnostics.snapshot.foregroundRuntimeRideId, isNull);
      expect(diagnostics.snapshot.isForegroundRuntimeRunning, isFalse);
    });
  });
}

SActiveRideRuntimeController _controller(
  _RuntimeServiceSpy service, {
  SRuntimeDiagnosticsController? diagnostics,
}) {
  return SActiveRideRuntimeController(
    service: service,
    diagnosticsController: diagnostics,
    accessTokenProvider: () async => 'access-token',
    refreshTokenProvider: () async => 'refresh-token',
    locationBaseUrl: 'http://location.test/api/v1/location',
    authBaseUrl: 'http://auth.test/api/v1/auth',
  );
}

class _RuntimeServiceSpy implements SActiveRideRuntimeService {
  final List<SActiveRideRuntimeConfig> started = [];
  int stops = 0;

  @override
  Future<void> start(SActiveRideRuntimeConfig config) async {
    started.add(config);
  }

  @override
  Future<void> stop() async {
    stops += 1;
  }
}
