import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'package:iconsax/iconsax.dart';

import '../../../../personalization/screens/driver_registration/widgets/driver_registration_date_field.dart';
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

  Future<void> _selectDateOfBirth(BuildContext context) async {
    final now = DateTime.now();
    final latestAllowed = DateTime(
      now.year - SProfileController.minimumAge,
      now.month,
      now.day,
    );
    final picked = await showDatePicker(
      context: context,
      firstDate: DateTime(1900),
      lastDate: latestAllowed,
      initialDate: controller.dateOfBirth.value ?? DateTime(1998),
    );
    if (picked != null) controller.selectDateOfBirth(picked);
  }

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
            textInputAction: TextInputAction.next,
            validator: SValidator.validateEmail,
            decoration: const InputDecoration(
              labelText: STexts.emailAddress,
              prefixIcon: Icon(Iconsax.sms),
            ),
          ),
          const SizedBox(height: SSizes.spaceBtwInputFields),
          Obx(
            () => Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Align(
                  alignment: Alignment.centerLeft,
                  child: Text(
                    STexts.profileGender,
                    style: Theme.of(context).textTheme.labelLarge,
                  ),
                ),
                const SizedBox(height: SSizes.sm),
                Wrap(
                  spacing: SSizes.sm,
                  runSpacing: SSizes.sm,
                  children: [
                    _GenderChip(
                      label: STexts.profileGenderMale,
                      value: 'male',
                      controller: controller,
                    ),
                    _GenderChip(
                      label: STexts.profileGenderFemale,
                      value: 'female',
                      controller: controller,
                    ),
                    _GenderChip(
                      label: STexts.profileGenderOther,
                      value: 'other',
                      controller: controller,
                    ),
                  ],
                ),
                if (controller.genderError.value != null)
                  Padding(
                    padding: const EdgeInsets.only(top: SSizes.xs),
                    child: Text(
                      controller.genderError.value!,
                      style: Theme.of(context).textTheme.bodySmall?.copyWith(
                            color: Theme.of(context).colorScheme.error,
                          ),
                    ),
                  ),
              ],
            ),
          ),
          const SizedBox(height: SSizes.spaceBtwInputFields),
          Obx(
            () => SDriverRegistrationDateField(
              label: STexts.profileDateOfBirth,
              value: controller.dateOfBirth.value,
              error: controller.dateOfBirthError.value,
              onTap: () => _selectDateOfBirth(context),
            ),
          ),
          const SizedBox(height: SSizes.spaceBtwSections),
          SProfileTermsAgreement(controller: controller),
          const SizedBox(height: SSizes.spaceBtwSections),
          SizedBox(
            width: double.infinity,
            child: Obx(
              () => ElevatedButton(
                onPressed: controller.isSubmitting.value
                    ? null
                    : controller.submitProfile,
                child: const Text(STexts.continueText),
              ),
            ),
          ),
        ],
      ),
    );
  }
}

class _GenderChip extends StatelessWidget {
  const _GenderChip({
    required this.label,
    required this.value,
    required this.controller,
  });

  final String label;
  final String value;
  final SProfileController controller;

  @override
  Widget build(BuildContext context) {
    return Obx(
      () => ChoiceChip(
        label: Text(label),
        selected: controller.selectedGender.value == value,
        onSelected: (_) => controller.selectGender(value),
      ),
    );
  }
}
