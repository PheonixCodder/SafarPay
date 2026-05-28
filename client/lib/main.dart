import 'package:flutter/material.dart';
import 'package:get_storage/get_storage.dart';
import 'package:firebase_core/firebase_core.dart';
import 'package:firebase_messaging/firebase_messaging.dart';
import 'common/runtime/app_lifecycle_controller.dart';
import 'common/runtime/runtime_diagnostics_controller.dart';
import 'features/drivers/data/active_ride_foreground_service.dart';
import 'features/personalization/screens/notifications/controllers/push_notification_controller.dart';
import 'features/location/data/mapbox_config.dart';
import 'firebase_options.dart';
import 'app.dart';

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  SActiveRideForegroundService.initializeCommunication();
  await GetStorage.init();
  await Firebase.initializeApp(
    options: DefaultFirebaseOptions.currentPlatform,
  );
  SAppLifecycleController.instance;
  SRuntimeDiagnosticsController.instance;
  FirebaseMessaging.onBackgroundMessage(
    safarPayFirebaseMessagingBackgroundHandler,
  );
  await SPushNotificationController.instance.initialize();
  SActiveRideForegroundService.initializeService();
  SMapboxConfig.initialize();
  runApp(const App());
}
