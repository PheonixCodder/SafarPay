import 'package:client/utils/constants/colors.dart';
import 'package:flutter/material.dart';

import '../../../utils/constants/sizes.dart';
import '../../../utils/constants/texts.dart';

Future<void> showSEditValueDrawer({
  required BuildContext context,
  required String title,
  required String fieldLabel,
  required String currentValue,
  required ValueChanged<String> onSave,
  String description = STexts.editDrawerDefaultDescription,
  String saveLabel = STexts.editDrawerConfirm,
  String cancelLabel = STexts.editDrawerCancel,
  TextInputType keyboardType = TextInputType.text,
  String? Function(String value)? validator,
}) async {
  await showDialog<void>(
    context: context,
    barrierDismissible: false,
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
  late final TextEditingController _controller;
  String? _errorText;

  @override
  void initState() {
    super.initState();
    _controller = TextEditingController(text: widget.currentValue);
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  void _save() {
    final trimmedValue = _controller.text.trim();
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
    return AlertDialog(
      backgroundColor: SColors.white,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(SSizes.borderRadiusLg),
      ),
      title: Text(widget.title),
      content: ConstrainedBox(
        constraints: const BoxConstraints(maxWidth: SSizes.editDrawerMaxWidth),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Text(
              widget.description,
              style: Theme.of(context).textTheme.bodySmall,
            ),
            const SizedBox(height: SSizes.editDrawerFieldGap),
            TextFormField(
              controller: _controller,
              keyboardType: widget.keyboardType,
              autofocus: true,
              decoration: InputDecoration(
                labelText: widget.fieldLabel,
                errorText: _errorText,
              ),
              onChanged: (_) {
                if (_errorText != null) setState(() => _errorText = null);
              },
              onFieldSubmitted: (_) => _save(),
            ),
          ],
        ),
      ),
      actions: [
        TextButton(
          onPressed: () => Navigator.of(context).pop(),
          child: Text(widget.cancelLabel),
        ),
        ElevatedButton(
          onPressed: _save,
          style: ElevatedButton.styleFrom(backgroundColor: SColors.primary,textStyle: const TextStyle( fontSize: SSizes.md - 4)),
          child: Text(widget.saveLabel),
        ),
      ],
    );
  }
}
