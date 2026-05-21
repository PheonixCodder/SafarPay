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

enum SGoogleAuthNextStep {
  login,
  verifyExistingPhone,
}

class SGoogleAuthResponse {
  const SGoogleAuthResponse({
    required this.phoneRequired,
    this.nextStep,
    this.accessToken,
    this.tokenType = 'bearer',
    this.expiresIn,
    this.refreshToken,
    this.maskedPhone,
    this.googleLoginToken,
  });

  final SGoogleAuthNextStep? nextStep;
  final String? accessToken;
  final String tokenType;
  final int? expiresIn;
  final String? refreshToken;
  final bool phoneRequired;
  final String? maskedPhone;
  final String? googleLoginToken;

  factory SGoogleAuthResponse.fromJson(Map<String, dynamic> json) {
    return SGoogleAuthResponse(
      nextStep: _parseNextStep(json['next_step'] as String?),
      accessToken: json['access_token'] as String?,
      tokenType: json['token_type'] as String? ?? 'bearer',
      expiresIn: json['expires_in'] as int?,
      refreshToken: json['refresh_token'] as String?,
      phoneRequired: json['phone_required'] as bool? ?? false,
      maskedPhone: json['masked_phone'] as String?,
      googleLoginToken: json['google_login_token'] as String?,
    );
  }

  static SGoogleAuthNextStep? _parseNextStep(String? value) {
    return switch (value) {
      'verify_existing_phone' => SGoogleAuthNextStep.verifyExistingPhone,
      'login' => SGoogleAuthNextStep.login,
      _ => null,
    };
  }
}

enum SAuthOtpNextStep {
  login,
  completeProfile,
  linkPhone,
}

class SOtpVerifyResponse {
  const SOtpVerifyResponse({
    required this.nextStep,
    this.registrationToken,
    this.accessToken,
    this.tokenType = 'bearer',
    this.expiresIn,
    this.refreshToken,
    this.phoneRequired = false,
  });

  final SAuthOtpNextStep nextStep;
  final String? registrationToken;
  final String? accessToken;
  final String tokenType;
  final int? expiresIn;
  final String? refreshToken;
  final bool phoneRequired;

  factory SOtpVerifyResponse.fromJson(Map<String, dynamic> json) {
    return SOtpVerifyResponse(
      nextStep: _parseNextStep(json['next_step'] as String?),
      registrationToken: json['registration_token'] as String?,
      accessToken: json['access_token'] as String?,
      tokenType: json['token_type'] as String? ?? 'bearer',
      expiresIn: json['expires_in'] as int?,
      refreshToken: json['refresh_token'] as String?,
      phoneRequired: json['phone_required'] as bool? ?? false,
    );
  }

  static SAuthOtpNextStep _parseNextStep(String? value) {
    return switch (value) {
      'login' => SAuthOtpNextStep.login,
      'link_phone' => SAuthOtpNextStep.linkPhone,
      _ => SAuthOtpNextStep.completeProfile,
    };
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
    this.gender,
    this.dateOfBirth,
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
  final String? gender;
  final String? dateOfBirth;
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
      gender: json['gender'] as String?,
      dateOfBirth: json['date_of_birth'] as String?,
      profileImage: json['profile_img'] as String?,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'role': role,
      'is_active': isActive,
      'is_verified': isVerified,
      'is_onboarded': isOnboarded,
      'full_name': fullName,
      'email': email,
      'phone': phone,
      'gender': gender,
      'date_of_birth': dateOfBirth,
      'profile_img': profileImage,
    };
  }

  SUserResponse copyWith({
    String? id,
    String? role,
    bool? isActive,
    bool? isVerified,
    bool? isOnboarded,
    String? fullName,
    String? email,
    String? phone,
    String? gender,
    String? dateOfBirth,
    String? profileImage,
  }) {
    return SUserResponse(
      id: id ?? this.id,
      role: role ?? this.role,
      isActive: isActive ?? this.isActive,
      isVerified: isVerified ?? this.isVerified,
      isOnboarded: isOnboarded ?? this.isOnboarded,
      fullName: fullName ?? this.fullName,
      email: email ?? this.email,
      phone: phone ?? this.phone,
      gender: gender ?? this.gender,
      dateOfBirth: dateOfBirth ?? this.dateOfBirth,
      profileImage: profileImage ?? this.profileImage,
    );
  }
}

enum SAuthOtpFlow {
  phoneRegistration,
  googlePhoneLink,
  googleExistingEmailPhone,
}
