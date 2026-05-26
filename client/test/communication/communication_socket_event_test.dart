import 'package:client/features/communication/data/communication_socket_event.dart';
import 'package:client/features/communication/domain/communication_models.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  test('parses realtime text message events', () {
    final event = SCommunicationSocketEvent.fromMessage({
      'event': 'MESSAGE_SENT',
      'data': {
        'id': 'message-1',
        'conversation_id': 'conversation-1',
        'sender_participant_id': 'participant-1',
        'message_type': 'TEXT',
        'body': 'I am outside',
        'sent_at': '2026-05-25T12:00:00Z',
      },
    });

    expect(event.type, SCommunicationSocketEventType.messageSent);
    expect(event.message?.body, 'I am outside');
    expect(event.message?.type, SCommunicationMessageType.text);
  });

  test('parses WebRTC ICE candidate events', () {
    final event = SCommunicationSocketEvent.fromMessage({
      'event': 'WEBRTC_ICE_CANDIDATE',
      'data': {
        'call_id': 'call-1',
        'sender_participant_id': 'participant-1',
        'payload': {
          'candidate': 'candidate',
          'sdpMid': '0',
          'sdpMLineIndex': 0,
        },
      },
    });

    expect(event.type, SCommunicationSocketEventType.webRtcIceCandidate);
    expect(event.callId, 'call-1');
    expect(event.payload?['candidate'], 'candidate');
  });
}
