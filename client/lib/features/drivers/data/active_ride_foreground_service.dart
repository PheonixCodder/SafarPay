import 'dart:async';
import 'dart:convert';
import 'dart:io';

import 'package:flutter_foreground_task/flutter_foreground_task.dart';
import 'package:geolocator/geolocator.dart';
import 'package:http/http.dart' as http;

import '../../../utils/logging/logger.dart';
import '../domain/active_ride_runtime_models.dart';

class SActiveRideForegroundService implements SActiveRideRuntimeService {
  const SActiveRideForegroundService();

  static const int _serviceId = 7901;
  static const String _configKey = 'active_ride_runtime_config';

  static void initializeCommunication() {
    FlutterForegroundTask.initCommunicationPort();
  }

  static void initializeService() {
    FlutterForegroundTask.init(
      androidNotificationOptions: AndroidNotificationOptions(
        channelId: 'active_ride_runtime',
        channelName: 'Active ride tracking',
        channelDescription:
            'Keeps active driver trips visible and location tracking running.',
        onlyAlertOnce: true,
      ),
      iosNotificationOptions: const IOSNotificationOptions(
        showNotification: false,
        playSound: false,
      ),
      foregroundTaskOptions: ForegroundTaskOptions(
        eventAction: ForegroundTaskEventAction.repeat(8000),
        autoRunOnBoot: false,
        autoRunOnMyPackageReplaced: false,
        allowWakeLock: true,
        allowWifiLock: true,
      ),
    );
  }

  @override
  Future<void> start(SActiveRideRuntimeConfig config) async {
    if (!config.isValid) return;
    await _requestRuntimePermissions();
    await FlutterForegroundTask.saveData(
      key: _configKey,
      value: jsonEncode(config.toMap()),
    );
    initializeService();

    final title = 'Active ride running';
    final text = _notificationText(config.status);
    if (await FlutterForegroundTask.isRunningService) {
      await FlutterForegroundTask.restartService();
      await FlutterForegroundTask.updateService(
        notificationTitle: title,
        notificationText: text,
      );
      return;
    }

    await FlutterForegroundTask.startService(
      serviceId: _serviceId,
      serviceTypes: const [ForegroundServiceTypes.location],
      notificationTitle: title,
      notificationText: text,
      notificationInitialRoute: '/',
      callback: safarPayActiveRideRuntimeStartCallback,
    );
  }

  @override
  Future<void> stop() async {
    await FlutterForegroundTask.removeData(key: _configKey);
    if (await FlutterForegroundTask.isRunningService) {
      await FlutterForegroundTask.stopService();
    }
  }

  static Future<SActiveRideRuntimeConfig?> runtimeConfig() async {
    final raw = await FlutterForegroundTask.getData(key: _configKey);
    if (raw == null) return null;
    final decoded = jsonDecode(raw.toString());
    if (decoded is! Map) return null;
    return SActiveRideRuntimeConfig.fromMap(
      decoded.cast<String, Object?>(),
    );
  }
}

@pragma('vm:entry-point')
void safarPayActiveRideRuntimeStartCallback() {
  FlutterForegroundTask.setTaskHandler(_ActiveRideRuntimeTaskHandler());
}

class _ActiveRideRuntimeTaskHandler extends TaskHandler {
  @override
  Future<void> onStart(DateTime timestamp, TaskStarter starter) async {
    await _sendLocationUpdate();
  }

  @override
  void onRepeatEvent(DateTime timestamp) {
    unawaited(_sendLocationUpdate());
  }

  @override
  Future<void> onDestroy(DateTime timestamp, bool isTimeout) async {}

