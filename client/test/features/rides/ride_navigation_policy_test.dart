import 'package:client/data/rides/ride_models.dart';
import 'package:client/features/rides/domain/ride_lifecycle.dart';
import 'package:client/features/rides/navigation/ride_navigation_policy.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  group('sResolvePassengerRideEntry', () {
    test('routes hybrid matching rides to offers flow', () {
      final decision = sResolvePassengerRideEntry(
        SRideLifecycleSnapshot.fromSummary(
          _ride(
            status: RideStatus.matching,
            pricingMode: PricingMode.hybrid,
          ),
        ),
      );

      expect(decision.surface, SRideNavigationSurface.hybridMatching);
      expect(decision.actionLabel, 'View offers');
    });

    test('routes fixed matching rides to waiting flow', () {
      final decision = sResolvePassengerRideEntry(
        SRideLifecycleSnapshot.fromSummary(
          _ride(
            status: RideStatus.matching,
            pricingMode: PricingMode.fixed,
          ),
        ),
      );

      expect(decision.surface, SRideNavigationSurface.fixedWaiting);
      expect(decision.actionLabel, 'Finding driver');
    });

    test('routes assigned accepted rides to live tracking', () {
      final decision = sResolvePassengerRideEntry(
        SRideLifecycleSnapshot.fromSummary(
          _ride(
            status: RideStatus.accepted,
            pricingMode: PricingMode.fixed,
            assignedDriverId: 'driver-001',
          ),
        ),
      );

      expect(decision.surface, SRideNavigationSurface.liveTracking);
      expect(decision.actionLabel, 'Track ride');
    });

    test('routes terminal rides to details', () {
      final decision = sResolvePassengerRideEntry(
        SRideLifecycleSnapshot.fromSummary(
          _ride(
            status: RideStatus.completed,
            pricingMode: PricingMode.fixed,
            assignedDriverId: 'driver-001',
          ),
        ),
      );

      expect(decision.surface, SRideNavigationSurface.rideDetails);
      expect(decision.actionLabel, 'View details');
    });
  });

  group('SNotificationRouteIntent', () {
    test('parses driver request deeplink', () {
      final intent = sNotificationRouteIntentFromData({
        'deeplink': 'safarpay://driver/requests/ride-100',
      });

      expect(intent?.kind, SNotificationRouteKind.driverRequests);
      expect(intent?.rideId, 'ride-100');
    });

    test('parses urgent driver ride request data without deeplink', () {
      final intent = sNotificationRouteIntentFromData({
        'notification_kind': 'driver_ride_request',
        'ride_id': 'ride-101',
      });

      expect(intent?.kind, SNotificationRouteKind.driverRequests);
      expect(intent?.rideId, 'ride-101');
    });

    test('parses communication call payload', () {
      final intent = sNotificationRouteIntentFromData({
        'deeplink': 'safarpay://communication/rides/ride-200',
        'notification_kind': 'communication_call',
        'call_id': 'call-200',
      });

      expect(intent?.kind, SNotificationRouteKind.communication);
      expect(intent?.rideId, 'ride-200');
      expect(intent?.callId, 'call-200');
      expect(intent?.presentAsCall, isTrue);
    });

    test('parses data-only communication call payload', () {
      final intent = sNotificationRouteIntentFromData({
        'notification_kind': 'communication_call',
        'ride_id': 'ride-201',
        'call_id': 'call-201',
        'present_as_call': 'true',
      });

      expect(intent?.kind, SNotificationRouteKind.communication);
      expect(intent?.rideId, 'ride-201');
      expect(intent?.callId, 'call-201');
      expect(intent?.presentAsCall, isTrue);
    });

    test('parses data-only communication message payload', () {
      final intent = sNotificationRouteIntentFromData({
        'notification_kind': 'communication_message',
        'ride_id': 'ride-202',
      });

      expect(intent?.kind, SNotificationRouteKind.communication);
      expect(intent?.rideId, 'ride-202');
      expect(intent?.presentAsCall, isFalse);
    });
  });
}

RideSummaryResponse _ride({
  required RideStatus status,
  required PricingMode pricingMode,
  String? assignedDriverId,
}) {
  return RideSummaryResponse(
    id: 'ride-001',
    passengerId: 'passenger-001',
    assignedDriverId: assignedDriverId,
    serviceType: ServiceType.cityRide,
    category: ServiceCategory.mini,
    pricingMode: pricingMode,
    status: status,
    passengerPaymentMethod: PassengerPaymentMethod.cash,
    paymentCollectionMode: PaymentCollectionMode.driverCollected,
    createdAt: DateTime.parse('2026-05-27T10:00:00Z'),
    scheduledAt: null,
    pickupStop: null,
    dropoffStop: null,
  );
}
