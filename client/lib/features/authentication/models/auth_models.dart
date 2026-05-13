class STokenResponse {
  const STokenResponse({
    required this.accessToken,
    required this.tokenType,
    required this.expiresIn,
    required this.phoneRequired,
    this.refreshToken,
  });

  final String accessToken;
  final String tokenType;
  final int expiresIn;
  final bool phoneRequired;
  final String? refreshToken;

  factory STokenResponse.fromJson(Map<String, dynamic> json) {
    return STokenResponse(
      accessToken: json['access_token'] as String,
      tokenType: json['token_type'] as String? ?? 'bearer',
      expiresIn: json['expires_in'] as int? ?? 900,
      phoneRequired: json['phone_required'] as bool? ?? false,
      refreshToken: json['refresh_token'] as String?,
    );
  }
}

class SOtpVerifyResponse {
  const SOtpVerifyResponse({required this.verificationToken});

  final String verificationToken;

  factory SOtpVerifyResponse.fromJson(Map<String, dynamic> json) {
    return SOtpVerifyResponse(
      verificationToken: json['verification_token'] as String,
    );
  }
}

class SUserResponse {
  const SUserResponse({
    required this.id,
    required this.role,
    required this.isActive,
    required this.isVerified,
    required this.isOnboarded,
    this.fullName,
    this.email,
    this.phone,
    this.profileImage,
  });

  final String id;
  final String role;
  final bool isActive;
  final bool isVerified;
  final bool isOnboarded;
  final String? fullName;
  final String? email;
  final String? phone;
  final String? profileImage;

  factory SUserResponse.fromJson(Map<String, dynamic> json) {
    return SUserResponse(
      id: json['id'] as String,
      role: json['role'] as String,
      isActive: json['is_active'] as bool? ?? false,
      isVerified: json['is_verified'] as bool? ?? false,
      isOnboarded: json['is_onboarded'] as bool? ?? false,
      fullName: json['full_name'] as String?,
      email: json['email'] as String?,
      phone: json['phone'] as String?,
      profileImage: json['profile_img'] as String?,
    );
  }
}

enum SAuthOtpFlow {
  phoneRegistration,
  googlePhoneLink,
}
