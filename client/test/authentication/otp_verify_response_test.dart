import 'package:client/features/authentication/models/auth_models.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  test('OTP verify response parses existing-user login result', () {
    final response = SOtpVerifyResponse.fromJson({
      'next_step': 'login',
      'access_token': 'access',
      'refresh_token': 'refresh',
      'token_type': 'bearer',
      'expires_in': 900,
      'phone_required': false,
    });

    expect(response.nextStep, SAuthOtpNextStep.login);
    expect(response.accessToken, 'access');
    expect(response.refreshToken, 'refresh');
    expect(response.registrationToken, isNull);
  });

  test('OTP verify response parses new-user profile completion result', () {
    final response = SOtpVerifyResponse.fromJson({
      'next_step': 'complete_profile',
      'registration_token': 'registration-token',
    });

    expect(response.nextStep, SAuthOtpNextStep.completeProfile);
    expect(response.registrationToken, 'registration-token');
    expect(response.accessToken, isNull);
  });

  test('OTP verify response parses Google phone-link result', () {
    final response = SOtpVerifyResponse.fromJson({
      'next_step': 'link_phone',
      'registration_token': 'registration-token',
    });

    expect(response.nextStep, SAuthOtpNextStep.linkPhone);
    expect(response.registrationToken, 'registration-token');
  });
}
