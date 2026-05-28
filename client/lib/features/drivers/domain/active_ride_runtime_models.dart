class SActiveRideRuntimeConfig {
  const SActiveRideRuntimeConfig({
    required this.driverId,
    required this.rideId,
    required this.locationBaseUrl,
    required this.authBaseUrl,
    required this.accessToken,
    required this.status,
    this.refreshToken,
  });

  final String driverId;
  final String rideId;
  final String locationBaseUrl;
  final String authBaseUrl;
  final String accessToken;
  final String status;
  final String? refreshToken;

  Map<String, Object> toMap() {
    return {
      'driver_id': driverId,
      'ride_id': rideId,
      'location_base_url': locationBaseUrl,
      'auth_base_url': authBaseUrl,
      'access_token': accessToken,
      'status': status,
      if (refreshToken != null && refreshToken!.isNotEmpty)
        'refresh_token': refreshToken!,
    };
  }

  factory SActiveRideRuntimeConfig.fromMap(Map<String, Object?> map) {
    return SActiveRideRuntimeConfig(
      driverId: map['driver_id']?.toString() ?? '',
      rideId: map['ride_id']?.toString() ?? '',
      locationBaseUrl: map['location_base_url']?.toString() ?? '',
      authBaseUrl: map['auth_base_url']?.toString() ?? '',
      accessToken: map['access_token']?.toString() ?? '',
      status: map['status']?.toString() ?? '',
      refreshToken: map['refresh_token']?.toString(),
    );
  }

  bool get isValid {
    return driverId.isNotEmpty &&
        rideId.isNotEmpty &&
        locationBaseUrl.isNotEmpty &&
        authBaseUrl.isNotEmpty &&
        accessToken.isNotEmpty;
  }
}

abstract interface class SActiveRideRuntimeService {
  Future<void> start(SActiveRideRuntimeConfig config);

  Future<void> stop();
}
