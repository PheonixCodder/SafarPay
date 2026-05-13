import 'dart:async';

import 'package:flutter/material.dart';
import 'package:get/get.dart';

import '../../home/screens/home.dart';
import '../models/auth_models.dart';
import '../repositories/auth_repository.dart';
import '../screens/profile/profile.dart';
import '../screens/permissions/permissions.dart';
import '../utils/auth_navigation.dart';
import '../../../utils/constants/texts.dart';
import '../../../utils/helpers/helpers.dart';
import '../../../utils/http/client.dart';
import '../../../utils/local_storage/token_storage.dart';
import 'permissions.dart';

class SOtpController extends GetxController {
  SOtpController({
    required this.phoneNumber,
    required this.flow,
    this.displayName,
  });

  static const int otpLength = 6;
  static const int resendDuration = 30;

  final String phoneNumber;
  final SAuthOtpFlow flow;
  final String? displayName;
  final RxString verificationCode = ''.obs;
  final RxInt resendSecondsRemaining = resendDuration.obs;
  final RxBool isVerifying = false.obs;
  final RxBool isResending = false.obs;

  Timer? _resendTimer;

  bool get canResend => resendSecondsRemaining.value == 0;
  bool get canVerify =>
      verificationCode.value.length == otpLength && !isVerifying.value;
  bool get isGooglePhoneLink => flow == SAuthOtpFlow.googlePhoneLink;
  bool get hasDisplayName => displayName != null && displayName!.isNotEmpty;

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
      final response = await SAuthRepository.instance.verifyOtp(
        phone: phoneNumber,
        code: otp,
      );

      if (flow == SAuthOtpFlow.googlePhoneLink) {
        final tokens = await SAuthRepository.instance.linkGooglePhone(
          verificationToken: response.verificationToken,
        );
        await STokenStorage.saveTokens(
          accessToken: tokens.accessToken,
          refreshToken: tokens.refreshToken,
        );
        SHelperFunctions.showSnackBar(STexts.otpVerified);
        await _goToPostAuthDestination();
        return;
      }

      SAuthNavigation.to(
        CompleteProfileScreen(
          verificationToken: response.verificationToken,
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
      SAuthNavigation.offAll(const HomeScreen());
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