  Future<void> _sendLocationUpdate({bool allowRefresh = true}) async {
    final config = await SActiveRideForegroundService.runtimeConfig();
    if (config == null || !config.isValid) {
      await FlutterForegroundTask.stopService();
      return;
    }

    try {
      final permission = await _ensureLocationPermission();
      if (!permission) return;

      final position = await Geolocator.getCurrentPosition(
        locationSettings: const LocationSettings(
          accuracy: LocationAccuracy.high,
          timeLimit: Duration(seconds: 12),
        ),
      );

      final uri = Uri.parse(
        '${config.locationBaseUrl}/drivers/${config.driverId}/location',
      );
      final response = await http
          .post(
            uri,
            headers: {
              'Accept': 'application/json',
              'Content-Type': 'application/json',
              'Authorization': 'Bearer ${config.accessToken}',
            },
            body: jsonEncode({
              'lat': position.latitude,
              'lng': position.longitude,
              'accuracy': position.accuracy,
              'speed': position.speed >= 0 ? position.speed * 3.6 : null,
              'heading': position.heading >= 0 ? position.heading : null,
              'ts': DateTime.now().millisecondsSinceEpoch,
              'ride_id': config.rideId,
            }),
          )
          .timeout(const Duration(seconds: 20));

      if (response.statusCode == 401) {
        if (allowRefresh) {
          final refreshed = await _refreshAccessToken(config);
          if (refreshed != null) {
            await FlutterForegroundTask.saveData(
              key: SActiveRideForegroundService._configKey,
              value: jsonEncode(refreshed.toMap()),
            );
            await _sendLocationUpdate(allowRefresh: false);
            return;
          }
        }
        await FlutterForegroundTask.stopService();
        return;
      }

      if (response.statusCode == 403) {
        await FlutterForegroundTask.stopService();
        return;
      }

      if (response.statusCode >= 200 && response.statusCode < 300) {
        FlutterForegroundTask.updateService(
          notificationTitle: 'Active ride running',
          notificationText: 'Location shared just now',
        );
        FlutterForegroundTask.sendDataToMain({
          'event': 'active_ride_location_sent',
          'ride_id': config.rideId,
          'lat': position.latitude,
          'lng': position.longitude,
        });
      }
    } catch (error) {
      SLoggerHelper.warning(
          'Active ride runtime location update failed: $error');
    }
  }
}

Future<SActiveRideRuntimeConfig?> _refreshAccessToken(
  SActiveRideRuntimeConfig config,
) async {
  final refreshToken = config.refreshToken;
  if (refreshToken == null || refreshToken.isEmpty) return null;
  final response = await http
      .post(
        Uri.parse('${config.authBaseUrl}/refresh'),
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json',
        },
        body: jsonEncode({'refresh_token': refreshToken}),
      )
      .timeout(const Duration(seconds: 20));
  if (response.statusCode < 200 || response.statusCode >= 300) return null;

  final decoded = jsonDecode(response.body);
  if (decoded is! Map<String, dynamic>) return null;
  final accessToken = decoded['access_token']?.toString();
  if (accessToken == null || accessToken.isEmpty) return null;
  final nextRefreshToken = decoded['refresh_token']?.toString();

  return SActiveRideRuntimeConfig(
    driverId: config.driverId,
    rideId: config.rideId,
    locationBaseUrl: config.locationBaseUrl,
    authBaseUrl: config.authBaseUrl,
    accessToken: accessToken,
    refreshToken: nextRefreshToken == null || nextRefreshToken.isEmpty
        ? refreshToken
        : nextRefreshToken,
    status: config.status,
  );
}

Future<void> _requestRuntimePermissions() async {
  final permission = await Geolocator.checkPermission();
  if (permission == LocationPermission.denied) {
    final nextPermission = await Geolocator.requestPermission();
    if (nextPermission == LocationPermission.deniedForever) {
      await Geolocator.openAppSettings();
    }
  } else if (permission == LocationPermission.deniedForever) {
    await Geolocator.openAppSettings();
  }

  final notificationPermission =
      await FlutterForegroundTask.checkNotificationPermission();
  if (notificationPermission != NotificationPermission.granted) {
    await FlutterForegroundTask.requestNotificationPermission();
  }

  if (Platform.isAndroid &&
      !await FlutterForegroundTask.isIgnoringBatteryOptimizations) {
    await FlutterForegroundTask.requestIgnoreBatteryOptimization();
  }
}

Future<bool> _ensureLocationPermission() async {
  final serviceEnabled = await Geolocator.isLocationServiceEnabled();
  if (!serviceEnabled) return false;

  var permission = await Geolocator.checkPermission();
  if (permission == LocationPermission.denied) {
    permission = await Geolocator.requestPermission();
  }
  if (permission == LocationPermission.deniedForever) {
    await Geolocator.openAppSettings();
    return false;
  }

  return permission == LocationPermission.always ||
      permission == LocationPermission.whileInUse;
}

String _notificationText(String status) {
  return status.toUpperCase() == 'IN_PROGRESS'
      ? 'Sharing live trip location'
      : 'Sharing route-to-pickup location';
}
