import 'dart:async';

import 'bidding_socket_event.dart';
import 'demo/location_demo_data.dart';

class SBiddingSocketRepository {
  SBiddingSocketRepository();

  Stream<SBiddingSocketEvent> connectPassenger({
    required String sessionId,
  }) async* {
    for (final event in SLocationDemoData.demoBiddingSocketEvents(sessionId)) {
      await Future<void>.delayed(const Duration(milliseconds: 350));
      yield SBiddingSocketEvent.fromJson(event);
    }

    // final token = await STokenStorage.accessToken();
    // final uri = SApiConstants.websocketUri(
    //   SApiService.bidding,
    //   '/ws/passengers',
    //   queryParameters: {'token': token!},
    // );
    //
    // final channel = WebSocketChannel.connect(uri);
    // channel.sink.add(jsonEncode({
    //   'action': 'subscribe',
    //   'session_id': sessionId,
    // }));
    // await for (final message in channel.stream) {
    //   final body = jsonDecode(message as String) as Map<String, dynamic>;
    //   yield SBiddingSocketEvent.fromJson(body);
    // }
  }

  Stream<SBiddingSocketEvent> connectDriver({
    required String sessionId,
  }) async* {
    for (final event in SLocationDemoData.demoBiddingSocketEvents(sessionId)) {
      await Future<void>.delayed(const Duration(milliseconds: 350));
      yield SBiddingSocketEvent.fromJson(event);
    }

    // final token = await STokenStorage.accessToken();
    // final uri = SApiConstants.websocketUri(
    //   SApiService.bidding,
    //   '/ws/drivers',
    //   queryParameters: {'token': token!},
    // );
    //
    // final channel = WebSocketChannel.connect(uri);
    // channel.sink.add(jsonEncode({
    //   'action': 'subscribe',
    //   'session_id': sessionId,
    // }));
    // await for (final message in channel.stream) {
    //   final body = jsonDecode(message as String) as Map<String, dynamic>;
    //   yield SBiddingSocketEvent.fromJson(body);
    // }
  }

  Future<void> subscribe(String sessionId) async {}

  Future<void> close() async {}
}

class SBiddingSocketException implements Exception {
  const SBiddingSocketException(this.message);

  final String message;

  @override
  String toString() => message;
}
