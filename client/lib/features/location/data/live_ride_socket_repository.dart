import 'dart:async';
import 'dart:convert';

import 'package:web_socket_channel/web_socket_channel.dart';

import '../../../utils/constants/api_constants.dart';
import '../../../utils/local_storage/token_storage.dart';
import '../../../utils/logging/logger.dart';
import 'live_ride_socket_event.dart';

class SLiveRideSocketRepository {
  SLiveRideSocketRepository();

  WebSocketChannel? _channel;

  Stream<SLiveRideSocketEvent> connect(String rideId) async* {
    final token = await STokenStorage.accessToken();
    if (token == null || token.isEmpty) {
      throw const SLiveRideSocketException('Missing access token.');
    }

    final uri = SApiConstants.websocketUri(
      SApiService.location,
      '/ws/rides/$rideId/track',
      queryParameters: {'token': token},
    );

    SLoggerHelper.info(
        'WS ${uri.replace(queryParameters: {'token': 'redacted'})}');
    _channel = WebSocketChannel.connect(uri);

    await for (final message in _channel!.stream) {
      final event = _parse(message);
      if (event.type == SLiveRideSocketEventType.ping) {
        _channel?.sink.add('{"event":"pong"}');
      }
      yield event;
    }
  }

  Future<void> close() async {
    await _channel?.sink.close();
    _channel = null;
  }

  SLiveRideSocketEvent _parse(Object? message) {
    try {
      if (message is String) {
        final body = jsonDecode(message);
        if (body is Map<String, dynamic>) {
          return SLiveRideSocketEvent.fromJson(body);
        }
        if (message == 'ping') {
          return const SLiveRideSocketEvent(
            type: SLiveRideSocketEventType.ping,
          );
        }
      }
    } catch (error) {
      SLoggerHelper.warning('Invalid ride socket event: $error');
    }

    return const SLiveRideSocketEvent(type: SLiveRideSocketEventType.unknown);
  }
}

class SLiveRideSocketException implements Exception {
  const SLiveRideSocketException(this.message);

  final String message;

  @override
  String toString() => message;
}
