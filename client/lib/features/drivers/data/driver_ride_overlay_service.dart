import 'package:flutter/foundation.dart';
import 'package:flutter/services.dart';

class SDriverRideOverlayService {
  const SDriverRideOverlayService();

  static const MethodChannel _channel = MethodChannel('safarpay/driver_overlay');

  Future<bool> canDrawOverlays() async {
    if (defaultTargetPlatform != TargetPlatform.android) return false;
    try {
      return await _channel.invokeMethod<bool>('canDrawOverlays') ?? false;
    } on MissingPluginException {
      return false;
    }
  }

  Future<void> openOverlaySettings() async {
    if (defaultTargetPlatform != TargetPlatform.android) return;
    try {
      await _channel.invokeMethod<void>('openOverlaySettings');
    } on MissingPluginException {
      return;
    }
  }

  Future<void> requestPermissionIfNeeded() async {
    if (defaultTargetPlatform != TargetPlatform.android) return;
    final granted = await canDrawOverlays();
    if (!granted) await openOverlaySettings();
  }

  Future<bool> showRideRequest({
    required String rideId,
    required String title,
    required String body,
    String? deeplink,
  }) async {
    if (defaultTargetPlatform != TargetPlatform.android) return false;
    try {
      return await _channel.invokeMethod<bool>(
            'showDriverRideOverlay',
            {
              'rideId': rideId,
              'title': title,
              'body': body,
              'deeplink': deeplink,
            },
          ) ??
          false;
    } on MissingPluginException {
      return false;
    }
  }

  Future<void> hide() async {
    if (defaultTargetPlatform != TargetPlatform.android) return;
    try {
      await _channel.invokeMethod<void>('hideDriverRideOverlay');
    } on MissingPluginException {
      return;
    }
  }

  Future<Map<String, dynamic>?> consumeLaunchIntent() async {
    if (defaultTargetPlatform != TargetPlatform.android) return null;
    try {
      final value = await _channel.invokeMethod<Object?>('consumeOverlayIntent');
      if (value is Map) return Map<String, dynamic>.from(value);
    } on MissingPluginException {
      return null;
    }
    return null;
  }
}
