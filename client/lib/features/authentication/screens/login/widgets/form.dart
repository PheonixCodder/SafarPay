import 'package:flutter/material.dart';
import 'package:get/get.dart';

import '../../../../../utils/constants/colors.dart';
import '../../../../../utils/constants/sizes.dart';
import '../../../../../utils/constants/texts.dart';
import '../../../../../utils/device/utility.dart';
import '../../../../../utils/validators/validator.dart';
import '../../../controllers/login.dart';

class SLoginForm extends StatefulWidget {
  const SLoginForm({
    super.key,
    required this.controller,
  });

  final SLoginController controller;

  @override
  State<SLoginForm> createState() => _SLoginFormState();
}

class _SLoginFormState extends State<SLoginForm> {
  final _formKey = GlobalKey<FormState>();
  final _phoneController = TextEditingController();

  @override
  void dispose() {
    _phoneController.dispose();
    super.dispose();
  }

  void _sendOtp() {
    SDeviceUtils.hideKeyboard(context);

    if (!(_formKey.currentState?.validate() ?? false)) return;

    widget.controller.sendOtp(_phoneController.text.trim());
  }

  @override
  Widget build(BuildContext context) {
    return Form(
      key: _formKey,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            "Enter Your Phone number",
            style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                  fontWeight: FontWeight.bold,
                  color: SColors.textPrimary,
                ),
          ),
          const SizedBox(height: SSizes.sm),
          Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Container(
                height: 56,
                padding: const EdgeInsets.symmetric(horizontal: 16),
                decoration: BoxDecoration(
                  color: SColors.light,
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(color: SColors.borderPrimary),
                ),
                child: Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    const Text(
                      '🇵🇰',
                      style: TextStyle(fontSize: 24),
                    ),
                    const SizedBox(width: 8),
                    Text(
                      '+92',
                      style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                            fontWeight: FontWeight.bold,
                            color: SColors.textPrimary,
                          ),
                    ),
                  ],
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: TextFormField(
                  controller: _phoneController,
                  keyboardType: TextInputType.phone,
                  textInputAction: TextInputAction.done,
                  onFieldSubmitted: (_) => _sendOtp(),
                  validator: SValidator.validatePhoneNumber,
                  decoration: InputDecoration(
                    hintText: '300 1234567',
                    fillColor: SColors.light,
                    filled: true,
                    contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 18),
                    border: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(12),
                      borderSide: const BorderSide(color: SColors.borderPrimary),
                    ),
                    enabledBorder: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(12),
                      borderSide: const BorderSide(color: SColors.borderPrimary),
                    ),
                    focusedBorder: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(12),
                      borderSide: const BorderSide(color: SColors.primary, width: 1.5),
                    ),
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: SSizes.spaceBtwSections),
          SizedBox(
            width: double.infinity,
            child: Obx(
              () => ElevatedButton(
                onPressed:
                    widget.controller.isSendingOtp.value ? null : _sendOtp,
                style: ElevatedButton.styleFrom(
                  backgroundColor: SColors.primaryContainer,
                  foregroundColor: SColors.onPrimary,
                  disabledBackgroundColor: SColors.buttonDisabled,
                  disabledForegroundColor: SColors.onSurfaceVariant,
                  padding: const EdgeInsets.symmetric(vertical: 18),
                  shape: const StadiumBorder(),
                ),
                child: const Text(STexts.continueText),
              ),
            ),
          ),
        ],
      ),
    );
  }
}
