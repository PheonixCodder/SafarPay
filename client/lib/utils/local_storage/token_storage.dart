import 'package:flutter_secure_storage/flutter_secure_storage.dart';

class STokenStorage {
  STokenStorage._();

  static const _storage = FlutterSecureStorage();
  static const _accessTokenKey = 'access_token';
  static const _refreshTokenKey = 'refresh_token';

  static Future<void> saveTokens({
    required String accessToken,
    String? refreshToken,
  }) async {
    await _storage.write(key: _accessTokenKey, value: accessToken);

    if (refreshToken != null && refreshToken.isNotEmpty) {
      await _storage.write(key: _refreshTokenKey, value: refreshToken);
    }
  }

  static Future<String?> accessToken() {
    return _storage.read(key: _accessTokenKey);
  }

  static Future<String?> refreshToken() {
    return _storage.read(key: _refreshTokenKey);
  }

  static Future<bool> hasAccessToken() async {
    final token = await accessToken();
    return token != null && token.isNotEmpty;
  }

  static Future<void> clear() async {
    await _storage.delete(key: _accessTokenKey);
    await _storage.delete(key: _refreshTokenKey);
  }
}
