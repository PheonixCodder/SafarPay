import 'package:client/features/location/data/bidding_socket_event.dart';
import 'package:client/features/location/data/ride_socket_event.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  test('parses ride passenger websocket lifecycle event', () {
    final event = SRideSocketEvent.fromJson({
      'event': 'RIDE_UPDATED',
      'data': {
        'ride_id': 'ride-001',
        'status': 'ACCEPTED',
      },
    });

    expect(event.type, SRideSocketEventType.rideUpdated);
    expect(event.rideId, 'ride-001');
    expect(event.status, 'ACCEPTED');
  });

  test('parses bidding passenger websocket bid event', () {
    final event = SBiddingSocketEvent.fromJson({
      'event': 'BID_PLACED',
      'data': {
        'session_id': 'session-001',
        'bid': {
          'id': 'bid-001',
          'bidding_session_id': 'session-001',
          'driver_id': 'driver-001',
          'driver_vehicle_id': null,
          'bid_amount': 230,
          'currency': 'PKR',
          'eta_minutes': 3,
          'message': null,
          'status': 'PLACED',
          'placed_at': '2026-05-18T12:00:00Z',
        },
      },
    });

    expect(event.type, SBiddingSocketEventType.bidPlaced);
    expect(event.sessionId, 'session-001');
    expect(event.bid?.id, 'bid-001');
  });
}
