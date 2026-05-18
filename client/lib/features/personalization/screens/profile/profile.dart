import 'package:flutter/material.dart';

import '../../../../common/widgets/appbar/appbar.dart';
import '../../../../common/widgets/drawers/edit_value_drawer.dart';
import '../../../../common/widgets/images/circular_image.dart';
import '../../../../utils/constants/images.dart';
import '../../../../utils/constants/sizes.dart';
import '../../../../utils/constants/texts.dart';
import '../../../../utils/validators/validator.dart';
import 'widgets/profile_menu.dart';
import 'widgets/section_heading.dart';

class ProfileScreen extends StatefulWidget {
  const ProfileScreen({super.key});

  @override
  State<ProfileScreen> createState() => _ProfileScreenState();
}

class _ProfileScreenState extends State<ProfileScreen> {
  late String _name = STexts.profileDemoName;
  late String _email = STexts.profileDemoEmail;
  late String _phoneNumber = STexts.profileDemoPhone;
  late String _gender = STexts.profileDemoGender;
  late String _dateOfBirth = STexts.profileDemoDateOfBirth;

  void _openEditDrawer({
    required String fieldLabel,
    required String currentValue,
    required ValueChanged<String> onSave,
    TextInputType keyboardType = TextInputType.text,
    String? Function(String value)? validator,
  }) {
    showSEditValueDrawer(
      context: context,
      title: '${STexts.editDrawerTitlePrefix} $fieldLabel',
      description: STexts.profileEditDescription,
      fieldLabel: fieldLabel,
      currentValue: currentValue,
      keyboardType: keyboardType,
      validator: validator,
      onSave: (value) => setState(() => onSave(value)),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: const SAppBar(
        showBackArrow: true,
        title: Text(STexts.profileTitle),
      ),
      body: SingleChildScrollView(
        child: Padding(
          padding: const EdgeInsets.all(SSizes.defaultSpace),
          child: Column(
            children: [
              SizedBox(
                width: double.infinity,
                child: Column(
                  children: [
                    const SCircularImage(
                      imageUrl: SImages.user,
                      width: 80,
                      height: 80,
                    ),
                    TextButton(
                      onPressed: () {},
                      child: const Text(STexts.changeProfilePicture),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: SSizes.spaceBtwItems / 2),
              const Divider(),
              const SizedBox(height: SSizes.spaceBtwItems),
              const SSectionHeading(
                title: STexts.profileInformation,
                showActionButton: false,
              ),
              const SizedBox(height: SSizes.spaceBtwItems),
              SProfileMenu(
                title: STexts.profileName,
                value: _name,
                onPressed: () => _openEditDrawer(
                  fieldLabel: STexts.profileName,
                  currentValue: _name,
                  validator: (value) => SValidator.validateNotEmpty(
                    value,
                    fieldName: STexts.profileName,
                  ),
                  onSave: (value) => _name = value,
                ),
              ),
              const SizedBox(height: SSizes.spaceBtwSections),
              const SSectionHeading(
                title: STexts.personalInformation,
                showActionButton: false,
              ),
              const SizedBox(height: SSizes.spaceBtwItems),
              SProfileMenu(
                title: STexts.profileEmail,
                value: _email,
                onPressed: () => _openEditDrawer(
                  fieldLabel: STexts.profileEmail,
                  currentValue: _email,
                  keyboardType: TextInputType.emailAddress,
                  validator: SValidator.validateEmail,
                  onSave: (value) => _email = value,
                ),
              ),
              SProfileMenu(
                title: STexts.profilePhoneNumber,
                value: _phoneNumber,
                onPressed: () => _openEditDrawer(
                  fieldLabel: STexts.profilePhoneNumber,
                  currentValue: _phoneNumber,
                  keyboardType: TextInputType.phone,
                  validator: SValidator.validatePhoneNumber,
                  onSave: (value) => _phoneNumber = value,
                ),
              ),
              SProfileMenu(
                title: STexts.profileGender,
                value: _gender,
                onPressed: () => _openEditDrawer(
                  fieldLabel: STexts.profileGender,
                  currentValue: _gender,
                  validator: (value) => SValidator.validateNotEmpty(
                    value,
                    fieldName: STexts.profileGender,
                  ),
                  onSave: (value) => _gender = value,
                ),
              ),
              SProfileMenu(
                title: STexts.profileDateOfBirth,
                value: _dateOfBirth,
                onPressed: () => _openEditDrawer(
                  fieldLabel: STexts.profileDateOfBirth,
                  currentValue: _dateOfBirth,
                  validator: (value) => SValidator.validateNotEmpty(
                    value,
                    fieldName: STexts.profileDateOfBirth,
                  ),
                  onSave: (value) => _dateOfBirth = value,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
