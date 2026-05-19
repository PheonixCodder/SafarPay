enum SSupportTicketAttachmentType {
  image('IMAGE'),
  file('FILE'),
  audio('AUDIO');

  const SSupportTicketAttachmentType(this.value);

  final String value;
}

enum SSupportTicketPriority {
  normal('NORMAL'),
  urgent('URGENT');

  const SSupportTicketPriority(this.value);

  final String value;
}

class SSupportTicketAttachment {
  const SSupportTicketAttachment({
    required this.type,
    required this.fileName,
    required this.mimeType,
    required this.sizeBytes,
  });

  final SSupportTicketAttachmentType type;
  final String fileName;
  final String mimeType;
  final int sizeBytes;

  Map<String, dynamic> toJson() {
    return {
      'type': type.value,
      'file_name': fileName,
      'mime_type': mimeType,
      'size_bytes': sizeBytes,
    };
  }
}

class SSupportTicketCreateRequest {
  const SSupportTicketCreateRequest({
    required this.description,
    required this.relatedRideId,
    required this.priority,
    required this.attachments,
  });

  final String description;
  final String? relatedRideId;
  final SSupportTicketPriority priority;
  final List<SSupportTicketAttachment> attachments;

  Map<String, dynamic> toJson() {
    return {
      'description': description,
      'related_ride_id': relatedRideId,
      'priority': priority.value,
      'attachments': attachments.map((item) => item.toJson()).toList(),
    };
  }
}

class SSupportTicketCreateResponse {
  const SSupportTicketCreateResponse({
    required this.ticketId,
    required this.status,
    required this.expectedResponseMinutes,
    required this.message,
  });

  final String ticketId;
  final String status;
  final int expectedResponseMinutes;
  final String message;

  factory SSupportTicketCreateResponse.fromJson(Map<String, dynamic> json) {
    return SSupportTicketCreateResponse(
      ticketId: json['ticket_id']?.toString() ?? '',
      status: json['status']?.toString() ?? '',
      expectedResponseMinutes:
          int.tryParse(json['expected_response_minutes']?.toString() ?? '') ??
              0,
      message: json['message']?.toString() ?? '',
    );
  }
}
