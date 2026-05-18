import 'package:client/features/location/data/live_ride_socket_event.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  test('parses driver location websocket event', () {
    final event = SLiveRideSocketEvent.fromJson({
      'event': 'DRIVER_LOCATION_UPDATED',
      'timestamp': '2026-05-17T12:00:00Z',
      'data': {
        'driver_id': 'driver-1',
        'lat': 31.52,
        'lng': 74.35,
        'heading': 180.0,
        'speed': 42.1,
      },
    });

    expect(event.type, SLiveRideSocketEventType.driverLocationUpdated);
    expect(event.driverLocation?.driverId, 'driver-1');
    expect(event.driverLocation?.coordinate.latitude, 31.52);
  });

  test('identifies ping and pong events', () {
    expect(
      SLiveRideSocketEvent.fromJson({'event': 'ping'}).type,
      SLiveRideSocketEventType.ping,
    );
    expect(
      SLiveRideSocketEvent.fromJson({'event': 'pong'}).type,
      SLiveRideSocketEventType.pong,
    );
  });
}
