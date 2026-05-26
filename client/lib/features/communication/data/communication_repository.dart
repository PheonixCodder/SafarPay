import 'dart:typed_data';

import '../../../utils/constants/api_constants.dart';
import '../../../utils/http/client.dart';
import '../domain/communication_models.dart';

class SCommunicationRepository {
  const SCommunicationRepository();

  Future<SConversation> conversationByRide(String rideId) async {
    final data = await SHttpClient.get(
      '/conversations/by-ride/$rideId',
      service: SApiService.communication,
      requiresAuth: true,
    );
    return SConversation.fromJson(data);
  }

  Future<List<SCommunicationMessage>> messages(String conversationId) async {
    final data = await SHttpClient.get(
      '/conversations/$conversationId/messages',
      service: SApiService.communication,
      requiresAuth: true,
    );
    final values = data['data'];
    if (values is! List) return const [];
    return values
        .whereType<Map<String, dynamic>>()
        .map(SCommunicationMessage.fromJson)
        .toList();
  }

  Future<SCommunicationMessage> sendText({
    required String conversationId,
    required String body,
  }) async {
    final data = await SHttpClient.post(
      '/conversations/$conversationId/messages',
      service: SApiService.communication,
      requiresAuth: true,
      body: {'body': body},
    );
    return SCommunicationMessage.fromJson(data);
  }

  Future<SMediaUploadTicket> createMediaUpload({
    required String conversationId,
    required SCommunicationMediaType mediaType,
    required String mimeType,
    required int sizeBytes,
    String? fileName,
    double? durationSeconds,
  }) async {
    final data = await SHttpClient.post(
      '/conversations/$conversationId/media/upload-url',
      service: SApiService.communication,
      requiresAuth: true,
      body: {
        'media_type':
            mediaType == SCommunicationMediaType.image ? 'IMAGE' : 'VOICE_NOTE',
        'mime_type': mimeType,
        'file_size_bytes': sizeBytes,
        if (fileName != null) 'file_name': fileName,
        if (durationSeconds != null) 'duration_seconds': durationSeconds,
      },
    );
    return SMediaUploadTicket.fromJson(data);
  }

  Future<void> uploadMediaBytes({
    required SMediaUploadTicket ticket,
    required Uint8List bytes,
  }) {
    return SHttpClient.putBytesToAbsoluteUrl(
      ticket.uploadUrl,
      bytes: bytes,
      contentType: ticket.mimeType,
    );
  }

  Future<SCommunicationMessage> registerMediaMessage({
    required String conversationId,
    required String mediaId,
  }) async {
    final data = await SHttpClient.post(
      '/conversations/$conversationId/messages/media',
      service: SApiService.communication,
      requiresAuth: true,
      body: {'media_id': mediaId},
    );
    final message = data['message'];
    if (message is Map<String, dynamic>) {
      return SCommunicationMessage.fromJson(message).copyWith(
        mediaId: data['media_id']?.toString(),
      );
    }
    return SCommunicationMessage.fromJson(data);
  }

  Future<String> mediaUrl(String messageId) async {
    final data = await SHttpClient.get(
      '/messages/$messageId/media-url',
      service: SApiService.communication,
      requiresAuth: true,
    );
    return data['view_url']?.toString() ?? '';
  }

  Future<List<Map<String, dynamic>>> iceServers() async {
    final data = await SHttpClient.get(
      '/webrtc/ice-servers',
      service: SApiService.communication,
      requiresAuth: true,
    );
    final values = data['ice_servers'];
    if (values is! List) return const [];
    return values.whereType<Map<String, dynamic>>().toList();
  }

  Future<SCommunicationCall> startCall({
    required String conversationId,
    Map<String, dynamic>? initialOffer,
  }) async {
    final data = await SHttpClient.post(
      '/conversations/$conversationId/calls',
      service: SApiService.communication,
      requiresAuth: true,
      body: {
        if (initialOffer != null) 'initial_offer': initialOffer,
      },
    );
    return SCommunicationCall.fromJson(data);
  }

  Future<SCommunicationCall> endCall({
    required String callId,
    required SCommunicationCallStatus status,
    String? reason,
  }) async {
    final data = await SHttpClient.post(
      '/calls/$callId/end',
      service: SApiService.communication,
      requiresAuth: true,
      body: {
        'status': _callStatusWire(status),
        if (reason != null) 'reason': reason,
      },
    );
    return SCommunicationCall.fromJson(data);
  }
}

String _callStatusWire(SCommunicationCallStatus status) {
  return switch (status) {
    SCommunicationCallStatus.missed => 'MISSED',
    SCommunicationCallStatus.rejected => 'REJECTED',
    SCommunicationCallStatus.failed => 'FAILED',
    _ => 'ENDED',
  };
}
