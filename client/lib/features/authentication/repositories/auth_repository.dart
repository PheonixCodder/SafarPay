import '../../../utils/http/client.dart';
import '../../../utils/local_storage/token_storage.dart';
import '../models/auth_models.dart';

class SAuthRepository {
  SAuthRepository._();

  static final SAuthRepository instance = SAuthRepository._();

  Future<void> sendOtp(String phone) async {
    // --- Original API call (commented out) ---
    // await SHttpClient.post(
    //   '/otp/send',
    //   body: {'phone': phone},
    // );

    // --- Mock implementation ---
    // Simulate a short network delay for realistic behavior (optional)
    await Future.delayed(const Duration(milliseconds: 500));
    // No return value needed
  }

  Future<SOtpVerifyResponse> verifyOtp({
    required String phone,
    required String code,
  }) async {
    // --- Original API call (commented out) ---
    // final response = await SHttpClient.post(
    //   '/otp/verify',
    //   body: {
    //     'phone': phone,
    //     'code': code,
    //   },
    // );
    // return SOtpVerifyResponse.fromJson(response);

    // --- Mock implementation ---
    await Future.delayed(const Duration(milliseconds: 500));
    // Return a dummy verification token. Accept any 6‑digit code.
    if (code.length != 6) {
      throw const SHttpException(
        message: 'Invalid OTP code',
        statusCode: 400,
      );
    }
    return const SOtpVerifyResponse(
      verificationToken: 'mock_verification_token_123',
    );
  }

  Future<STokenResponse> register({
    required String verificationToken,
    required String fullName,
    required String email,
  }) async {
    // --- Original API call (commented out) ---
    // final response = await SHttpClient.post(
    //   '/register',
    //   body: {
    //     'verification_token': verificationToken,
    //     'full_name': fullName,
    //     'email': email,
    //   },
    // );
    // return STokenResponse.fromJson(response);

    // --- Mock implementation ---
    await Future.delayed(const Duration(milliseconds: 500));
    return const STokenResponse(
      accessToken: 'mock_access_token_123',
      refreshToken: 'mock_refresh_token_123',
      tokenType: 'bearer',
      expiresIn: 900,
      phoneRequired: false,
    );
  }

  Future<STokenResponse> verifyGoogleToken(String idToken) async {
    // --- Original API call (commented out) ---
    // final response = await SHttpClient.post(
    //   '/google/verify-token',
    //   body: {'id_token': idToken},
    // );
    // return STokenResponse.fromJson(response);

    // --- Mock implementation ---
    await Future.delayed(const Duration(milliseconds: 500));
    // For testing: set phoneRequired to true to exercise the Google phone-link flow.
    // Change to false if you want to skip that flow.
    final phoneRequired = bool.fromEnvironment(
      'MOCK_GOOGLE_PHONE_REQUIRED',
      defaultValue: true,
    );
    return STokenResponse(
      accessToken: phoneRequired ? '' : 'mock_google_access_token',
      refreshToken: phoneRequired ? '' : 'mock_google_refresh_token',
      tokenType: 'bearer',
      expiresIn: 900,
      phoneRequired: phoneRequired,
    );
  }

  Future<STokenResponse> linkGooglePhone({
    required String verificationToken,
  }) async {
    // --- Original API call (commented out) ---
    // final response = await SHttpClient.post(
    //   '/google/link-phone',
    //   body: {'verification_token': verificationToken},
    //   requiresAuth: true,
    // );
    // return STokenResponse.fromJson(response);

    // --- Mock implementation ---
    await Future.delayed(const Duration(milliseconds: 500));
    return const STokenResponse(
      accessToken: 'mock_linked_google_access_token',
      refreshToken: 'mock_linked_google_refresh_token',
      tokenType: 'bearer',
      expiresIn: 900,
      phoneRequired: false,
    );
  }

  Future<STokenResponse> refresh({String? refreshToken}) async {
    // --- Original API call (commented out) ---
    // final token = refreshToken ?? await STokenStorage.refreshToken();
    // final response = await SHttpClient.post(
    //   '/refresh',
    //   body: token == null ? null : {'refresh_token': token},
    // );
    // return STokenResponse.fromJson(response);

    // --- Mock implementation ---
    await Future.delayed(const Duration(milliseconds: 500));
    return const STokenResponse(
      accessToken: 'mock_refreshed_access_token',
      refreshToken: 'mock_refreshed_refresh_token',
      tokenType: 'bearer',
      expiresIn: 900,
      phoneRequired: false,
    );
  }

  Future<SUserResponse> getCurrentUser() async {
    // --- Original API call (commented out) ---
    // final response = await SHttpClient.get('/me', requiresAuth: true);
    // return SUserResponse.fromJson(response);

    // --- Mock implementation ---
    await Future.delayed(const Duration(milliseconds: 500));
    return const SUserResponse(
      id: 'mock_user_id',
      role: 'user',
      isActive: true,
      isVerified: true,
      isOnboarded: true,
      fullName: 'Mock User',
      email: 'mock@example.com',
      phone: '+1234567890',
      profileImage: null,
    );
  }

  Future<void> logout() async {
    // --- Original API call (commented out) ---
    // try {
    //   await SHttpClient.post('/logout', requiresAuth: true);
    // } finally {
    //   await STokenStorage.clear();
    // }

    // --- Mock implementation ---
    await Future.delayed(const Duration(milliseconds: 300));
    await STokenStorage.clear();
  }
}
