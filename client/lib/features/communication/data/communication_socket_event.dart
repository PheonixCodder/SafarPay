import 'dart:convert';

import '../domain/communication_models.dart';

enum SCommunicationSocketEventType {
  subscribed,
  messageSent,
  mediaMessageSent,
  typingStarted,
  typingStopped,
  callRinging,
  callAccepted,
  callEnded,
  webRtcOffer,
  webRtcAnswer,
  webRtcIceCandidate,
  error,
  unknown,
}

class SCommunicationSocketEvent {
  const SCommunicationSocketEvent({
    required this.type,
    required this.data,
    this.message,
    this.call,
    this.senderParticipantId,
    this.callId,
    this.payload,
  });

  final SCommunicationSocketEventType type;
  final Map<String, dynamic> data;
  final SCommunicationMessage? message;
  final SCommunicationCall? call;
  final String? senderParticipantId;
  final String? callId;
  final Map<String, dynamic>? payload;

  factory SCommunicationSocketEvent.fromMessage(Object? raw) {
    final decoded =
        raw is Map<String, dynamic> ? raw : jsonDecode(raw?.toString() ?? '{}');
    final envelope =
        decoded is Map<String, dynamic> ? decoded : <String, dynamic>{};
    final event = envelope['event']?.toString() ?? '';
    final dataRaw = envelope['data'];
    final data =
        dataRaw is Map<String, dynamic> ? dataRaw : <String, dynamic>{};

    final type = switch (event) {
      'SUBSCRIBED' => SCommunicationSocketEventType.subscribed,
      'MESSAGE_SENT' => SCommunicationSocketEventType.messageSent,
      'MEDIA_MESSAGE_SENT' => SCommunicationSocketEventType.mediaMessageSent,
      'TYPING_STARTED' => SCommunicationSocketEventType.typingStarted,
      'TYPING_STOPPED' => SCommunicationSocketEventType.typingStopped,
      'CALL_RINGING' => SCommunicationSocketEventType.callRinging,
      'CALL_ACCEPTED' => SCommunicationSocketEventType.callAccepted,
      'CALL_ENDED' => SCommunicationSocketEventType.callEnded,
      'WEBRTC_OFFER' => SCommunicationSocketEventType.webRtcOffer,
      'WEBRTC_ANSWER' => SCommunicationSocketEventType.webRtcAnswer,
      'WEBRTC_ICE_CANDIDATE' =>
        SCommunicationSocketEventType.webRtcIceCandidate,
      'ERROR' => SCommunicationSocketEventType.error,
      _ => SCommunicationSocketEventType.unknown,
    };

    final messageJson = data['message'] is Map<String, dynamic>
        ? data['message'] as Map<String, dynamic>
        : data;
    final callJson = data['id'] != null && data['caller_participant_id'] != null
        ? data
        : null;

    return SCommunicationSocketEvent(
      type: type,
      data: data,
      message: type == SCommunicationSocketEventType.messageSent
          ? SCommunicationMessage.fromJson(data)
          : type == SCommunicationSocketEventType.mediaMessageSent
              ? SCommunicationMessage.fromJson(messageJson).copyWith(
                  mediaId: data['media_id']?.toString(),
                )
              : null,
      call: callJson == null ? null : SCommunicationCall.fromJson(callJson),
      senderParticipantId: data['sender_participant_id']?.toString(),
      callId: data['call_id']?.toString(),
      payload: data['payload'] is Map<String, dynamic>
          ? data['payload'] as Map<String, dynamic>
          : null,
    );
  }
}
