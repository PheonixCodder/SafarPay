import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'package:iconsax/iconsax.dart';

import '../../../../../utils/constants/sizes.dart';
import '../../../../../utils/constants/texts.dart';
import '../../../../../utils/validators/validator.dart';
import '../../../controllers/profile.dart';
import 'profile_terms_agreement.dart';

class SProfileForm extends StatelessWidget {
  const SProfileForm({
    super.key,
    required this.controller,
  });

  final SProfileController controller;

  @override
  Widget build(BuildContext context) {
    return Form(
      key: controller.formKey,
      child: Column(
        children: [
          TextFormField(
            controller: controller.firstNameController,
            textInputAction: TextInputAction.next,
            validator: (value) => SValidator.validateNotEmpty(
              value,
              fieldName: STexts.firstName,
            ),
            decoration: const InputDecoration(
              labelText: STexts.firstName,
              prefixIcon: Icon(Iconsax.user),
            ),
          ),
          const SizedBox(height: SSizes.spaceBtwInputFields),
          TextFormField(
            controller: controller.lastNameController,
            textInputAction: TextInputAction.next,
            validator: (value) => SValidator.validateNotEmpty(
              value,
              fieldName: STexts.lastName,
            ),
            decoration: const InputDecoration(
              labelText: STexts.lastName,
              prefixIcon: Icon(Iconsax.user),
            ),
          ),
          const SizedBox(height: SSizes.spaceBtwInputFields),
          TextFormField(
            controller: controller.emailController,
            keyboardType: TextInputType.emailAddress,
            textInputAction: TextInputAction.done,
            onFieldSubmitted: (_) => controller.submitProfile(),
            validator: SValidator.validateEmail,
            decoration: const InputDecoration(
              labelText: STexts.emailAddress,
              prefixIcon: Icon(Iconsax.sms),
            ),
          ),
          const SizedBox(height: SSizes.spaceBtwSections),
          SProfileTermsAgreement(controller: controller),
          const SizedBox(height: SSizes.spaceBtwSections),
          SizedBox(
            width: double.infinity,
            child: Obx(
              () => ElevatedButton(
                onPressed:
                    controller.isSubmitting.value ? null : controller.submitProfile,
                child: const Text(STexts.continueText),
              ),
            ),
          ),
        ],
      ),
    );
  }
}
