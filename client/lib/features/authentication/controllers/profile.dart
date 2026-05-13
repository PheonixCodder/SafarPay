import 'package:flutter/material.dart';
import 'package:get/get.dart';

import '../../home/screens/home.dart';
import '../repositories/auth_repository.dart';
import 'permissions.dart';
import '../screens/permissions/permissions.dart';
import '../utils/auth_navigation.dart';
import '../../../utils/constants/texts.dart';
import '../../../utils/helpers/helpers.dart';
import '../../../utils/http/client.dart';
import '../../../utils/local_storage/token_storage.dart';

class SProfileController extends GetxController {
  SProfileController({required this.verificationToken});

  final String verificationToken;
  final formKey = GlobalKey<FormState>();
  final firstNameController = TextEditingController();
  final lastNameController = TextEditingController();
  final emailController = TextEditingController();
  final RxBool hasAcceptedTerms = false.obs;
  final RxBool isSubmitting = false.obs;

  void toggleTermsAgreement(bool? value) {
    hasAcceptedTerms.value = value ?? false;
  }

  Future<void> submitProfile() async {
    if (isSubmitting.value) return;
    if (!(formKey.currentState?.validate() ?? false)) return;

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
        verificationToken: verificationToken,
        fullName: fullName,
        email: emailController.text.trim(),
      );
      await STokenStorage.saveTokens(
        accessToken: tokens.accessToken,
        refreshToken: tokens.refreshToken,
      );

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

  Future<void> _goToPostAuthDestination() async {
    final hasRequiredPermissions =
        await SPermissionsController.hasRequiredPermissions();

    if (hasRequiredPermissions) {
      SAuthNavigation.offAll(const HomeScreen());
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
