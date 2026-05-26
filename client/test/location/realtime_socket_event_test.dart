import 'package:client/features/location/data/bidding_socket_event.dart';
import 'package:client/features/location/data/ride_socket_event.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  test('parses ride backend driver location update event', () {
    final event = SRideSocketEvent.fromJson({
      'event': 'DRIVER_LOCATION_UPDATED',
      'data': {
        'ride_id': 'ride-123',
        'driver_id': 'driver-123',
        'lat': 31.52,
        'lng': 74.35,
      },
    });

    expect(event.type, SRideSocketEventType.driverLocation);
    expect(event.rideId, 'ride-123');
    expect(event.data?['driver_id'], 'driver-123');
  });

  test('parses bidding backend payload envelope', () {
    final event = SBiddingSocketEvent.fromJson({
      'event': 'BID_ACCEPTED',
      'payload': {
        'session_id': 'session-123',
        'bid_id': 'bid-123',
        'ride_id': 'ride-123',
        'amount': 240,
      },
    });

    expect(event.type, SBiddingSocketEventType.bidAccepted);
    expect(event.sessionId, 'session-123');
    expect(event.data?['bid_id'], 'bid-123');
  });
}
