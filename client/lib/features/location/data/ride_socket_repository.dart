import 'dart:async';
import 'dart:convert';

import 'package:web_socket_channel/web_socket_channel.dart';

import '../../../utils/constants/api_constants.dart';
import '../../../utils/http/client.dart';
import 'demo/location_demo_data.dart';
import 'ride_socket_event.dart';

class SRideSocketRepository {
  SRideSocketRepository({bool? useDemoData})
      : _useDemoData = useDemoData ?? SApiConstants.useLocationDemoData;

  final bool _useDemoData;
  WebSocketChannel? _channel;

  Stream<SRideSocketEvent> connectPassenger({String? rideId}) async* {
    if (_useDemoData) {
      final demoRideId = rideId ?? 'demo-ride-001';
      for (final event in SLocationDemoData.demoRideSocketEvents(demoRideId)) {
        await Future<void>.delayed(const Duration(milliseconds: 350));
        yield SRideSocketEvent.fromJson(event);
      }
      return;
    }

    final token = await SHttpClient.accessTokenForSocket();
    if (token == null || token.isEmpty) {
      throw const SRideSocketException('Missing access token.');
    }

    final uri = SApiConstants.websocketUri(
      SApiService.ride,
      '/ws/passengers',
      queryParameters: {
        'token': token,
        if (rideId != null) 'ride_id': rideId,
      },
    );

    final channel = WebSocketChannel.connect(uri);
    _channel = channel;
    await for (final message in channel.stream) {
      final body = _decodeMessage(message);
      if (body['event'] == 'ping') {
        channel.sink.add('pong');
      }
      yield SRideSocketEvent.fromJson(body);
    }
  }

  Stream<SRideSocketEvent> connectDriver() async* {
    if (_useDemoData) {
      for (final event in SLocationDemoData.demoRideSocketEvents(
        'demo-driver-ride-001',
      )) {
        await Future<void>.delayed(const Duration(milliseconds: 350));
        yield SRideSocketEvent.fromJson(event);
      }
      return;
    }

    final token = await SHttpClient.accessTokenForSocket();
    if (token == null || token.isEmpty) {
      throw const SRideSocketException('Missing access token.');
    }

    final uri = SApiConstants.websocketUri(
      SApiService.ride,
      '/ws/drivers',
      queryParameters: {'token': token},
    );

    final channel = WebSocketChannel.connect(uri);
    _channel = channel;
    await for (final message in channel.stream) {
      final body = _decodeMessage(message);
      if (body['event'] == 'ping') {
        channel.sink.add('pong');
      }
      yield SRideSocketEvent.fromJson(body);
    }
  }

  Future<void> ping() async {
    _channel?.sink.add('ping');
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

class SRideSocketException implements Exception {
  const SRideSocketException(this.message);

  final String message;

  @override
  String toString() => message;
}
