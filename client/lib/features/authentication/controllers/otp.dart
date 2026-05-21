import 'dart:async';

import 'package:get/get.dart';

import '../../../navigation_menu.dart';
import '../models/auth_models.dart';
import '../repositories/auth_repository.dart';
import '../screens/profile/profile.dart';
import '../screens/permissions/permissions.dart';
import '../utils/auth_navigation.dart';
import '../../../utils/constants/texts.dart';
import '../../../utils/formatters/phone_number_normalizer.dart';
import '../../../utils/helpers/helpers.dart';
import '../../../utils/http/client.dart';
import '../../../utils/local_storage/token_storage.dart';
import 'current_user_controller.dart';
import 'permissions.dart';

class SOtpController extends GetxController {
  SOtpController({
    required String phoneNumber,
    required this.flow,
    this.displayName,
    this.googleLoginToken,
    this.maskedPhone,
  }) : phoneNumber =
           SPhoneNumberNormalizer.normalizeForPakistan(phoneNumber) ??
           phoneNumber;

  static const int otpLength = 6;
  static const int resendDuration = 30;

  final String phoneNumber;
  final SAuthOtpFlow flow;
  final String? displayName;
  final String? googleLoginToken;
  final String? maskedPhone;
  final RxString verificationCode = ''.obs;
  final RxInt resendSecondsRemaining = resendDuration.obs;
  final RxBool isVerifying = false.obs;
  final RxBool isResending = false.obs;

  Timer? _resendTimer;

  bool get canResend => resendSecondsRemaining.value == 0;
  bool get canVerify =>
      verificationCode.value.length == otpLength && !isVerifying.value;
  bool get isGooglePhoneLink => flow == SAuthOtpFlow.googlePhoneLink;
  bool get isGoogleExistingEmailPhone =>
      flow == SAuthOtpFlow.googleExistingEmailPhone;
  bool get hasDisplayName => displayName != null && displayName!.isNotEmpty;
  String get phoneDisplay => maskedPhone ?? phoneNumber;

  @override
  void onInit() {
    super.onInit();
    startResendCountdown();
  }

  void updateCode(String code) {
    verificationCode.value = code;
  }

  Future<void> verifyOtp([String? code]) async {
    if (isVerifying.value) return;

    final otp = code ?? verificationCode.value;
    verificationCode.value = otp;

    if (otp.length != otpLength) {
      SHelperFunctions.showSnackBar(STexts.invalidOtp);
      return;
    }

    isVerifying.value = true;
    try {
      if (flow == SAuthOtpFlow.googleExistingEmailPhone) {
        final token = googleLoginToken;
        if (token == null || token.isEmpty) {
          SHelperFunctions.showSnackBar(STexts.unexpectedError);
          return;
        }

        final tokens = await SAuthRepository.instance.verifyGoogleExistingPhone(
          googleLoginToken: token,
          code: otp,
        );
        await STokenStorage.saveTokens(
          accessToken: tokens.accessToken,
          refreshToken: tokens.refreshToken,
        );
        await SCurrentUserController.instance.refreshFromBackend();
        SHelperFunctions.showSnackBar(STexts.otpVerified);
        await _goToPostAuthDestination();
        return;
      }

      final response = await SAuthRepository.instance.verifyOtp(
        phone: phoneNumber,
        code: otp,
        purpose: isGooglePhoneLink ? 'phone_link' : 'phone_login',
      );

      if (flow == SAuthOtpFlow.googlePhoneLink) {
        final registrationToken = response.registrationToken;
        if (registrationToken == null || registrationToken.isEmpty) {
          SHelperFunctions.showSnackBar(STexts.unexpectedError);
          return;
        }

        final tokens = await SAuthRepository.instance.linkGooglePhone(
          verificationToken: registrationToken,
        );
        await STokenStorage.saveTokens(
          accessToken: tokens.accessToken,
          refreshToken: tokens.refreshToken,
        );
        await SCurrentUserController.instance.refreshFromBackend();
        SHelperFunctions.showSnackBar(STexts.otpVerified);
        await _goToPostAuthDestination();
        return;
      }

      if (response.nextStep == SAuthOtpNextStep.login) {
        final accessToken = response.accessToken;
        if (accessToken == null || accessToken.isEmpty) {
          SHelperFunctions.showSnackBar(STexts.unexpectedError);
          return;
        }

        await STokenStorage.saveTokens(
          accessToken: accessToken,
          refreshToken: response.refreshToken,
        );
        await SCurrentUserController.instance.refreshFromBackend();
        SHelperFunctions.showSnackBar(STexts.otpVerified);
        await _goToPostAuthDestination();
        return;
      }

      final registrationToken = response.registrationToken;
      if (registrationToken == null || registrationToken.isEmpty) {
        SHelperFunctions.showSnackBar(STexts.unexpectedError);
        return;
      }

      SAuthNavigation.to(
        CompleteProfileScreen(
          registrationToken: registrationToken,
        ),
      );
    } on SHttpException catch (error) {
      SHelperFunctions.showSnackBar(error.message);
    } catch (_) {
      SHelperFunctions.showSnackBar(STexts.unexpectedError);
    } finally {
      isVerifying.value = false;
    }
  }

  Future<void> resendOtp() async {
    if (!canResend || isResending.value) return;

    isResending.value = true;
    try {
      if (isGoogleExistingEmailPhone) {
        SHelperFunctions.showSnackBar(STexts.googleExistingPhoneResendHint);
        return;
      }

      await SAuthRepository.instance.sendOtp(phoneNumber);
      SHelperFunctions.showSnackBar(STexts.otpSentWhatsapp);
      startResendCountdown();
    } on SHttpException catch (error) {
      SHelperFunctions.showSnackBar(error.message);
    } catch (_) {
      SHelperFunctions.showSnackBar(STexts.unexpectedError);
    } finally {
      isResending.value = false;
    }
  }

  void changeNumber() {
    Get.back();
  }

  void startResendCountdown() {
    _resendTimer?.cancel();
    resendSecondsRemaining.value = resendDuration;

    _resendTimer = Timer.periodic(const Duration(seconds: 1), (timer) {
      if (resendSecondsRemaining.value <= 1) {
        resendSecondsRemaining.value = 0;
        timer.cancel();
        return;
      }

      resendSecondsRemaining.value--;
    });
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

  @override
  void onClose() {
    _resendTimer?.cancel();
    super.onClose();
  }
}
