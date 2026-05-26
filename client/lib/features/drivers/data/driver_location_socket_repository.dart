import 'dart:convert';

import 'package:web_socket_channel/web_socket_channel.dart';

import '../../../utils/constants/api_constants.dart';
import '../../../utils/http/client.dart';
import '../../location/domain/location_models.dart';

class SDriverLocationSocketRepository {
  WebSocketChannel? _channel;

  Future<void> connect() async {
    final token = await SHttpClient.accessTokenForSocket();
    if (token == null || token.isEmpty) {
      throw const SDriverLocationSocketException('Missing access token.');
    }

    final uri = SApiConstants.websocketUri(
      SApiService.location,
      '/ws/drivers/location',
      queryParameters: {'token': token},
    );
    _channel = WebSocketChannel.connect(uri);
    _channel?.stream.listen((message) {
      final data = _decode(message);
      if (data['event'] == 'ping') {
        _channel?.sink.add(jsonEncode({'event': 'pong'}));
      }
    });
  }

  void sendLocation({
    required SCoordinate coordinate,
    required double accuracy,
    double? speed,
    double? heading,
    String? rideId,
  }) {
    _channel?.sink.add(jsonEncode({
      'lat': coordinate.latitude,
      'lng': coordinate.longitude,
      'accuracy': accuracy,
      if (speed != null) 'speed': speed,
      if (heading != null) 'heading': heading,
      'ts': DateTime.now().millisecondsSinceEpoch,
      if (rideId != null) 'ride_id': rideId,
    }));
  }

  Future<void> close() async {
    await _channel?.sink.close();
    _channel = null;
  }
}

Map<String, dynamic> _decode(Object? message) {
  if (message is Map<String, dynamic>) return message;
  final decoded = jsonDecode(message?.toString() ?? '{}');
  return decoded is Map<String, dynamic> ? decoded : <String, dynamic>{};
}

class SDriverLocationSocketException implements Exception {
  const SDriverLocationSocketException(this.message);

  final String message;

  @override
  String toString() => message;
}
