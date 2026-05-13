import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'package:iconsax/iconsax.dart';

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
        children: [
          TextFormField(
            controller: _phoneController,
            keyboardType: TextInputType.phone,
            textInputAction: TextInputAction.done,
            onFieldSubmitted: (_) => _sendOtp(),
            validator: SValidator.validatePhoneNumber,
            decoration: const InputDecoration(
              labelText: STexts.phoneNo,
              helperText: STexts.phoneHelperText,
              prefixIcon: Icon(Iconsax.call),
            ),
          ),
          const SizedBox(height: SSizes.spaceBtwSections),
          SizedBox(
            width: double.infinity,
            child: Obx(
              () => ElevatedButton(
                onPressed: widget.controller.isSendingOtp.value
                    ? null
                    : _sendOtp,
                child: Text(
                  widget.controller.requiresGooglePhoneLink.value
                      ? STexts.continueText
                      : STexts.sendOtp,
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }
}
