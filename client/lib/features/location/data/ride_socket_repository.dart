import 'dart:async';

import 'demo/location_demo_data.dart';
import 'ride_socket_event.dart';

class SRideSocketRepository {
  SRideSocketRepository();

  Stream<SRideSocketEvent> connectPassenger({String? rideId}) async* {
    final demoRideId = rideId ?? 'demo-ride-001';
    for (final event in SLocationDemoData.demoRideSocketEvents(demoRideId)) {
      await Future<void>.delayed(const Duration(milliseconds: 350));
      yield SRideSocketEvent.fromJson(event);
    }

    // final token = await STokenStorage.accessToken();
    // final uri = SApiConstants.websocketUri(
    //   SApiService.ride,
    //   '/ws/passengers',
    //   queryParameters: {
    //     'token': token!,
    //     if (rideId != null) 'ride_id': rideId,
    //   },
    // );
    //
    // final channel = WebSocketChannel.connect(uri);
    // await for (final message in channel.stream) {
    //   final body = jsonDecode(message as String) as Map<String, dynamic>;
    //   yield SRideSocketEvent.fromJson(body);
    // }
  }

  Stream<SRideSocketEvent> connectDriver() async* {
    for (final event in SLocationDemoData.demoRideSocketEvents(
      'demo-driver-ride-001',
    )) {
      await Future<void>.delayed(const Duration(milliseconds: 350));
      yield SRideSocketEvent.fromJson(event);
    }

    // final token = await STokenStorage.accessToken();
    // final uri = SApiConstants.websocketUri(
    //   SApiService.ride,
    //   '/ws/drivers',
    //   queryParameters: {'token': token!},
    // );
    //
    // final channel = WebSocketChannel.connect(uri);
    // await for (final message in channel.stream) {
    //   final body = jsonDecode(message as String) as Map<String, dynamic>;
    //   yield SRideSocketEvent.fromJson(body);
    // }
  }

  Future<void> ping() async {}

  Future<void> close() async {}
}

class SRideSocketException implements Exception {
  const SRideSocketException(this.message);

  final String message;

  @override
  String toString() => message;
}
