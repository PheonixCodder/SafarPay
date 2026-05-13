class SApiConstants {
  SApiConstants._();

  static const String authBaseUrl = String.fromEnvironment(
    'SAFARPAY_AUTH_BASE_URL',
    defaultValue: 'http://10.0.2.2:8001/api/v1/auth',
  );

  static const Duration connectTimeout = Duration(seconds: 20);
}
