import 'dart:async';

import 'package:flutter/material.dart';

import '../../../../common/widgets/appbar/appbar.dart';
import '../../../../common/widgets/drawers/edit_value_drawer.dart';
import '../../../../common/widgets/images/circular_image.dart';
import '../../../authentication/controllers/current_user_controller.dart';
import '../../../authentication/repositories/auth_repository.dart';
import '../../../../utils/constants/images.dart';
import '../../../../utils/constants/sizes.dart';
import '../../../../utils/constants/texts.dart';
import '../../../../utils/helpers/helpers.dart';
import '../../../../utils/http/client.dart';
import '../../../../utils/validators/validator.dart';
import 'widgets/profile_menu.dart';
import 'widgets/section_heading.dart';

class ProfileScreen extends StatefulWidget {
  const ProfileScreen({super.key});

  @override
  State<ProfileScreen> createState() => _ProfileScreenState();
}

class _ProfileScreenState extends State<ProfileScreen> {
  final SCurrentUserController _userController = SCurrentUserController.instance;
  late String _name;
  late String _email;
  late String _phoneNumber;
  late String _gender;
  late String _dateOfBirth;

  @override
  void initState() {
    super.initState();
    final user = _userController.currentUser.value;
    _name = _safeValue(user?.fullName, STexts.currentUserFallbackName);
    _email = _safeValue(user?.email, STexts.currentUserNoEmail);
    _phoneNumber = _safeValue(user?.phone, STexts.currentUserNoPhone);
    _gender = _formatGender(user?.gender);
    _dateOfBirth = _safeValue(user?.dateOfBirth, STexts.profileNotSet);
  }

  void _openEditValuePopup({
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

  Future<void> _saveProfileChanges({
    String? fullName,
    String? email,
    String? gender,
    String? dateOfBirth,
  }) async {
    try {
      final user = await SAuthRepository.instance.updateProfile(
        fullName: fullName,
        email: email,
        gender: gender,
        dateOfBirth: dateOfBirth,
      );
      await _userController.cacheUser(user);
      if (!mounted) return;
      setState(() {
        _name = _safeValue(user.fullName, STexts.currentUserFallbackName);
        _email = _safeValue(user.email, STexts.currentUserNoEmail);
        _phoneNumber = _safeValue(user.phone, STexts.currentUserNoPhone);
        _gender = _formatGender(user.gender);
        _dateOfBirth = _safeValue(user.dateOfBirth, STexts.profileNotSet);
      });
      SHelperFunctions.showSnackBar(STexts.profileUpdated);
    } on SHttpException catch (error) {
      SHelperFunctions.showSnackBar(error.message);
    } catch (_) {
      SHelperFunctions.showSnackBar(STexts.unexpectedError);
    }
  }

  Future<void> _openGenderPicker() async {
    final selected = await showModalBottomSheet<String>(
      context: context,
      builder: (context) => SafeArea(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            ListTile(
              title: const Text(STexts.profileGenderMale),
              onTap: () => Navigator.of(context).pop('male'),
            ),
            ListTile(
              title: const Text(STexts.profileGenderFemale),
              onTap: () => Navigator.of(context).pop('female'),
            ),
            ListTile(
              title: const Text(STexts.profileGenderOther),
              onTap: () => Navigator.of(context).pop('other'),
            ),
          ],
        ),
      ),
    );
    if (selected == null) return;
    await _saveProfileChanges(gender: selected);
  }

  Future<void> _openDateOfBirthPicker() async {
    final now = DateTime.now();
    final latestAllowed = DateTime(now.year - 13, now.month, now.day);
    final initialDate = _parseDate(_dateOfBirth) ?? DateTime(1998);
    final picked = await showDatePicker(
      context: context,
      firstDate: DateTime(1900),
      lastDate: latestAllowed,
      initialDate: initialDate.isAfter(latestAllowed) ? latestAllowed : initialDate,
    );
    if (picked == null) return;
    await _saveProfileChanges(dateOfBirth: _formatDate(picked));
  }

  String _safeValue(String? value, String fallback) {
    return value == null || value.trim().isEmpty ? fallback : value;
  }

  String _formatGender(String? value) {
    return switch (value) {
      'male' => STexts.profileGenderMale,
      'female' => STexts.profileGenderFemale,
      'other' => STexts.profileGenderOther,
      _ => STexts.profileNotSet,
    };
  }

  DateTime? _parseDate(String value) {
    if (value == STexts.profileNotSet) return null;
    return DateTime.tryParse(value);
  }

  String _formatDate(DateTime value) {
    return '${value.year}-${value.month.toString().padLeft(2, '0')}-${value.day.toString().padLeft(2, '0')}';
  }

  @override
  Widget build(BuildContext context) {
    final profileImage = _userController.currentUser.value?.profileImage;
    final hasNetworkImage =
        profileImage != null && profileImage.startsWith('http');

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
                    SCircularImage(
                      imageUrl: profileImage ?? SImages.user,
                      isNetworkImage: hasNetworkImage,
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
                onPressed: () => _openEditValuePopup(
                  fieldLabel: STexts.profileName,
                  currentValue: _name,
                  validator: (value) => SValidator.validateNotEmpty(
                    value,
                    fieldName: STexts.profileName,
                  ),
                  onSave: (value) {
                    _name = value;
                    unawaited(_saveProfileChanges(fullName: value));
                  },
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
                onPressed: () => _openEditValuePopup(
                  fieldLabel: STexts.profileEmail,
                  currentValue: _email,
                  keyboardType: TextInputType.emailAddress,
                  validator: SValidator.validateEmail,
                  onSave: (value) {
                    _email = value;
                    unawaited(_saveProfileChanges(email: value));
                  },
                ),
              ),
              SProfileMenu(
                title: STexts.profilePhoneNumber,
                value: _phoneNumber,
                onPressed: () {},
              ),
              SProfileMenu(
                title: STexts.profileGender,
                value: _gender,
                onPressed: _openGenderPicker,
              ),
              SProfileMenu(
                key: const ValueKey('profile-date-of-birth-menu'),
                title: STexts.profileDateOfBirth,
                value: _dateOfBirth,
                onPressed: _openDateOfBirthPicker,
              ),
            ],
          ),
        ),
      ),
    );
  }
}
