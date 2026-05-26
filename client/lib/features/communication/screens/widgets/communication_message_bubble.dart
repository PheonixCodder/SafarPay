import 'package:flutter/material.dart';

import '../../../../utils/constants/colors.dart';
import '../../../../utils/constants/sizes.dart';
import '../../domain/communication_models.dart';

class SCommunicationMessageBubble extends StatelessWidget {
  const SCommunicationMessageBubble({
    super.key,
    required this.message,
    required this.isMine,
    required this.onPlayVoiceNote,
  });

  final SCommunicationMessage message;
  final bool isMine;
  final VoidCallback onPlayVoiceNote;

  @override
  Widget build(BuildContext context) {
    final background = isMine ? SColors.primary : SColors.white;
    final foreground = isMine ? SColors.white : SColors.textPrimary;

    return Align(
      alignment: isMine ? Alignment.centerRight : Alignment.centerLeft,
      child: ConstrainedBox(
        constraints: BoxConstraints(
          maxWidth: MediaQuery.sizeOf(context).width * 0.76,
        ),
        child: DecoratedBox(
          decoration: BoxDecoration(
            color: background,
            borderRadius: BorderRadius.circular(SSizes.cardRadiusMd),
          ),
          child: Padding(
            padding: const EdgeInsets.all(SSizes.sm),
            child: _content(context, foreground),
          ),
        ),
      ),
    );
  }

  Widget _content(BuildContext context, Color foreground) {
    if (message.isImage) {
      final url = message.mediaUrl;
      if (url == null || url.isEmpty) {
        return const SizedBox(
          width: 180,
          height: 120,
          child: Center(child: CircularProgressIndicator()),
        );
      }
      return ClipRRect(
        borderRadius: BorderRadius.circular(SSizes.cardRadiusSm),
        child: Image.network(
          url,
          width: 220,
          height: 160,
          fit: BoxFit.cover,
        ),
      );
    }
    if (message.isVoiceNote) {
      return TextButton.icon(
        onPressed: onPlayVoiceNote,
        icon: Icon(Icons.play_arrow, color: foreground),
        label: Text(
          'Voice message',
          style: TextStyle(color: foreground, fontWeight: FontWeight.w700),
        ),
      );
    }
    return Text(
      message.body ?? '',
      style: Theme.of(context).textTheme.bodyMedium?.copyWith(
            color: foreground,
            fontWeight: FontWeight.w600,
          ),
    );
  }
}
