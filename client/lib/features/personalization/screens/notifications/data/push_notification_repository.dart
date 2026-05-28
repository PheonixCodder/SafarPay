import 'package:flutter/foundation.dart';

import '../../../../../utils/constants/api_constants.dart';
import '../../../../../utils/http/client.dart';

class SPushNotificationRepository {
  const SPushNotificationRepository();

  Future<void> registerToken({
    required String token,
    String? driverId,
  }) {
    return SHttpClient.post(
      '/device-tokens',
      service: SApiService.notification,
      requiresAuth: true,
      body: {
        'token': token,
        'platform': _platformName(),
        if (driverId != null && driverId.isNotEmpty) 'driver_id': driverId,
      },
    ).then((_) {});
  }

  Future<void> unregisterToken(String token) {
    return SHttpClient.post(
      '/device-tokens/unregister',
      service: SApiService.notification,
      requiresAuth: true,
      body: {'token': token},
    ).then((_) {});
  }
}

String _platformName() {
  if (kIsWeb) return 'web';
  switch (defaultTargetPlatform) {
    case TargetPlatform.android:
      return 'android';
    case TargetPlatform.iOS:
      return 'ios';
    default:
      return 'unknown';
  }
}
