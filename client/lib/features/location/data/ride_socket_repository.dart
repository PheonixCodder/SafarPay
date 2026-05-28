import 'dart:async';
import 'dart:convert';

import 'package:web_socket_channel/web_socket_channel.dart';

import '../../../common/runtime/runtime_mode.dart';
import '../../../utils/constants/api_constants.dart';
import '../../../utils/http/client.dart';
import 'demo/location_demo_data.dart';
import 'ride_socket_event.dart';

class SRideSocketRepository {
  SRideSocketRepository({bool? useDemoData})
      : _delegate = (useDemoData ?? SRuntimeModeConfig.useLocationDemoData)
            ? _DemoRideSocketDelegate()
            : _WebRideSocketDelegate();

  final _RideSocketDelegate _delegate;

  SRuntimeDataSource get runtimeDataSource => _delegate.runtimeDataSource;

  Stream<SRideSocketEvent> connectPassenger({String? rideId}) async* {
    yield* _delegate.connectPassenger(rideId: rideId);
  }

  Stream<SRideSocketEvent> connectDriver() async* {
    yield* _delegate.connectDriver();
  }

  Future<void> ping() => _delegate.ping();

  Future<void> close() => _delegate.close();
}

abstract class _RideSocketDelegate {
  SRuntimeDataSource get runtimeDataSource;

  Stream<SRideSocketEvent> connectPassenger({String? rideId});

  Stream<SRideSocketEvent> connectDriver();

  Future<void> ping();

  Future<void> close();
}

class _DemoRideSocketDelegate implements _RideSocketDelegate {
  @override
  SRuntimeDataSource get runtimeDataSource => SRuntimeDataSource.demo;

  @override
  Stream<SRideSocketEvent> connectPassenger({String? rideId}) async* {
    final demoRideId = rideId ?? 'demo-ride-001';
    yield* _demoEvents(demoRideId);
  }

  @override
  Stream<SRideSocketEvent> connectDriver() async* {
    yield* _demoEvents('demo-driver-ride-001');
  }

  @override
  Future<void> ping() async {}

  @override
  Future<void> close() async {}

  Stream<SRideSocketEvent> _demoEvents(String rideId) async* {
    for (final event in SLocationDemoData.demoRideSocketEvents(rideId)) {
      await Future<void>.delayed(const Duration(milliseconds: 350));
      yield SRideSocketEvent.fromJson(event);
    }
  }
}

class _WebRideSocketDelegate implements _RideSocketDelegate {
  WebSocketChannel? _channel;

  @override
  SRuntimeDataSource get runtimeDataSource => SRuntimeDataSource.real;

  @override
  Stream<SRideSocketEvent> connectPassenger({String? rideId}) async* {
    final channel = await _connect('/ws/passengers', {
      if (rideId != null) 'ride_id': rideId,
    });
    await for (final message in channel.stream) {
      final body = _decodeMessage(message);
      if (body['event'] == 'ping') {
        channel.sink.add('pong');
      }
      yield SRideSocketEvent.fromJson(body);
    }
  }

  @override
  Stream<SRideSocketEvent> connectDriver() async* {
    final channel = await _connect('/ws/drivers');
    await for (final message in channel.stream) {
      final body = _decodeMessage(message);
      if (body['event'] == 'ping') {
        channel.sink.add('pong');
      }
      yield SRideSocketEvent.fromJson(body);
    }
  }

  @override
  Future<void> ping() async {
    _channel?.sink.add('ping');
  }

  @override
  Future<void> close() async {
    await _channel?.sink.close();
    _channel = null;
  }

  Future<WebSocketChannel> _connect(
    String endpoint, [
    Map<String, String> queryParameters = const {},
  ]) async {
    final token = await SHttpClient.accessTokenForSocket();
    if (token == null || token.isEmpty) {
      throw const SRideSocketException('Missing access token.');
    }

    final uri = SApiConstants.websocketUri(
      SApiService.ride,
      endpoint,
      queryParameters: {
        'token': token,
        ...queryParameters,
      },
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

class SRideSocketException implements Exception {
  const SRideSocketException(this.message);

  final String message;

  @override
  String toString() => message;
}
