import 'dart:async';
import 'dart:convert';

import 'package:http/http.dart' as http;

import '../constants/api_constants.dart';
import '../local_storage/token_storage.dart';
import '../logging/logger.dart';

class SHttpException implements Exception {
  const SHttpException({
    required this.message,
    required this.statusCode,
    this.body,
  });

  final String message;
  final int statusCode;
  final dynamic body;

  bool get isUnauthorized => statusCode == 401;

  @override
  String toString() => message;
}

class SHttpClient {
  SHttpClient._();

  static final http.Client _client = http.Client();
  static Future<bool>? _refreshInFlight;

  static Future<Map<String, dynamic>> get(
    String endpoint, {
    SApiService service = SApiService.auth,
    bool requiresAuth = false,
  }) {
    return _send(
      'GET',
      endpoint,
      service: service,
      requiresAuth: requiresAuth,
    );
  }

  static Future<Map<String, dynamic>> post(
    String endpoint, {
    SApiService service = SApiService.auth,
    Map<String, dynamic>? body,
    bool requiresAuth = false,
  }) {
    return _send(
      'POST',
      endpoint,
      service: service,
      body: body,
      requiresAuth: requiresAuth,
    );
  }

  static Future<Map<String, dynamic>> patch(
    String endpoint, {
    SApiService service = SApiService.auth,
    Map<String, dynamic>? body,
    bool requiresAuth = false,
  }) {
    return _send(
      'PATCH',
      endpoint,
      service: service,
      body: body,
      requiresAuth: requiresAuth,
    );
  }

  static Future<void> delete(
    String endpoint, {
    SApiService service = SApiService.auth,
    bool requiresAuth = true,
  }) async {
    await _send(
      'DELETE',
      endpoint,
      service: service,
      requiresAuth: requiresAuth,
    );
  }

  static Future<void> putBytesToAbsoluteUrl(
    String url, {
    required List<int> bytes,
    String contentType = 'image/jpeg',
  }) async {
    final uri = Uri.parse(url);
    final headers = <String, String>{
      'Content-Type': contentType,
    };

    SLoggerHelper.info('PUT ${uri.host}${uri.path}');

    try {
      final response = await _client
          .put(uri, headers: headers, body: bytes)
          .timeout(SApiConstants.connectTimeout);

      if (response.statusCode < 200 || response.statusCode >= 300) {
        throw SHttpException(
          message: 'Document upload failed. Please try again.',
          statusCode: response.statusCode,
          body: response.body,
        );
      }
    } on TimeoutException catch (error) {
      SLoggerHelper.error('Document upload timed out', error);
      throw const SHttpException(
        message: 'Document upload timed out. Please try again.',
        statusCode: 0,
      );
    } on SHttpException {
      rethrow;
    } catch (error) {
      SLoggerHelper.error('Document upload failed', error);
      throw const SHttpException(
        message: 'Unable to upload document. Please check your connection.',
        statusCode: 0,
      );
    }
  }

  static Future<String?> accessTokenForSocket() async {
    final token = await STokenStorage.accessToken();
    if (token == null || token.isEmpty) return null;

    if (_tokenExpiresSoon(token)) {
      await _refreshToken();
    }
    return STokenStorage.accessToken();
  }

  static Future<Map<String, dynamic>> _send(
    String method,
    String endpoint, {
    SApiService service = SApiService.auth,
    Map<String, dynamic>? body,
    bool requiresAuth = false,
    bool allowRefresh = true,
  }) async {
    final response = await _rawRequest(
      method,
      endpoint,
      service: service,
      body: body,
      requiresAuth: requiresAuth,
    );

    if (response.statusCode == 401 && requiresAuth && allowRefresh) {
      final refreshed = await _refreshToken();
      if (refreshed) {
        return _send(
          method,
          endpoint,
          service: service,
          body: body,
          requiresAuth: requiresAuth,
          allowRefresh: false,
        );
      }
    }

    return _handleResponse(response);
  }

