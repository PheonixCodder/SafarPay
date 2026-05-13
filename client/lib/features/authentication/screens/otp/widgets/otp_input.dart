import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

import '../../../../../utils/constants/colors.dart';
import '../../../../../utils/constants/sizes.dart';
import '../../../controllers/otp.dart';

class SOtpInput extends StatefulWidget {
  const SOtpInput({
    super.key,
    required this.controller,
  });

  final SOtpController controller;

  @override
  State<SOtpInput> createState() => _SOtpInputState();
}

class _SOtpInputState extends State<SOtpInput> {
  late final List<TextEditingController> _textControllers;
  late final List<FocusNode> _focusNodes;

  @override
  void initState() {
    super.initState();
    _textControllers = List.generate(
      SOtpController.otpLength,
      (_) => TextEditingController(),
    );
    _focusNodes = List.generate(
      SOtpController.otpLength,
      (_) => FocusNode(),
    );
  }

  @override
  void dispose() {
    for (final controller in _textControllers) {
      controller.dispose();
    }
    for (final node in _focusNodes) {
      node.dispose();
    }
    super.dispose();
  }

  void _handleChanged(int index, String value) {
    final digits = value.replaceAll(RegExp(r'\D'), '');

    if (digits.length == SOtpController.otpLength) {
      _fillCode(digits);
      return;
    }

    final digit = digits.isEmpty ? '' : digits[digits.length - 1];
    _setFieldValue(index, digit);

    if (digit.isNotEmpty && index < SOtpController.otpLength - 1) {
      _focusNodes[index + 1].requestFocus();
    }

    _syncCode();
  }

  void _fillCode(String code) {
    final normalizedCode = code.substring(0, SOtpController.otpLength);

    for (var i = 0; i < SOtpController.otpLength; i++) {
      _setFieldValue(i, normalizedCode[i]);
    }

    _focusNodes.last.requestFocus();
    widget.controller.verifyOtp(normalizedCode);
  }

  void _setFieldValue(int index, String value) {
    final textController = _textControllers[index];

    if (textController.text == value) return;

    textController.value = TextEditingValue(
      text: value,
      selection: TextSelection.collapsed(offset: value.length),
    );
  }

  void _syncCode() {
    final code = _textControllers.map((controller) => controller.text).join();
    widget.controller.updateCode(code);

    if (code.length == SOtpController.otpLength) {
      widget.controller.verifyOtp(code);
    }
  }

  KeyEventResult _handleKeyEvent(int index, KeyEvent event) {
    if (event is! KeyDownEvent ||
        event.logicalKey != LogicalKeyboardKey.backspace ||
        _textControllers[index].text.isNotEmpty) {
      return KeyEventResult.ignored;
    }

    if (index > 0) {
      _focusNodes[index - 1].requestFocus();
      _setFieldValue(index - 1, '');
      _syncCode();
      return KeyEventResult.handled;
    }

    return KeyEventResult.ignored;
  }

  @override
  Widget build(BuildContext context) {
    final textStyle = Theme.of(context).textTheme.headlineSmall?.copyWith(
              color: SColors.textPrimary,
              fontSize: SSizes.fontSizeXl,
            ) ??
        const TextStyle(
          color: SColors.textPrimary,
          fontSize: SSizes.fontSizeXl,
        );

    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: List.generate(
        SOtpController.otpLength,
        (index) => SizedBox(
          width: 42,
          child: Focus(
            onKeyEvent: (_, event) => _handleKeyEvent(index, event),
            child: TextField(
              controller: _textControllers[index],
              focusNode: _focusNodes[index],
              keyboardType: TextInputType.number,
              textInputAction: index == SOtpController.otpLength - 1
                  ? TextInputAction.done
                  : TextInputAction.next,
              textAlign: TextAlign.center,
              style: textStyle,
              cursorColor: SColors.primary,
              inputFormatters: [
                FilteringTextInputFormatter.digitsOnly,
              ],
              decoration: const InputDecoration(
                counterText: '',
                contentPadding: EdgeInsets.only(bottom: SSizes.sm),
                enabledBorder: UnderlineInputBorder(
                  borderSide: BorderSide(
                    color: SColors.borderPrimary,
                    width: 4,
                  ),
                ),
                focusedBorder: UnderlineInputBorder(
                  borderSide: BorderSide(
                    color: SColors.primary,
                    width: 4,
                  ),
                ),
              ),
              onTap: () => _textControllers[index].selection = TextSelection(
                baseOffset: 0,
                extentOffset: _textControllers[index].text.length,
              ),
              onChanged: (value) => _handleChanged(index, value),
              onSubmitted: (_) => widget.controller.verifyOtp(),
            ),
          ),
        ),
      ),
    );
  }
}
