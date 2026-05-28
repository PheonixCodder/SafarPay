import 'package:client/data/rides/ride_models.dart';
import 'package:client/features/location/data/ride_repository.dart';
import 'package:client/features/location/screens/ride_tracking/ride_tracking_screen.dart';
import 'package:client/features/rides/domain/ride_lifecycle.dart';
import 'package:client/features/rides/navigation/ride_navigation_destinations.dart';
import 'package:client/features/rides/navigation/ride_navigation_policy.dart';
import 'package:client/features/rides/screens/trips/screens/pending/fixed_ride_waiting_screen.dart';
import 'package:client/features/rides/screens/trips/screens/pending/pending_ride_matching_screen.dart';
import 'package:client/features/rides/screens/trips/screens/ride/ride.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  group('passenger ride destinations', () {
    test('builds hybrid matching destination', () {
      final ride = _ride(
        status: RideStatus.matching,
        pricingMode: PricingMode.hybrid,
      );

      final destination = sPassengerRideDestination(
        ride: ride,
        snapshot: SRideLifecycleSnapshot.fromSummary(ride),
      );

      expect(destination.kind, SRideDestinationKind.hybridMatching);
      expect(destination.buildPage(), isA<PendingRideMatchingScreen>());
    });

    test('builds fixed waiting destination', () {
      final ride = _ride(
        status: RideStatus.matching,
        pricingMode: PricingMode.fixed,
      );

      final destination = sPassengerRideDestination(
        ride: ride,
        snapshot: SRideLifecycleSnapshot.fromSummary(ride),
      );

      expect(destination.kind, SRideDestinationKind.fixedWaiting);
      expect(destination.buildPage(), isA<FixedRideWaitingScreen>());
    });

    test('builds live tracking destination for accepted rides', () {
      final ride = _ride(
        status: RideStatus.accepted,
        pricingMode: PricingMode.fixed,
        assignedDriverId: 'driver-001',
      );

      final destination = sPassengerRideDestination(
        ride: ride,
        snapshot: SRideLifecycleSnapshot.fromSummary(ride),
      );

      expect(destination.kind, SRideDestinationKind.liveTracking);
      expect(destination.buildPage(), isA<RideTrackingScreen>());
    });

    test('builds ride details destination for terminal rides', () {
      final ride = _ride(
        status: RideStatus.completed,
        pricingMode: PricingMode.fixed,
        assignedDriverId: 'driver-001',
      );

      final destination = sPassengerRideDestination(
        ride: ride,
        snapshot: SRideLifecycleSnapshot.fromSummary(ride),
      );

      expect(destination.kind, SRideDestinationKind.rideDetails);
      expect(destination.buildPage(), isA<RideDetailsScreen>());
    });
  });

  group('notification destinations', () {
    test('maps communication call intent to communication destination', () {
      final intent = sNotificationRouteIntentFromData({
        'deeplink': 'safarpay://communication/rides/ride-300',
        'notification_kind': 'communication_call',
        'call_id': 'call-300',
      })!;

      final destination = sDestinationFromNotificationIntent(intent)!;

      expect(destination.kind, SRideDestinationKind.communication);
      expect(destination.rideId, 'ride-300');
      expect(destination.callId, 'call-300');
      expect(destination.openCallOnLoad, isTrue);
    });

    test('maps driver request intent to driver requests destination', () {
      final intent = sNotificationRouteIntentFromData({
        'deeplink': 'safarpay://driver/requests/ride-301',
      })!;

      final destination = sDestinationFromNotificationIntent(intent)!;

      expect(destination.kind, SRideDestinationKind.driverRequests);
      expect(destination.requiresDriverMode, isTrue);
    });
  });

  group('legacy summary pricing resolution', () {
    test('hydrates missing pricing mode from full ride response', () async {
      final ride = _ride(
        status: RideStatus.matching,
        pricingMode: PricingMode.fixed,
        hasExplicitPricingMode: false,
      );

      final snapshot = await sResolveLifecycleSnapshotForRouting(
        ride: ride,
        repository: _RideRepositoryStub(PricingMode.hybrid),
      );

      expect(snapshot.pricingMode, PricingMode.hybrid);
      expect(snapshot.hasExplicitPricingMode, isTrue);
    });
  });
}

RideSummaryResponse _ride({
  required RideStatus status,
  required PricingMode pricingMode,
  bool hasExplicitPricingMode = true,
  String? assignedDriverId,
}) {
  return RideSummaryResponse(
    id: 'ride-001',
    passengerId: 'passenger-001',
    assignedDriverId: assignedDriverId,
    serviceType: ServiceType.cityRide,
    category: ServiceCategory.mini,
    pricingMode: pricingMode,
    hasExplicitPricingMode: hasExplicitPricingMode,
    status: status,
    passengerPaymentMethod: PassengerPaymentMethod.cash,
    paymentCollectionMode: PaymentCollectionMode.driverCollected,
    createdAt: DateTime.parse('2026-05-27T10:00:00Z'),
    scheduledAt: null,
    pickupStop: _stop('Pickup'),
    dropoffStop: _stop('Dropoff'),
  );
}

class _RideRepositoryStub extends SRideRepository {
  const _RideRepositoryStub(this.pricingMode);

  final PricingMode pricingMode;

  @override
  Future<Map<String, dynamic>> fetchRide(String rideId) async {
    return {
      'id': rideId,
      'passenger_id': 'passenger-001',
      'assigned_driver_id': null,
      'service_type': 'CITY_RIDE',
      'category': 'MINI',
      'pricing_mode': pricingMode.value,
      'status': 'MATCHING',
      'baseline_min_price': 200,
      'baseline_max_price': 250,
      'final_price': null,
      'passenger_payment_method': 'CASH',
      'passenger_payment_method_id': null,
      'payment_collection_mode': 'DRIVER_COLLECTED',
      'scheduled_at': null,
      'is_scheduled': false,
      'is_risky': false,
      'auto_accept_driver': false,
      'accepted_at': null,
      'completed_at': null,
      'cancelled_at': null,
      'cancellation_reason': null,
      'created_at': '2026-05-27T10:00:00Z',
      'stops': [_stop('Pickup').toJson(), _stop('Dropoff').toJson()],
      'proof_images': const [],
      'verification_codes': const [],
      'pickup_stop': _stop('Pickup').toJson(),
      'dropoff_stop': _stop('Dropoff').toJson(),
    };
  }
}

StopResponse _stop(String name) {
  return StopResponse(
    id: '$name-id',
    serviceRequestId: 'ride-001',
    sequenceOrder: name == 'Pickup' ? 1 : 2,
    stopType: name == 'Pickup' ? StopType.pickup : StopType.dropoff,
    latitude: 31.5,
    longitude: 74.3,
    placeName: name,
    addressLine1: '$name address',
    addressLine2: null,
    city: 'Lahore',
    state: null,
    country: 'Pakistan',
    postalCode: null,
    contactName: null,
    contactPhone: null,
    instructions: null,
    arrivedAt: null,
    completedAt: null,
  );
}
