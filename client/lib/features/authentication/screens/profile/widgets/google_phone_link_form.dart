import 'package:flutter/material.dart';
import 'package:iconsax/iconsax.dart';

import '../../../../../utils/constants/sizes.dart';
import '../../../../../utils/constants/texts.dart';
import '../../../../../utils/validators/validator.dart';

class SGooglePhoneLinkForm extends StatelessWidget {
  const SGooglePhoneLinkForm({
    super.key,
    required this.formKey,
    required this.phoneController,
    required this.isSendingOtp,
    required this.onSubmit,
  });

  final GlobalKey<FormState> formKey;
  final TextEditingController phoneController;
  final bool isSendingOtp;
  final VoidCallback onSubmit;

  @override
  Widget build(BuildContext context) {
    return Form(
      key: formKey,
      child: Column(
        children: [
          TextFormField(
            controller: phoneController,
            keyboardType: TextInputType.phone,
            textInputAction: TextInputAction.done,
            onFieldSubmitted: (_) => onSubmit(),
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
            child: ElevatedButton(
              onPressed: isSendingOtp ? null : onSubmit,
              child: isSendingOtp
                  ? const SizedBox(
                      width: SSizes.iconMd,
                      height: SSizes.iconMd,
                      child: CircularProgressIndicator(strokeWidth: 2),
                    )
                  : const Text(STexts.googlePhoneLinkCta),
            ),
          ),
        ],
      ),
    );
  }
}
