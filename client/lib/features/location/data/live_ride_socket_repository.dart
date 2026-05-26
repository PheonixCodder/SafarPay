import 'dart:async';
import 'dart:convert';

import 'package:web_socket_channel/web_socket_channel.dart';

import '../../../utils/constants/api_constants.dart';
import '../../../utils/http/client.dart';
import 'demo/location_demo_data.dart';
import 'live_ride_socket_event.dart';

class SLiveRideSocketRepository {
  SLiveRideSocketRepository({bool? useDemoData})
      : _useDemoData = useDemoData ?? SApiConstants.useLocationDemoData;

  final bool _useDemoData;
  WebSocketChannel? _channel;

  Stream<SLiveRideSocketEvent> connect(String rideId) async* {
    if (_useDemoData) {
      final locations = SLocationDemoData.liveRideLocations(rideId);
      await Future<void>.delayed(const Duration(milliseconds: 350));
      yield SLiveRideSocketEvent(
        type: SLiveRideSocketEventType.driverLocationUpdated,
        driverLocation: locations.driver,
      );
      return;
    }

    final token = await SHttpClient.accessTokenForSocket();
    if (token == null || token.isEmpty) {
      throw const SLiveRideSocketException('Missing access token.');
    }

    final uri = SApiConstants.websocketUri(
      SApiService.location,
      '/ws/rides/$rideId/track',
      queryParameters: {'token': token},
    );

    final channel = WebSocketChannel.connect(uri);
    _channel = channel;
    await for (final message in channel.stream) {
      final body = _decodeMessage(message);
      if (body['event'] == 'ping') {
        channel.sink.add(jsonEncode({'event': 'pong'}));
      }
      yield SLiveRideSocketEvent.fromJson(body);
    }
  }

  Future<void> close() async {
    await _channel?.sink.close();
    _channel = null;
  }
}

Map<String, dynamic> _decodeMessage(Object? message) {
  if (message is Map<String, dynamic>) return message;
  final decoded = jsonDecode(message?.toString() ?? '{}');
  return decoded is Map<String, dynamic> ? decoded : <String, dynamic>{};
}

class SLiveRideSocketException implements Exception {
  const SLiveRideSocketException(this.message);

  final String message;

  @override
  String toString() => message;
}