  static Future<http.Response> _rawRequest(
    String method,
    String endpoint, {
    SApiService service = SApiService.auth,
    Map<String, dynamic>? body,
    bool requiresAuth = false,
  }) async {
    final baseUrl = SApiConstants.baseUrlFor(service);
    final uri = Uri.parse('$baseUrl$endpoint');
    final headers = <String, String>{
      'Accept': 'application/json',
      'Content-Type': 'application/json',
    };

    if (requiresAuth) {
      final accessToken = await STokenStorage.accessToken();
      if (accessToken != null && accessToken.isNotEmpty) {
        headers['Authorization'] = 'Bearer $accessToken';
      }
    }

    SLoggerHelper.info('$method ${uri.path}');

    try {
      return switch (method) {
        'GET' => _client
            .get(uri, headers: headers)
            .timeout(SApiConstants.connectTimeout),
        'POST' => _client
            .post(uri, headers: headers, body: jsonEncode(body ?? {}))
            .timeout(SApiConstants.connectTimeout),
        'PATCH' => _client
            .patch(uri, headers: headers, body: jsonEncode(body ?? {}))
            .timeout(SApiConstants.connectTimeout),
        'DELETE' => _client
            .delete(uri, headers: headers)
            .timeout(SApiConstants.connectTimeout),
        _ => throw const SHttpException(
            message: 'Unsupported request method.',
            statusCode: 0,
          ),
      };
    } on TimeoutException catch (error) {
      SLoggerHelper.error('Request timed out', error);
      throw const SHttpException(
        message: 'Request timed out. Please try again.',
        statusCode: 0,
      );
    } on SHttpException {
      rethrow;
    } catch (error) {
      SLoggerHelper.error('Network request failed', error);
      throw const SHttpException(
        message: 'Unable to connect. Please check your internet connection.',
        statusCode: 0,
      );
    }
  }

  static Map<String, dynamic> _handleResponse(http.Response response) {
    final body = _decodeBody(response.body);

    if (response.statusCode >= 200 && response.statusCode < 300) {
      if (body == null) return {};
      if (body is Map<String, dynamic>) return body;

      return {'data': body};
    }

    final message = _extractErrorMessage(body, response.statusCode);
    SLoggerHelper.warning('HTTP ${response.statusCode}: $message');

    throw SHttpException(
      message: message,
      statusCode: response.statusCode,
      body: body,
    );
  }

  static dynamic _decodeBody(String body) {
    if (body.isEmpty) return null;

    try {
      return jsonDecode(body);
    } catch (_) {
      return body;
    }
  }

  static String _extractErrorMessage(dynamic body, int statusCode) {
    if (body is Map<String, dynamic>) {
      final detail = body['detail'];
      if (detail is String && detail.isNotEmpty) return detail;
      if (detail is List && detail.isNotEmpty) {
        final firstError = detail.first;
        if (firstError is Map<String, dynamic> && firstError['msg'] is String) {
          return firstError['msg'] as String;
        }
      }
      if (body['message'] is String) return body['message'] as String;
    }

    return switch (statusCode) {
      400 => 'Please check your details and try again.',
      401 => 'Your session has expired. Please login again.',
      409 => 'This account already exists.',
      429 => 'Too many requests. Please try again later.',
      500 => 'Server error. Please try again later.',
      _ => 'Request failed. Please try again.',
    };
  }

  static Future<bool> _refreshToken() {
    final inFlight = _refreshInFlight;
    if (inFlight != null) return inFlight;

    final refresh = _refreshTokenInternal();
    _refreshInFlight = refresh;
    return refresh.whenComplete(() => _refreshInFlight = null);
  }

  static Future<bool> _refreshTokenInternal() async {
    final refreshToken = await STokenStorage.refreshToken();
    if (refreshToken == null || refreshToken.isEmpty) return false;

    try {
      final response = await _rawRequest(
        'POST',
        '/refresh',
        body: {'refresh_token': refreshToken},
      );
      final data = _handleResponse(response);
      final accessToken = data['access_token'] as String?;
      final newRefreshToken = data['refresh_token'] as String?;

      if (accessToken == null || accessToken.isEmpty) return false;

      await STokenStorage.saveTokens(
        accessToken: accessToken,
        refreshToken: newRefreshToken,
      );
      return true;
    } catch (error) {
      SLoggerHelper.error('Token refresh failed', error);
      await STokenStorage.clear();
      return false;
    }
  }

  static bool _tokenExpiresSoon(String token) {
    try {
      final parts = token.split('.');
      if (parts.length < 2) return false;
      final payload = utf8.decode(base64Url.decode(base64Url.normalize(parts[1])));
      final data = jsonDecode(payload);
      if (data is! Map<String, dynamic>) return false;
      final exp = data['exp'];
      if (exp is! num) return false;
      final expiry = DateTime.fromMillisecondsSinceEpoch(
        exp.toInt() * 1000,
        isUtc: true,
      );
      return expiry
          .subtract(const Duration(minutes: 1))
          .isBefore(DateTime.now().toUtc());
    } catch (_) {
      return false;
    }
  }
}
