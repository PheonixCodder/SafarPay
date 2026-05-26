import 'dart:async';
import 'dart:convert';

import 'package:web_socket_channel/web_socket_channel.dart';

import '../../../utils/constants/api_constants.dart';
import '../../../utils/http/client.dart';
import 'communication_socket_event.dart';

class SCommunicationSocketRepository {
  WebSocketChannel? _channel;

  Stream<SCommunicationSocketEvent> connect(String conversationId) async* {
    final token = await SHttpClient.accessTokenForSocket();
    if (token == null || token.isEmpty) {
      throw const SCommunicationSocketException('Missing access token.');
    }

    final uri = SApiConstants.websocketUri(
      SApiService.communication,
      '/ws',
      queryParameters: {'token': token},
    );

    final channel = WebSocketChannel.connect(uri);
    _channel = channel;
    channel.sink.add(jsonEncode({
      'action': 'subscribe',
      'conversation_id': conversationId,
    }));

    await for (final message in channel.stream) {
      yield SCommunicationSocketEvent.fromMessage(message);
    }
  }

  void typingStarted(String conversationId) {
    _send({
      'action': 'typing_started',
      'conversation_id': conversationId,
    });
  }

  void typingStopped(String conversationId) {
    _send({
      'action': 'typing_stopped',
      'conversation_id': conversationId,
    });
  }

  void sendOffer({
    required String conversationId,
    required String callId,
    required Map<String, dynamic> payload,
  }) {
    _send({
      'action': 'webrtc_offer',
      'conversation_id': conversationId,
      'call_id': callId,
      'payload': payload,
    });
  }

  void sendAnswer({
    required String conversationId,
    required String callId,
    required Map<String, dynamic> payload,
  }) {
    _send({
      'action': 'webrtc_answer',
      'conversation_id': conversationId,
      'call_id': callId,
      'payload': payload,
    });
  }

  void sendIceCandidate({
    required String conversationId,
    required String callId,
    required Map<String, dynamic> payload,
  }) {
    _send({
      'action': 'webrtc_ice_candidate',
      'conversation_id': conversationId,
      'call_id': callId,
      'payload': payload,
    });
  }

  Future<void> close() async {
    await _channel?.sink.close();
    _channel = null;
  }

  void _send(Map<String, dynamic> payload) {
    _channel?.sink.add(jsonEncode(payload));
  }
}

class SCommunicationSocketException implements Exception {
  const SCommunicationSocketException(this.message);

  final String message;

  @override
  String toString() => message;
}
