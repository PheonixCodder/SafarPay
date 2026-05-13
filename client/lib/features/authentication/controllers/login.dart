import 'package:get/get.dart';
import 'package:google_sign_in/google_sign_in.dart';

import '../../home/screens/home.dart';
import '../models/auth_models.dart';
import '../repositories/auth_repository.dart';
import '../screens/otp/otp.dart';
import '../screens/permissions/permissions.dart';
import '../utils/auth_navigation.dart';
import 'permissions.dart';
import '../../../utils/constants/texts.dart';
import '../../../utils/helpers/helpers.dart';
import '../../../utils/http/client.dart';
import '../../../utils/local_storage/token_storage.dart';

class SLoginController extends GetxController {
  final RxBool isSendingOtp = false.obs;
  final RxBool isGoogleLoading = false.obs;
  final RxBool requiresGooglePhoneLink = false.obs;
  final RxString googleDisplayName = ''.obs;

  Future<void> sendOtp(String phoneNumber) async {
    if (isSendingOtp.value) return;

    isSendingOtp.value = true;
    try {
      await SAuthRepository.instance.sendOtp(phoneNumber);
      SHelperFunctions.showSnackBar(STexts.otpSent);
      SAuthNavigation.to(
        OtpScreen(
          phoneNumber: phoneNumber,
          flow: requiresGooglePhoneLink.value
              ? SAuthOtpFlow.googlePhoneLink
              : SAuthOtpFlow.phoneRegistration,
          displayName: requiresGooglePhoneLink.value
              ? googleDisplayName.value
              : null,
        ),
      );
    } on SHttpException catch (error) {
      SHelperFunctions.showSnackBar(error.message);
    } catch (_) {
      SHelperFunctions.showSnackBar(STexts.unexpectedError);
    } finally {
      isSendingOtp.value = false;
    }
  }

  Future<void> loginWithGoogle() async {
    if (isGoogleLoading.value) return;

    isGoogleLoading.value = true;
    try {
      final googleUser = await GoogleSignIn(scopes: ['email'], serverClientId: '411278048243-um4o8hv7dopg74cj69ja08d4kak193ll.apps.googleusercontent.com').signIn();
      if (googleUser == null) return;

      final googleAuth = await googleUser.authentication;
      final idToken = googleAuth.idToken;

      if (idToken == null || idToken.isEmpty) {
        SHelperFunctions.showSnackBar(STexts.googleTokenMissing);
        return;
      }

      final tokens = await SAuthRepository.instance.verifyGoogleToken(idToken);
      await STokenStorage.saveTokens(
        accessToken: tokens.accessToken,
        refreshToken: tokens.refreshToken,
      );

      if (tokens.phoneRequired) {
        requiresGooglePhoneLink.value = true;
        googleDisplayName.value = googleUser.displayName ?? '';
        SHelperFunctions.showSnackBar(STexts.googlePhoneRequired);
        return;
      }

      requiresGooglePhoneLink.value = false;
      googleDisplayName.value = '';
      await _goToPostAuthDestination();
    } on SHttpException catch (error) {
      SHelperFunctions.showSnackBar(error.message);
    } catch (e) {
      SHelperFunctions.showSnackBar(STexts.googleLoginFailed);
    } finally {
      isGoogleLoading.value = false;
    }
  }

  Future<void> _goToPostAuthDestination() async {
    final permissionsCompleted =
        await SPermissionsController.hasRequiredPermissions();

    if (permissionsCompleted) {
      SAuthNavigation.offAll(const HomeScreen());
      return;
    }

    SAuthNavigation.offAll(const PermissionsScreen());
  }
}
