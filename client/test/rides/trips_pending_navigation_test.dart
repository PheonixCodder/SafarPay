import 'package:client/data/rides/ride_models.dart';
import 'package:client/features/location/data/ride_repository.dart';
import 'package:client/features/location/screens/ride_tracking/ride_tracking_screen.dart';
import 'package:client/features/rides/controllers/trips_controller.dart';
import 'package:client/features/rides/screens/trips/screens/pending/fixed_ride_waiting_screen.dart';
import 'package:client/features/rides/screens/trips/screens/pending/pending_ride_matching_screen.dart';
import 'package:client/features/rides/screens/trips/widgets/ride_card.dart';
import 'package:client/features/rides/screens/trips/widgets/trips_list.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  testWidgets('hybrid matching ride opens driver bid offers', (tester) async {
    await tester.pumpWidget(
      MaterialApp(
        home: Scaffold(
          body: STripsList(
            filter: STripsFilter.ongoing,
            rides: [
              _ride(
                status: RideStatus.matching,
                pricingMode: PricingMode.hybrid,
              ),
            ],
          ),
        ),
      ),
    );

    await tester.tap(find.byType(SRideCard));
    await tester.pump();
    await tester.pump(const Duration(milliseconds: 350));

    expect(find.byType(PendingRideMatchingScreen), findsOneWidget);
  });

  testWidgets('fixed matching ride opens fixed waiting screen', (tester) async {
    await tester.pumpWidget(
      MaterialApp(
        home: Scaffold(
          body: STripsList(
            filter: STripsFilter.ongoing,
            rides: [
              _ride(
                status: RideStatus.matching,
                pricingMode: PricingMode.fixed,
              ),
            ],
          ),
        ),
      ),
    );

    await tester.tap(find.byType(SRideCard));
    await tester.pump();
    await tester.pump(const Duration(milliseconds: 350));

    expect(find.byType(FixedRideWaitingScreen), findsOneWidget);
    expect(find.byType(PendingRideMatchingScreen), findsNothing);
  });

  testWidgets(
      'legacy matching summary resolves full hybrid ride before opening',
      (tester) async {
    await tester.pumpWidget(
      MaterialApp(
        home: Scaffold(
          body: STripsList(
            filter: STripsFilter.ongoing,
            repository: _RideRepositoryStub(PricingMode.hybrid),
            rides: [
              _ride(
                status: RideStatus.matching,
                pricingMode: PricingMode.fixed,
                hasExplicitPricingMode: false,
              ),
            ],
          ),
        ),
      ),
    );

    await tester.tap(find.byType(SRideCard));
    await tester.pump();
    await tester.pump(const Duration(milliseconds: 350));

    expect(find.byType(PendingRideMatchingScreen), findsOneWidget);
    expect(find.byType(FixedRideWaitingScreen), findsNothing);
  });

  testWidgets('legacy matching summary resolves full fixed ride before waiting',
      (tester) async {
    await tester.pumpWidget(
      MaterialApp(
        home: Scaffold(
          body: STripsList(
            filter: STripsFilter.ongoing,
            repository: _RideRepositoryStub(PricingMode.fixed),
            rides: [
              _ride(
                status: RideStatus.matching,
                pricingMode: PricingMode.fixed,
                hasExplicitPricingMode: false,
              ),
            ],
          ),
        ),
      ),
    );

    await tester.tap(find.byType(SRideCard));
    await tester.pump();
    await tester.pump(const Duration(milliseconds: 350));

    expect(find.byType(FixedRideWaitingScreen), findsOneWidget);
    expect(find.byType(PendingRideMatchingScreen), findsNothing);
  });

  testWidgets('accepted ride with driver opens ride tracking', (tester) async {
    await tester.pumpWidget(
      MaterialApp(
        home: Scaffold(
          body: STripsList(
            filter: STripsFilter.ongoing,
            rides: [
              _ride(
                status: RideStatus.accepted,
                pricingMode: PricingMode.fixed,
                assignedDriverId: 'driver-001',
              ),
            ],
          ),
        ),
      ),
    );

    await tester.tap(find.byType(SRideCard));
    await tester.pump();
    await tester.pump(const Duration(milliseconds: 350));

    expect(find.byType(RideTrackingScreen), findsOneWidget);
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
    createdAt: DateTime.parse('2026-05-26T10:00:00Z'),
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
      'created_at': '2026-05-26T10:00:00Z',
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
