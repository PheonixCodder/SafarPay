enum SConversationStatus {
  active,
  closed,
}

enum SCommunicationMessageType {
  text,
  image,
  voiceNote,
  system,
}

enum SCommunicationMediaType {
  image,
  voiceNote,
}

enum SCommunicationCallStatus {
  ringing,
  accepted,
  ended,
  missed,
  rejected,
  failed,
}

class SConversation {
  const SConversation({
    required this.id,
    required this.rideId,
    required this.passengerUserId,
    required this.driverId,
    required this.driverUserId,
    required this.status,
  });

  final String id;
  final String rideId;
  final String passengerUserId;
  final String driverId;
  final String driverUserId;
  final SConversationStatus status;

  factory SConversation.fromJson(Map<String, dynamic> json) {
    return SConversation(
      id: json['id']?.toString() ?? '',
      rideId: json['service_request_id']?.toString() ?? '',
      passengerUserId: json['passenger_user_id']?.toString() ?? '',
      driverId: json['driver_id']?.toString() ?? '',
      driverUserId: json['driver_user_id']?.toString() ?? '',
      status: _conversationStatus(json['status']),
    );
  }
}

class SCommunicationMessage {
  const SCommunicationMessage({
    required this.id,
    required this.conversationId,
    required this.senderParticipantId,
    required this.type,
    required this.sentAt,
    this.body,
    this.replyToMessageId,
    this.mediaId,
    this.mediaUrl,
  });

  final String id;
  final String conversationId;
  final String senderParticipantId;
  final SCommunicationMessageType type;
  final DateTime sentAt;
  final String? body;
  final String? replyToMessageId;
  final String? mediaId;
  final String? mediaUrl;

  bool get isText => type == SCommunicationMessageType.text;
  bool get isImage => type == SCommunicationMessageType.image;
  bool get isVoiceNote => type == SCommunicationMessageType.voiceNote;

  SCommunicationMessage copyWith({
    String? mediaId,
    String? mediaUrl,
  }) {
    return SCommunicationMessage(
      id: id,
      conversationId: conversationId,
      senderParticipantId: senderParticipantId,
      type: type,
      sentAt: sentAt,
      body: body,
      replyToMessageId: replyToMessageId,
      mediaId: mediaId ?? this.mediaId,
      mediaUrl: mediaUrl ?? this.mediaUrl,
    );
  }

  factory SCommunicationMessage.fromJson(Map<String, dynamic> json) {
    return SCommunicationMessage(
      id: json['id']?.toString() ?? '',
      conversationId: json['conversation_id']?.toString() ?? '',
      senderParticipantId: json['sender_participant_id']?.toString() ?? '',
      type: _messageType(json['message_type']),
      body: json['body']?.toString(),
      sentAt: DateTime.tryParse(json['sent_at']?.toString() ?? '') ??
          DateTime.now(),
      replyToMessageId: json['reply_to_message_id']?.toString(),
      mediaId: json['media_id']?.toString(),
    );
  }
}

class SMediaUploadTicket {
  const SMediaUploadTicket({
    required this.mediaId,
    required this.uploadUrl,
    required this.mediaType,
    required this.mimeType,
  });

  final String mediaId;
  final String uploadUrl;
  final SCommunicationMediaType mediaType;
  final String mimeType;

  factory SMediaUploadTicket.fromJson(Map<String, dynamic> json) {
    return SMediaUploadTicket(
      mediaId: json['media_id']?.toString() ?? '',
      uploadUrl: json['presigned_url']?.toString() ?? '',
      mediaType: _mediaType(json['media_type']),
      mimeType: json['mime_type']?.toString() ?? '',
    );
  }
}

class SCommunicationCall {
  const SCommunicationCall({
    required this.id,
    required this.conversationId,
    required this.callerParticipantId,
    required this.calleeParticipantId,
    required this.status,
    this.initialOffer,
  });

  final String id;
  final String conversationId;
  final String callerParticipantId;
  final String calleeParticipantId;
  final SCommunicationCallStatus status;
  final Map<String, dynamic>? initialOffer;

  factory SCommunicationCall.fromJson(Map<String, dynamic> json) {
    final offer = json['initial_offer'];
    return SCommunicationCall(
      id: json['id']?.toString() ?? '',
      conversationId: json['conversation_id']?.toString() ?? '',
      callerParticipantId: json['caller_participant_id']?.toString() ?? '',
      calleeParticipantId: json['callee_participant_id']?.toString() ?? '',
      status: _callStatus(json['status']),
      initialOffer: offer is Map<String, dynamic> ? offer : null,
    );
  }
}

SConversationStatus _conversationStatus(Object? value) {
  return value?.toString() == 'CLOSED'
      ? SConversationStatus.closed
      : SConversationStatus.active;
}

SCommunicationMessageType _messageType(Object? value) {
  return switch (value?.toString()) {
    'IMAGE' => SCommunicationMessageType.image,
    'VOICE_NOTE' => SCommunicationMessageType.voiceNote,
    'SYSTEM' => SCommunicationMessageType.system,
    _ => SCommunicationMessageType.text,
  };
}

SCommunicationMediaType _mediaType(Object? value) {
  return value?.toString() == 'VOICE_NOTE'
      ? SCommunicationMediaType.voiceNote
      : SCommunicationMediaType.image;
}

SCommunicationCallStatus _callStatus(Object? value) {
  return switch (value?.toString()) {
    'ACCEPTED' => SCommunicationCallStatus.accepted,
    'ENDED' => SCommunicationCallStatus.ended,
    'MISSED' => SCommunicationCallStatus.missed,
    'REJECTED' => SCommunicationCallStatus.rejected,
    'FAILED' => SCommunicationCallStatus.failed,
    _ => SCommunicationCallStatus.ringing,
  };
}
