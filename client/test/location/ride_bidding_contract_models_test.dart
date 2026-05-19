import 'package:client/data/rides/ride_models.dart';
import 'package:client/features/location/domain/bidding_models.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  test('parses backend ride response contract', () {
    final ride = RideResponse.fromJson(_rideJson());

    expect(ride.id, 'ride-001');
    expect(ride.serviceType, ServiceType.cityRide);
    expect(ride.pricingMode, PricingMode.hybrid);
    expect(ride.status, RideStatus.matching);
    expect(ride.stops, hasLength(2));
    expect(ride.pickupStop?.stopType, StopType.pickup);
  });

  test('parses backend bidding session contract', () {
    final session = SBiddingSession.fromJson({
      'session_id': 'session-001',
      'service_request_id': 'ride-001',
      'status': 'OPEN',
      'pricing_mode': 'HYBRID',
      'passenger_user_id': 'passenger-001',
      'baseline_price': 250,
      'lowest_bid': 240,
      'bids': [
        {
          'id': 'bid-001',
          'bidding_session_id': 'session-001',
          'driver_id': 'driver-001',
          'driver_vehicle_id': null,
          'bid_amount': 240,
          'currency': 'PKR',
          'eta_minutes': 4,
          'message': 'I can pick you up',
          'status': 'PLACED',
          'placed_at': '2026-05-18T12:00:00Z',
        },
      ],
      'counter_offers': [
        {
          'id': 'counter-001',
          'price': 245,
          'eta_minutes': 5,
          'status': 'PENDING',
          'user_id': 'passenger-001',
          'driver_id': null,
          'bid_id': null,
          'created_at': '2026-05-18T12:01:00Z',
        },
      ],
    });

    expect(session.sessionId, 'session-001');
    expect(session.pricingMode, PricingMode.hybrid);
    expect(session.bids.single.bidAmount, 240);
    expect(session.counterOffers.single.price, 245);
  });
}

Map<String, dynamic> _rideJson() {
  final stop = {
    'id': 'stop-001',
    'service_request_id': 'ride-001',
    'sequence_order': 1,
    'stop_type': 'PICKUP',
    'latitude': 31.52,
    'longitude': 74.35,
    'place_name': 'Pickup',
    'address_line_1': 'Pickup',
    'address_line_2': null,
    'city': 'Lahore',
    'state': null,
    'country': 'Pakistan',
    'postal_code': null,
    'contact_name': null,
    'contact_phone': null,
    'instructions': null,
    'arrived_at': null,
    'completed_at': null,
  };
  final dropoff = {
    ...stop,
    'id': 'stop-002',
    'sequence_order': 2,
    'stop_type': 'DROPOFF',
    'place_name': 'Dropoff',
  };

  return {
    'id': 'ride-001',
    'passenger_id': 'passenger-001',
    'assigned_driver_id': null,
    'service_type': 'CITY_RIDE',
    'category': 'MINI',
    'pricing_mode': 'HYBRID',
    'status': 'MATCHING',
    'baseline_min_price': 200,
    'baseline_max_price': 260,
    'final_price': null,
    'passenger_payment_method': 'CASH',
    'passenger_payment_method_id': null,
    'payment_collection_mode': 'DRIVER_COLLECTED',
    'scheduled_at': null,
    'is_scheduled': false,
    'is_risky': false,
    'auto_accept_driver': true,
    'accepted_at': null,
    'completed_at': null,
    'cancelled_at': null,
    'cancellation_reason': null,
    'created_at': '2026-05-18T12:00:00Z',
    'stops': [stop, dropoff],
    'proof_images': [],
    'verification_codes': [],
    'pickup_stop': stop,
    'dropoff_stop': dropoff,
  };
}
