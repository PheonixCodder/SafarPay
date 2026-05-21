import 'package:get/get.dart';
import 'package:google_sign_in/google_sign_in.dart';

import '../../../navigation_menu.dart';
import '../models/auth_models.dart';
import '../repositories/auth_repository.dart';
import '../screens/otp/otp.dart';
import '../screens/permissions/permissions.dart';
import '../screens/profile/otp_google.dart';
import '../utils/auth_navigation.dart';
import 'permissions.dart';
import '../../../utils/constants/texts.dart';
import '../../../utils/formatters/phone_number_normalizer.dart';
import '../../../utils/helpers/helpers.dart';
import '../../../utils/http/client.dart';
import '../../../utils/local_storage/token_storage.dart';
import 'current_user_controller.dart';

class SLoginController extends GetxController {
  final RxBool isSendingOtp = false.obs;
  final RxBool isGoogleLoading = false.obs;

  Future<void> sendOtp(String phoneNumber) async {
    if (isSendingOtp.value) return;

    isSendingOtp.value = true;
    try {
      final normalizedPhone =
          SPhoneNumberNormalizer.normalizeForPakistan(phoneNumber);
      if (normalizedPhone == null) {
        SHelperFunctions.showSnackBar('Enter a valid Pakistani phone number.');
        return;
      }

      await SAuthRepository.instance.sendOtp(normalizedPhone);
      SHelperFunctions.showSnackBar(STexts.otpSent);
      SAuthNavigation.to(
        OtpScreen(
          phoneNumber: normalizedPhone,
          flow: SAuthOtpFlow.phoneRegistration,
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
      final googleUser = await GoogleSignIn(
        scopes: ['email'],
        serverClientId:
            '411278048243-um4o8hv7dopg74cj69ja08d4kak193ll.apps.googleusercontent.com',
      ).signIn();
      if (googleUser == null) return;

      final googleAuth = await googleUser.authentication;
      final idToken = googleAuth.idToken;

      if (idToken == null || idToken.isEmpty) {
        SHelperFunctions.showSnackBar(STexts.googleTokenMissing);
        return;
      }

      final tokens = await SAuthRepository.instance.verifyGoogleToken(idToken);

      if (tokens.nextStep == SGoogleAuthNextStep.verifyExistingPhone) {
        final googleLoginToken = tokens.googleLoginToken;
        if (googleLoginToken == null || googleLoginToken.isEmpty) {
          SHelperFunctions.showSnackBar(STexts.unexpectedError);
          return;
        }

        SHelperFunctions.showSnackBar(STexts.otpSent);
        SAuthNavigation.to(
          OtpScreen(
            phoneNumber: tokens.maskedPhone ?? STexts.googleExistingPhoneMasked,
            flow: SAuthOtpFlow.googleExistingEmailPhone,
            displayName: googleUser.displayName,
            googleLoginToken: googleLoginToken,
            maskedPhone: tokens.maskedPhone,
          ),
        );
        return;
      }

      if (tokens.phoneRequired) {
        final accessToken = tokens.accessToken;
        if (accessToken != null && accessToken.isNotEmpty) {
          await STokenStorage.saveTokens(
            accessToken: accessToken,
            refreshToken: tokens.refreshToken,
          );
        }
        SHelperFunctions.showSnackBar(STexts.googlePhoneRequired);
        SAuthNavigation.to(
          GoogleOtpProfileScreen(
            displayName: googleUser.displayName,
            email: googleUser.email,
          ),
        );
        return;
      }

      final accessToken = tokens.accessToken;
      if (accessToken == null || accessToken.isEmpty) {
        SHelperFunctions.showSnackBar(STexts.unexpectedError);
        return;
      }

      await STokenStorage.saveTokens(
        accessToken: accessToken,
        refreshToken: tokens.refreshToken,
      );
      await SCurrentUserController.instance.refreshFromBackend();
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
      SAuthNavigation.offAll(const NavigationMenu());
      return;
    }

    SAuthNavigation.offAll(const PermissionsScreen());
  }
}
