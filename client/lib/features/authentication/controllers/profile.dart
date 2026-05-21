import 'package:flutter/material.dart';
import 'package:get/get.dart';

import '../../../navigation_menu.dart';
import '../repositories/auth_repository.dart';
import 'permissions.dart';
import '../screens/permissions/permissions.dart';
import '../utils/auth_navigation.dart';
import '../../../utils/constants/texts.dart';
import '../../../utils/helpers/helpers.dart';
import '../../../utils/http/client.dart';
import '../../../utils/local_storage/token_storage.dart';
import 'current_user_controller.dart';

class SProfileController extends GetxController {
  SProfileController({required this.registrationToken});

  final String registrationToken;
  final formKey = GlobalKey<FormState>();
  final firstNameController = TextEditingController();
  final lastNameController = TextEditingController();
  final emailController = TextEditingController();
  final RxnString selectedGender = RxnString();
  final Rxn<DateTime> dateOfBirth = Rxn<DateTime>();
  final RxnString genderError = RxnString();
  final RxnString dateOfBirthError = RxnString();
  final RxBool hasAcceptedTerms = false.obs;
  final RxBool isSubmitting = false.obs;

  static const int minimumAge = 13;

  void selectGender(String gender) {
    selectedGender.value = gender;
    genderError.value = null;
  }

  void selectDateOfBirth(DateTime value) {
    dateOfBirth.value = value;
    dateOfBirthError.value = null;
  }

  void toggleTermsAgreement(bool? value) {
    hasAcceptedTerms.value = value ?? false;
  }

  Future<void> submitProfile() async {
    if (isSubmitting.value) return;
    if (!(formKey.currentState?.validate() ?? false)) return;
    if (!_validateProfileDetails()) return;

    if (!hasAcceptedTerms.value) {
      SHelperFunctions.showSnackBar(STexts.acceptTermsRequired);
      return;
    }

    isSubmitting.value = true;
    try {
      final fullName = [
        firstNameController.text.trim(),
        lastNameController.text.trim(),
      ].where((name) => name.isNotEmpty).join(' ');

      final tokens = await SAuthRepository.instance.register(
        registrationToken: registrationToken,
        fullName: fullName,
        email: emailController.text.trim(),
        gender: selectedGender.value!,
        dateOfBirth: _formatDate(dateOfBirth.value!),
      );
      await STokenStorage.saveTokens(
        accessToken: tokens.accessToken,
        refreshToken: tokens.refreshToken,
      );
      await SCurrentUserController.instance.refreshFromBackend();

      SHelperFunctions.showSnackBar(STexts.profileCompleted);
      await _goToPostAuthDestination();
    } on SHttpException catch (error) {
      SHelperFunctions.showSnackBar(error.message);
    } catch (_) {
      SHelperFunctions.showSnackBar(STexts.unexpectedError);
    } finally {
      isSubmitting.value = false;
    }
  }

  bool _validateProfileDetails() {
    var isValid = true;

    if (selectedGender.value == null) {
      genderError.value = STexts.profileGenderRequired;
      isValid = false;
    }

    final birthDate = dateOfBirth.value;
    if (birthDate == null) {
      dateOfBirthError.value = STexts.profileDateOfBirthRequired;
      isValid = false;
    } else if (!_isAtLeastMinimumAge(birthDate)) {
      dateOfBirthError.value = STexts.profileDateOfBirthMinimumAge;
      isValid = false;
    }

    return isValid;
  }

  bool _isAtLeastMinimumAge(DateTime value) {
    final now = DateTime.now();
    final latestAllowed = DateTime(now.year - minimumAge, now.month, now.day);
    final selected = DateTime(value.year, value.month, value.day);
    return !selected.isAfter(latestAllowed);
  }

  String _formatDate(DateTime value) {
    return '${value.year}-${value.month.toString().padLeft(2, '0')}-${value.day.toString().padLeft(2, '0')}';
  }

  Future<void> _goToPostAuthDestination() async {
    final hasRequiredPermissions =
        await SPermissionsController.hasRequiredPermissions();

    if (hasRequiredPermissions) {
      SAuthNavigation.offAll(const NavigationMenu());
      return;
    }

    SAuthNavigation.offAll(const PermissionsScreen());
  }

  @override
  void onClose() {
    firstNameController.dispose();
    lastNameController.dispose();
    emailController.dispose();
    super.onClose();
  }
}
