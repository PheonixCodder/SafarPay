import '../../../utils/formatters/phone_number_normalizer.dart';
import '../../../utils/http/client.dart';
import '../../../utils/local_storage/app_mode_storage.dart';
import '../../../utils/local_storage/token_storage.dart';
import '../../../utils/local_storage/user_storage.dart';
import '../models/auth_models.dart';

class SAuthRepository {
  SAuthRepository._();

  static final SAuthRepository instance = SAuthRepository._();

  Future<void> sendOtp(String phone) async {
    await SHttpClient.post(
      '/otp/send',
      body: {'phone': _normalizePhone(phone)},
    );
  }

  Future<SOtpVerifyResponse> verifyOtp({
    required String phone,
    required String code,
    String purpose = 'phone_login',
  }) async {
    final response = await SHttpClient.post(
      '/otp/verify',
      body: {
        'phone': _normalizePhone(phone),
        'code': code,
        'purpose': purpose,
      },
    );
    return SOtpVerifyResponse.fromJson(response);
  }

  Future<STokenResponse> register({
    required String registrationToken,
    required String fullName,
    required String email,
    required String gender,
    required String dateOfBirth,
  }) async {
    final response = await SHttpClient.post(
      '/register',
      body: {
        'registration_token': registrationToken,
        'full_name': fullName,
        'email': email,
        'gender': gender,
        'date_of_birth': dateOfBirth,
      },
    );
    return STokenResponse.fromJson(response);
  }

  Future<SUserResponse> updateProfile({
    String? fullName,
    String? email,
    String? gender,
    String? dateOfBirth,
  }) async {
    final body = <String, dynamic>{
      if (fullName != null) 'full_name': fullName,
      if (email != null) 'email': email,
      if (gender != null) 'gender': gender,
      if (dateOfBirth != null) 'date_of_birth': dateOfBirth,
    };
    final response = await SHttpClient.patch(
      '/me',
      body: body,
      requiresAuth: true,
    );
    return SUserResponse.fromJson(response);
  }

  Future<SGoogleAuthResponse> verifyGoogleToken(String idToken) async {
    final response = await SHttpClient.post(
      '/google/verify-token',
      body: {'id_token': idToken},
    );
    return SGoogleAuthResponse.fromJson(response);
  }

  Future<STokenResponse> verifyGoogleExistingPhone({
    required String googleLoginToken,
    required String code,
  }) async {
    final response = await SHttpClient.post(
      '/google/verify-existing-phone',
      body: {
        'google_login_token': googleLoginToken,
        'code': code,
      },
    );
    return STokenResponse.fromJson(response);
  }

  Future<STokenResponse> linkGooglePhone({
    required String verificationToken,
  }) async {
    final response = await SHttpClient.post(
      '/google/link-phone',
      body: {'verification_token': verificationToken},
      requiresAuth: true,
    );
    return STokenResponse.fromJson(response);
  }

  Future<STokenResponse> refresh({String? refreshToken}) async {
    final token = refreshToken ?? await STokenStorage.refreshToken();
    final response = await SHttpClient.post(
      '/refresh',
      body: token == null ? null : {'refresh_token': token},
    );
    return STokenResponse.fromJson(response);
  }

  Future<SUserResponse> getCurrentUser() async {
    final response = await SHttpClient.get('/me', requiresAuth: true);
    return SUserResponse.fromJson(response);
  }

  Future<void> logout() async {
    try {
      await SHttpClient.post('/logout', requiresAuth: true);
    } finally {
      await STokenStorage.clear();
      await SUserStorage.clear();
      await SAppModeStorage.clear();
    }
  }

  String _normalizePhone(String phone) {
    final normalized = SPhoneNumberNormalizer.normalizeForPakistan(phone);
    if (normalized == null) {
      throw const SHttpException(
        message: 'Enter a valid Pakistani phone number.',
        statusCode: 0,
      );
    }

    return normalized;
  }
}
