import 'package:client/data/rides/ride_models.dart';
import 'package:client/features/rides/controllers/ride_lifecycle_coordinator.dart';
import 'package:client/features/rides/domain/ride_lifecycle.dart';
import 'package:client/features/rides/orchestration/ride_realtime_orchestrator.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  group('SRideRealtimeOrchestrator', () {
    test('connects bidding only for matching hybrid rides', () {
      final orchestrator = SRideRealtimeOrchestrator();

      expect(
        orchestrator.shouldConnectBiddingSocket(
          SRideLifecycleSnapshot(
            rideId: 'ride-001',
            pricingMode: PricingMode.hybrid,
            status: RideStatus.matching,
          ),
        ),
        isTrue,
      );
      expect(
        orchestrator.shouldConnectBiddingSocket(
          SRideLifecycleSnapshot(
            rideId: 'ride-002',
            pricingMode: PricingMode.fixed,
            status: RideStatus.matching,
          ),
        ),
        isFalse,
      );
    });

    test('connects live passenger location only for assigned active rides', () {
      final orchestrator = SRideRealtimeOrchestrator();

      expect(
        orchestrator.shouldConnectPassengerLiveLocationSocket(
          SRideLifecycleSnapshot(
            rideId: 'ride-001',
            pricingMode: PricingMode.fixed,
            status: RideStatus.accepted,
            assignedDriverId: 'driver-001',
          ),
        ),
        isTrue,
      );
      expect(
        orchestrator.shouldConnectPassengerLiveLocationSocket(
          SRideLifecycleSnapshot(
            rideId: 'ride-002',
            pricingMode: PricingMode.fixed,
            status: RideStatus.matching,
          ),
        ),
        isFalse,
      );
    });

    test('suppresses driver requests and runs runtime for active rides', () {
      final orchestrator = SRideRealtimeOrchestrator();
      final snapshot = SRideLifecycleSnapshot.fromDriverState(
        rideId: 'ride-100',
        pricingMode: 'FIXED',
        status: 'IN_PROGRESS',
        assignedDriverId: 'driver-001',
      );

      expect(orchestrator.shouldRunDriverForegroundRuntime(snapshot), isTrue);
      expect(orchestrator.shouldSuppressDriverRequests(snapshot), isTrue);
      expect(
        orchestrator.shouldRefreshDriverMarketplace(
          isOnline: true,
          activeDriverRide: snapshot,
        ),
        isFalse,
      );
    });

    test('treats driver-assigned backend status as active runtime state', () {
      final orchestrator = SRideRealtimeOrchestrator();
      final snapshot = SRideLifecycleSnapshot.fromDriverState(
        rideId: 'ride-101',
        pricingMode: 'FIXED',
        status: 'DRIVER_ASSIGNED',
        assignedDriverId: 'driver-001',
      );

      expect(orchestrator.shouldRunDriverForegroundRuntime(snapshot), isTrue);
      expect(orchestrator.shouldSuppressDriverRequests(snapshot), isTrue);
    });

    test('recovers communication permission from coordinator lifecycle state',
        () {
      final coordinator = SRideLifecycleCoordinator();
      coordinator.syncPassengerSnapshot(
        const SRideLifecycleSnapshot(
          rideId: 'ride-communication',
          pricingMode: PricingMode.fixed,
          status: RideStatus.arriving,
          assignedDriverId: 'driver-001',
        ),
      );
      final orchestrator =
          SRideRealtimeOrchestrator(lifecycleCoordinator: coordinator);

      expect(
        orchestrator.shouldConnectCommunicationSocketForRide(
          'ride-communication',
        ),
        isTrue,
      );
      expect(
        orchestrator.shouldConnectCommunicationSocketForRide('unknown-ride'),
        isTrue,
      );
    });

    test('stops terminal ride sockets', () {
      final orchestrator = SRideRealtimeOrchestrator();
      final snapshot = const SRideLifecycleSnapshot(
        rideId: 'ride-terminal',
        pricingMode: PricingMode.fixed,
        status: RideStatus.completed,
        assignedDriverId: 'driver-001',
      );

      expect(
        orchestrator.shouldConnectPassengerRideLifecycleSocket(snapshot),
        isFalse,
      );
      expect(
        orchestrator.shouldConnectCommunicationSocket(snapshot),
        isFalse,
      );
      expect(orchestrator.shouldRunDriverForegroundRuntime(snapshot), isFalse);
    });
  });
}
