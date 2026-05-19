import 'dart:async';

import 'demo/location_demo_data.dart';
import 'live_ride_socket_event.dart';

class SLiveRideSocketRepository {
  SLiveRideSocketRepository();

  Stream<SLiveRideSocketEvent> connect(String rideId) async* {
    final locations = SLocationDemoData.liveRideLocations(rideId);
    await Future<void>.delayed(const Duration(milliseconds: 350));
    yield SLiveRideSocketEvent(
      type: SLiveRideSocketEventType.driverLocationUpdated,
      driverLocation: locations.driver,
    );

    // final token = await STokenStorage.accessToken();
    // if (token == null || token.isEmpty) {
    //   throw const SLiveRideSocketException('Missing access token.');
    // }
    //
    // final uri = SApiConstants.websocketUri(
    //   SApiService.location,
    //   '/ws/rides/$rideId/track',
    //   queryParameters: {'token': token},
    // );
    //
    // final channel = WebSocketChannel.connect(uri);
    // await for (final message in channel.stream) {
    //   final body = jsonDecode(message as String) as Map<String, dynamic>;
    //   yield SLiveRideSocketEvent.fromJson(body);
    // }
  }

  Future<void> close() async {}
}

class SLiveRideSocketException implements Exception {
  const SLiveRideSocketException(this.message);

  final String message;

  @override
  String toString() => message;
}
