import 'package:flutter/material.dart';
import 'package:get/get.dart';

import '../models/support_ticket_models.dart';
import '../repositories/support_ticket_repository.dart';

class SSomethingElseController extends GetxController {
  SSomethingElseController({
    SSupportTicketRepository repository = const SSupportTicketRepository(),
  }) : _repository = repository;

  final SSupportTicketRepository _repository;

  final TextEditingController descriptionController = TextEditingController();
  final RxString description = ''.obs;
  final RxString errorMessage = ''.obs;
  final RxBool isSubmitting = false.obs;
  final RxList<SSupportTicketAttachment> attachments =
      <SSupportTicketAttachment>[].obs;

  static const String demoRideId = 'ride-demo-001';

  int get remainingCharacters {
    final remaining = 1000 - description.value.length;
    return remaining < 0 ? 0 : remaining;
  }

  @override
  void onClose() {
    descriptionController.dispose();
    super.onClose();
  }

  void onDescriptionChanged(String value) {
    final nextValue = value.length > 1000 ? value.substring(0, 1000) : value;
    if (nextValue != value) {
      descriptionController.text = nextValue;
      descriptionController.selection = TextSelection.collapsed(
        offset: nextValue.length,
      );
    }
    description.value = nextValue;
    if (errorMessage.value.isNotEmpty && nextValue.trim().isNotEmpty) {
      errorMessage.value = '';
    }
  }

  void addDemoAttachment(SSupportTicketAttachmentType type) {
    final fileName = switch (type) {
      SSupportTicketAttachmentType.image => 'support-image.jpg',
      SSupportTicketAttachmentType.file => 'support-file.pdf',
      SSupportTicketAttachmentType.audio => 'support-audio.m4a',
    };
    final mimeType = switch (type) {
      SSupportTicketAttachmentType.image => 'image/jpeg',
      SSupportTicketAttachmentType.file => 'application/pdf',
      SSupportTicketAttachmentType.audio => 'audio/mp4',
    };

    attachments.removeWhere((item) => item.type == type);
    attachments.add(
      SSupportTicketAttachment(
        type: type,
        fileName: fileName,
        mimeType: mimeType,
        sizeBytes: 1024,
      ),
    );
  }

  Future<SSupportTicketCreateResponse?> submit() async {
    final trimmedDescription = description.value.trim();
    if (trimmedDescription.isEmpty) {
      errorMessage.value = 'Describe your issue to submit a ticket.';
      return null;
    }

    isSubmitting.value = true;
    errorMessage.value = '';
    try {
      return _repository.createTicket(
        SSupportTicketCreateRequest(
          description: trimmedDescription,
          relatedRideId: demoRideId,
          priority: SSupportTicketPriority.normal,
          attachments: attachments.toList(growable: false),
        ),
      );
    } catch (_) {
      errorMessage.value = 'Ticket submission failed. Please try again.';
      return null;
    } finally {
      isSubmitting.value = false;
    }
  }
}
