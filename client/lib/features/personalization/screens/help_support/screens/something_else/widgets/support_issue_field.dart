import 'package:flutter/material.dart';

import '../../../../../../../utils/constants/colors.dart';
import '../../../../../../../utils/constants/sizes.dart';

class SSupportIssueField extends StatelessWidget {
  const SSupportIssueField({
    super.key,
    required this.controller,
    required this.onChanged,
    required this.currentLength,
  });

  final TextEditingController controller;
  final ValueChanged<String> onChanged;
  final int currentLength;

  @override
  Widget build(BuildContext context) {
    final textTheme = Theme.of(context).textTheme;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            Text(
              'Describe your issue',
              style: textTheme.labelLarge?.copyWith(
                color: SColors.textPrimary,
                fontWeight: FontWeight.w800,
              ),
            ),
            Text(
              ' *',
              style: textTheme.labelLarge?.copyWith(
                color: SColors.error,
                fontWeight: FontWeight.w800,
              ),
            ),
          ],
        ),
        const SizedBox(height: SSizes.sm),
        TextField(
          controller: controller,
          onChanged: onChanged,
          maxLines: 6,
          minLines: 5,
          textInputAction: TextInputAction.newline,
          decoration: InputDecoration(
            hintText: 'Write here...',
            filled: true,
            fillColor: SColors.white,
            alignLabelWithHint: true,
            contentPadding: const EdgeInsets.all(SSizes.md),
            border: OutlineInputBorder(
              borderRadius: BorderRadius.circular(SSizes.inputFieldRadius),
              borderSide: const BorderSide(color: SColors.borderSecondary),
            ),
            enabledBorder: OutlineInputBorder(
              borderRadius: BorderRadius.circular(SSizes.inputFieldRadius),
              borderSide: const BorderSide(color: SColors.borderSecondary),
            ),
            focusedBorder: OutlineInputBorder(
              borderRadius: BorderRadius.circular(SSizes.inputFieldRadius),
              borderSide: const BorderSide(color: SColors.primary),
            ),
          ),
        ),
        const SizedBox(height: SSizes.xs),
        Align(
          alignment: Alignment.centerRight,
          child: Text(
            '$currentLength/1000',
            style: textTheme.labelSmall?.copyWith(
              color: SColors.textSecondary,
              fontWeight: FontWeight.w600,
            ),
          ),
        ),
      ],
    );
  }
}
