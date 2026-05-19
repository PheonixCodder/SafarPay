import 'package:flutter/material.dart';
import 'package:iconsax/iconsax.dart';

import '../../../../../../../utils/constants/colors.dart';
import '../../../../../../../utils/constants/sizes.dart';
import '../models/support_ticket_models.dart';
import 'support_attachment_tile.dart';

class SSupportAttachmentsSection extends StatelessWidget {
  const SSupportAttachmentsSection({
    super.key,
    required this.attachments,
    required this.onAddAttachment,
  });

  final List<SSupportTicketAttachment> attachments;
  final ValueChanged<SSupportTicketAttachmentType> onAddAttachment;

  bool _isSelected(SSupportTicketAttachmentType type) {
    return attachments.any((item) => item.type == type);
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'Attach documents (optional)',
          style: Theme.of(context).textTheme.labelLarge?.copyWith(
                color: SColors.textPrimary,
                fontWeight: FontWeight.w800,
              ),
        ),
        const SizedBox(height: SSizes.sm),
        Row(
          children: [
            SSupportAttachmentTile(
              icon: Iconsax.gallery,
              label: 'Upload Image',
              isSelected: _isSelected(SSupportTicketAttachmentType.image),
              onTap: () =>
                  onAddAttachment(SSupportTicketAttachmentType.image),
            ),
            const SizedBox(width: SSizes.sm),
            SSupportAttachmentTile(
              icon: Iconsax.document_upload,
              label: 'Upload File',
              isSelected: _isSelected(SSupportTicketAttachmentType.file),
              onTap: () => onAddAttachment(SSupportTicketAttachmentType.file),
            ),
            const SizedBox(width: SSizes.sm),
            SSupportAttachmentTile(
              icon: Iconsax.microphone_2,
              label: 'Record Audio',
              isSelected: _isSelected(SSupportTicketAttachmentType.audio),
              onTap: () => onAddAttachment(SSupportTicketAttachmentType.audio),
            ),
          ],
        ),
      ],
    );
  }
}
