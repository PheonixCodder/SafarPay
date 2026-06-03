enum SApiService {
  auth,
  gateway,
  location,
  geospatial,
  ride,
  bidding,
  verification,
  payment,
  communication,
  notification,
}

class SApiConstants {
  SApiConstants._();

  static const String authBaseUrl = String.fromEnvironment(
    'SAFARPAY_AUTH_BASE_URL',
    defaultValue: 'http://192.168.100.3:8001/api/v1/auth',
  );
  static const String gatewayBaseUrl = String.fromEnvironment(
    'SAFARPAY_GATEWAY_BASE_URL',
    defaultValue: 'http://192.168.100.3:8000/api/v1',
  );
  static const String locationBaseUrl = String.fromEnvironment(
    'SAFARPAY_LOCATION_BASE_URL',
    defaultValue: 'http://192.168.100.3:8003/api/v1/location',
  );
  static const String geospatialBaseUrl = String.fromEnvironment(
    'SAFARPAY_GEOSPATIAL_BASE_URL',
    defaultValue: 'http://192.168.100.3:8006/api/v1',
  );
  static const String rideBaseUrl = String.fromEnvironment(
    'SAFARPAY_RIDE_BASE_URL',
    defaultValue: 'http://192.168.100.3:8008/api/v1',
  );
  static const String biddingBaseUrl = String.fromEnvironment(
    'SAFARPAY_BIDDING_BASE_URL',
    defaultValue: 'http://192.168.100.3:8002/api/v1/bidding',
  );
  static const String verificationBaseUrl = String.fromEnvironment(
    'SAFARPAY_VERIFICATION_BASE_URL',
    defaultValue: 'http://192.168.100.3:8005/api/v1/verification',
  );
  static const String paymentBaseUrl = String.fromEnvironment(
    'SAFARPAY_PAYMENT_BASE_URL',
    defaultValue: 'http://192.168.100.3:8009/api/v1',
  );
  static const String communicationBaseUrl = String.fromEnvironment(
    'SAFARPAY_COMMUNICATION_BASE_URL',
    defaultValue: 'http://192.168.100.3:8007/api/v1/communication',
  );
  static const String notificationBaseUrl = String.fromEnvironment(
    'SAFARPAY_NOTIFICATION_BASE_URL',
    defaultValue: 'http://192.168.100.3:8004/api/v1/notification',
  );
  static const String mapboxAccessToken = String.fromEnvironment(
    'MAPBOX_ACCESS_TOKEN',
    defaultValue:
        '',
  );
  static const bool useLocationDemoData = bool.fromEnvironment(
    'SAFARPAY_USE_LOCATION_DEMO_DATA',
    defaultValue: false,
  );

  static const Duration connectTimeout = Duration(seconds: 20);

  static String baseUrlFor(SApiService service) {
    return switch (service) {
      SApiService.auth => authBaseUrl,
      SApiService.gateway => gatewayBaseUrl,
      SApiService.location => locationBaseUrl,
      SApiService.geospatial => geospatialBaseUrl,
      SApiService.ride => rideBaseUrl,
      SApiService.bidding => biddingBaseUrl,
      SApiService.verification => verificationBaseUrl,
      SApiService.payment => paymentBaseUrl,
      SApiService.communication => communicationBaseUrl,
      SApiService.notification => notificationBaseUrl,
    };
  }

  static Uri websocketUri(
    SApiService service,
    String endpoint, {
    Map<String, String> queryParameters = const {},
  }) {
    final baseUri = Uri.parse(baseUrlFor(service));
    final wsScheme = baseUri.scheme == 'https' ? 'wss' : 'ws';
    final normalizedEndpoint =
        endpoint.startsWith('/') ? endpoint : '/$endpoint';
    final path = '${baseUri.path}$normalizedEndpoint'.replaceAll('//', '/');

    return baseUri.replace(
      scheme: wsScheme,
      path: path,
      queryParameters: {
        ...baseUri.queryParameters,
        ...queryParameters,
      },
    );
  }
}
