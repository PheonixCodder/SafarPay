import 'package:client/utils/constants/colors.dart';
import 'package:flutter/material.dart';
import 'package:shadcn_ui/shadcn_ui.dart';

import '../../../utils/constants/sizes.dart';
import '../../../utils/constants/texts.dart';

Future<void> showSEditValueDrawer({
  required BuildContext context,
  required String title,
  required String fieldLabel,
  required String currentValue,
  required ValueChanged<String> onSave,
  String description = STexts.editDrawerDefaultDescription,
  String saveLabel = STexts.editDrawerSave,
  String cancelLabel = STexts.editDrawerCancel,
  TextInputType keyboardType = TextInputType.text,
  String? Function(String value)? validator,
}) async {
  await showShadSheet<void>(
    context: context,
    side: ShadSheetSide.right,
    builder: (context) => SEditValueDrawer(
      title: title,
      description: description,
      fieldLabel: fieldLabel,
      currentValue: currentValue,
      saveLabel: saveLabel,
      cancelLabel: cancelLabel,
      keyboardType: keyboardType,
      validator: validator,
      onSave: onSave,
    ),
  );
}

class SEditValueDrawer extends StatefulWidget {
  const SEditValueDrawer({
    super.key,
    required this.title,
    required this.description,
    required this.fieldLabel,
    required this.currentValue,
    required this.saveLabel,
    required this.cancelLabel,
    required this.keyboardType,
    required this.onSave,
    this.validator,
  });

  final String title;
  final String description;
  final String fieldLabel;
  final String currentValue;
  final String saveLabel;
  final String cancelLabel;
  final TextInputType keyboardType;
  final String? Function(String value)? validator;
  final ValueChanged<String> onSave;

  @override
  State<SEditValueDrawer> createState() => _SEditValueDrawerState();
}

class _SEditValueDrawerState extends State<SEditValueDrawer> {
  late String _value = widget.currentValue;
  String? _errorText;

  void _save() {
    final trimmedValue = _value.trim();
    final validationError = widget.validator?.call(trimmedValue);

    if (validationError != null) {
      setState(() => _errorText = validationError);
      return;
    }

    if (trimmedValue.isEmpty) {
      setState(() => _errorText = STexts.editDrawerRequired);
      return;
    }

    widget.onSave(trimmedValue);
    Navigator.of(context).pop();
  }

  @override
  Widget build(BuildContext context) {
    return ShadSheet(
      constraints: const BoxConstraints(maxWidth: SSizes.editDrawerMaxWidth),
      title: Text(widget.title),
      description: Text(widget.description),
      actions: [
        ShadButton.outline(
          onPressed: () => Navigator.of(context).pop(),
          child: Text(widget.cancelLabel),
        ),
        ShadButton(
          onPressed: _save,
          backgroundColor: SColors.primary,
          child: Text(widget.saveLabel),
        ),
      ],
      child: Padding(
        padding: const EdgeInsets.symmetric(
          vertical: SSizes.editDrawerVerticalPadding,
        ),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            ShadInput(
              initialValue: widget.currentValue,
              keyboardType: widget.keyboardType,
              placeholder: Text(widget.fieldLabel),
              onChanged: (value) {
                _value = value;
                if (_errorText != null) setState(() => _errorText = null);
              },
            ),
            if (_errorText != null)
              const SizedBox(height: SSizes.editDrawerFieldGap),
            if (_errorText != null)
              Text(
                _errorText!,
                style: Theme.of(context).textTheme.bodySmall?.copyWith(
                  color: Theme.of(context).colorScheme.error,
                ),
              ),
          ],
        ),
      ),
    );
  }
}
