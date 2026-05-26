import 'package:client/data/rides/ride_models.dart';
import 'package:client/features/rides/screens/trips/screens/pending/pending_ride_matching_screen.dart';
import 'package:client/features/rides/screens/trips/widgets/ride_card.dart';
import 'package:client/features/rides/screens/trips/widgets/trips_list.dart';
import 'package:client/features/rides/controllers/trips_controller.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  testWidgets('pending ongoing ride opens matching offers instead of tracking',
      (tester) async {
    await tester.pumpWidget(
      MaterialApp(
        home: Scaffold(
          body: STripsList(
            filter: STripsFilter.ongoing,
            rides: [_ride(status: RideStatus.matching)],
          ),
        ),
      ),
    );

    await tester.tap(find.byType(SRideCard));
    await tester.pump();
    await tester.pump(const Duration(milliseconds: 350));

    expect(find.byType(PendingRideMatchingScreen), findsOneWidget);
  });
}

RideSummaryResponse _ride({required RideStatus status}) {
  return RideSummaryResponse(
    id: 'ride-001',
    passengerId: 'passenger-001',
    assignedDriverId: null,
    serviceType: ServiceType.cityRide,
    category: ServiceCategory.mini,
    status: status,
    passengerPaymentMethod: PassengerPaymentMethod.cash,
    paymentCollectionMode: PaymentCollectionMode.driverCollected,
    createdAt: DateTime.parse('2026-05-26T10:00:00Z'),
    scheduledAt: null,
    pickupStop: _stop('Pickup'),
    dropoffStop: _stop('Dropoff'),
  );
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
