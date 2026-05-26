import 'dart:async';
import 'dart:convert';

import 'package:web_socket_channel/web_socket_channel.dart';

import '../../../utils/constants/api_constants.dart';
import '../../../utils/http/client.dart';
import 'bidding_socket_event.dart';
import 'demo/location_demo_data.dart';

class SBiddingSocketRepository {
  SBiddingSocketRepository({bool? useDemoData})
      : _useDemoData = useDemoData ?? SApiConstants.useLocationDemoData;

  final bool _useDemoData;
  WebSocketChannel? _channel;

  Stream<SBiddingSocketEvent> connectPassenger({
    required String sessionId,
  }) async* {
    if (_useDemoData) {
      for (final event in SLocationDemoData.demoBiddingSocketEvents(sessionId)) {
        await Future<void>.delayed(const Duration(milliseconds: 350));
        yield SBiddingSocketEvent.fromJson(event);
      }
      return;
    }

    final channel = await _connect(SApiService.bidding, '/ws/passengers');
    channel.sink.add(jsonEncode({
      'action': 'subscribe',
      'session_id': sessionId,
    }));

    await for (final message in channel.stream) {
      final body = _decodeMessage(message);
      if (body['event'] == 'ping') {
        channel.sink.add(jsonEncode({'event': 'pong'}));
      }
      yield SBiddingSocketEvent.fromJson(body);
    }
  }

  Stream<SBiddingSocketEvent> connectDriver({
    required String sessionId,
  }) async* {
    if (_useDemoData) {
      for (final event in SLocationDemoData.demoBiddingSocketEvents(sessionId)) {
        await Future<void>.delayed(const Duration(milliseconds: 350));
        yield SBiddingSocketEvent.fromJson(event);
      }
      return;
    }

    final channel = await _connect(SApiService.bidding, '/ws/drivers');
    channel.sink.add(jsonEncode({
      'action': 'subscribe',
      'session_id': sessionId,
    }));

    await for (final message in channel.stream) {
      final body = _decodeMessage(message);
      if (body['event'] == 'ping') {
        channel.sink.add(jsonEncode({'event': 'pong'}));
      }
      yield SBiddingSocketEvent.fromJson(body);
    }
  }

  Future<void> subscribe(String sessionId) async {
    _channel?.sink.add(jsonEncode({
      'action': 'subscribe',
      'session_id': sessionId,
    }));
  }

  Future<void> close() async {
    await _channel?.sink.close();
    _channel = null;
  }

  Future<WebSocketChannel> _connect(
    SApiService service,
    String endpoint,
  ) async {
    final token = await SHttpClient.accessTokenForSocket();
    if (token == null || token.isEmpty) {
      throw const SBiddingSocketException('Missing access token.');
    }

    final uri = SApiConstants.websocketUri(
      service,
      endpoint,
      queryParameters: {'token': token},
    );
    final channel = WebSocketChannel.connect(uri);
    _channel = channel;
    return channel;
  }
}

Map<String, dynamic> _decodeMessage(Object? message) {
  if (message is Map<String, dynamic>) return message;
  final decoded = jsonDecode(message?.toString() ?? '{}');
  return decoded is Map<String, dynamic> ? decoded : <String, dynamic>{};
}

class SBiddingSocketException implements Exception {
  const SBiddingSocketException(this.message);

  final String message;

  @override
  String toString() => message;
}
