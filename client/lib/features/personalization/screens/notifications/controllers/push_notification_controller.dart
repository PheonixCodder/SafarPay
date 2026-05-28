import 'dart:async';
import 'dart:convert';

import 'package:firebase_core/firebase_core.dart';
import 'package:firebase_messaging/firebase_messaging.dart';
import 'package:flutter/widgets.dart';
import 'package:flutter_local_notifications/flutter_local_notifications.dart';
import 'package:get/get.dart';

import '../../../../../app_mode_controller.dart';
import '../../../../../firebase_options.dart';
import '../../../../../features/communication/controllers/ride_communication_controller.dart';
import '../../../../../features/drivers/controllers/driver_requests_controller.dart';
import '../../../../../features/drivers/data/driver_ride_overlay_service.dart';
import '../../../../../features/drivers/data/driver_requests_repository.dart';
import '../../../../../features/rides/navigation/ride_navigation_destinations.dart';
import '../../../../../features/rides/navigation/ride_navigation_policy.dart';
import '../../../../../utils/constants/api_constants.dart';
import '../../../../../utils/http/client.dart';
import '../../../../../utils/logging/logger.dart';
import '../data/push_notification_repository.dart';

const _rideAlertsChannelId = 'ride_alerts';
const _rideCallsChannelId = 'ride_calls';
const _callAcceptActionId = 'ride_call_accept';
const _callRejectActionId = 'ride_call_reject';
const _messageReplyActionId = 'ride_message_reply';

@pragma('vm:entry-point')
Future<void> safarPayFirebaseMessagingBackgroundHandler(
  RemoteMessage message,
) async {
  await Firebase.initializeApp(options: DefaultFirebaseOptions.currentPlatform);
  if (sNotificationRouteIntentFromData(message.data)?.kind ==
      SNotificationRouteKind.driverRequests) {
    final notifications = FlutterLocalNotificationsPlugin();
    await _initializeLocalNotificationsPlugin(notifications);
    final displayedOverlay = await _showDriverRideOverlay(message);
    if (displayedOverlay) return;
    await _showDriverRideAlert(notifications, message);
    return;
  }
  if (sIsIncomingRideCallNotificationData(message.data)) {
    final notifications = FlutterLocalNotificationsPlugin();
    await _initializeLocalNotificationsPlugin(notifications);
    await _showRideCallNotification(notifications, message);
    return;
  }
  if (sIsRideCommunicationMessageNotificationData(message.data)) {
    final notifications = FlutterLocalNotificationsPlugin();
    await _initializeLocalNotificationsPlugin(notifications);
    await _showRideMessageNotification(notifications, message);
  }
}

@pragma('vm:entry-point')
void safarPayNotificationTapBackground(NotificationResponse response) {
  final decoded = _decodePayload(response.payload);
  if (decoded == null) return;
  if (response.actionId == _callRejectActionId) {
    unawaited(_rejectCallFromNotificationPayload(decoded));
  }
  if (response.actionId == _messageReplyActionId) {
    unawaited(_replyToMessageFromNotificationPayload(decoded, response.input));
  }
}

class SPushNotificationController extends GetxController
    with WidgetsBindingObserver {
  SPushNotificationController({
    FirebaseMessaging? messaging,
    FlutterLocalNotificationsPlugin? localNotifications,
    SPushNotificationRepository repository = const SPushNotificationRepository(),
    SDriverRequestsRepository driverRequestsRepository =
        const SDriverRequestsRepository(),
  })  : _messaging = messaging ?? FirebaseMessaging.instance,
        _localNotifications =
            localNotifications ?? FlutterLocalNotificationsPlugin(),
        _repository = repository,
        _driverRequestsRepository = driverRequestsRepository;

  static SPushNotificationController get instance {
    if (Get.isRegistered<SPushNotificationController>()) {
      return Get.find<SPushNotificationController>();
    }
    return Get.put(SPushNotificationController());
  }

  final FirebaseMessaging _messaging;
  final FlutterLocalNotificationsPlugin _localNotifications;
  final SPushNotificationRepository _repository;
  final SDriverRequestsRepository _driverRequestsRepository;

  StreamSubscription<String>? _tokenRefreshSub;
  StreamSubscription<RemoteMessage>? _foregroundMessageSub;
  StreamSubscription<RemoteMessage>? _messageOpenedSub;

  @override
  void onInit() {
    super.onInit();
    WidgetsBinding.instance.addObserver(this);
  }

  Future<void> initialize() async {
    await _initializeLocalNotifications();
    _tokenRefreshSub?.cancel();
    _tokenRefreshSub = _messaging.onTokenRefresh.listen(_registerToken);
    _foregroundMessageSub?.cancel();
    _foregroundMessageSub =
        FirebaseMessaging.onMessage.listen(_showForegroundNotification);
    _messageOpenedSub?.cancel();
    _messageOpenedSub =
        FirebaseMessaging.onMessageOpenedApp.listen(_handleMessage);
    final launchDetails =
        await _localNotifications.getNotificationAppLaunchDetails();
    final launchPayload = launchDetails?.notificationResponse?.payload;
    if (launchDetails?.didNotificationLaunchApp ?? false) {
      final decoded = _decodePayload(launchPayload);
      if (decoded != null) {
        unawaited(_handleData(decoded));
      }
    }
    final initialMessage = await _messaging.getInitialMessage();
    if (initialMessage != null) unawaited(_handleMessage(initialMessage));
    await _consumeOverlayLaunchIntent();
  }

  Future<void> ensurePermissionAndRegister() async {
    await requestPermission();
    await registerCurrentToken();
  }

  Future<void> requestPermission() async {
    await _messaging.requestPermission(
      alert: true,
      badge: true,
      sound: true,
      provisional: false,
    );
    await _localNotifications
        .resolvePlatformSpecificImplementation<
            AndroidFlutterLocalNotificationsPlugin>()
        ?.requestFullScreenIntentPermission();
  }

  Future<void> registerCurrentToken() async {
    final token = await _messaging.getToken();
    if (token == null || token.isEmpty) return;
    await _registerToken(token);
  }

  Future<void> unregisterCurrentToken() async {
    final token = await _messaging.getToken();
    if (token == null || token.isEmpty) return;
    await _repository.unregisterToken(token);
  }

  @override
  void onClose() {
    WidgetsBinding.instance.removeObserver(this);
    _tokenRefreshSub?.cancel();
    _foregroundMessageSub?.cancel();
    _messageOpenedSub?.cancel();
    super.onClose();
  }

  @override
  void didChangeAppLifecycleState(AppLifecycleState state) {
    if (state == AppLifecycleState.resumed) {
      unawaited(_consumeOverlayLaunchIntent());
    }
  }

  Future<void> _registerToken(String token) async {
    String? driverId;
    try {
      driverId = await _driverRequestsRepository.fetchCurrentDriverId();
    } catch (error) {
      SLoggerHelper.info('Registering push token without driver id: $error');
    }
    try {
      await _repository.registerToken(token: token, driverId: driverId);
    } catch (error) {
      SLoggerHelper.warning('Unable to register push token: $error');
    }
  }

  Future<void> _initializeLocalNotifications() async {
    await _initializeLocalNotificationsPlugin(
      _localNotifications,
      onDidReceiveNotificationResponse: (response) {
        unawaited(_handleNotificationResponse(response));
      },
    );
  }

  Future<void> _showForegroundNotification(RemoteMessage message) async {
    if (sNotificationRouteIntentFromData(message.data)?.kind ==
        SNotificationRouteKind.driverRequests) {
      if (Get.isRegistered<SDriverRequestsController>()) {
        return;
      }
      final displayedOverlay = await _showDriverRideOverlay(message);
      if (displayedOverlay) return;
      await _showDriverRideAlert(_localNotifications, message);
      return;
    }
    final notification = message.notification;
    final title = notification?.title ?? message.data['title'] ?? 'SafarPay';
    final body = notification?.body ?? message.data['body'] ?? 'New update';
    if (sIsIncomingRideCallNotificationData(message.data)) {
      await _showRideCallNotification(_localNotifications, message);
      return;
    }
    if (sIsRideCommunicationMessageNotificationData(message.data)) {
      await _showRideMessageNotification(_localNotifications, message);
      return;
    }
    await _localNotifications.show(
      message.hashCode,
      title,
      body,
      const NotificationDetails(
        android: AndroidNotificationDetails(
          _rideAlertsChannelId,
          'Ride alerts',
          channelDescription: 'Ride requests and active trip updates',
          importance: Importance.high,
          priority: Priority.high,
        ),
        iOS: DarwinNotificationDetails(),
      ),
      payload: jsonEncode(message.data),
    );
  }

  Future<void> _handleMessage(RemoteMessage message) {
    return _handleData(message.data);
  }

  Future<void> _handleNotificationResponse(
    NotificationResponse response,
  ) async {
    final decoded = _decodePayload(response.payload);
    if (decoded == null) return;
    if (response.actionId == _callRejectActionId) {
      await _rejectCallFromNotificationPayload(decoded);
      return;
    }
    if (response.actionId == _messageReplyActionId) {
      await _replyToMessageFromNotificationPayload(decoded, response.input);
      return;
    }
    await _handleData(decoded);
  }

  Future<void> _consumeOverlayLaunchIntent() async {
    final data = await const SDriverRideOverlayService().consumeLaunchIntent();
    if (data == null) return;
    await _handleData(data);
  }

  Future<void> _handleData(Map<String, dynamic> data) async {
    final intent = sNotificationRouteIntentFromData(data);
    if (intent == null) return;

    switch (intent.kind) {
      case SNotificationRouteKind.communication:
        final rideId = intent.rideId!;
        final callId = intent.callId;
        if (callId != null &&
            callId.isNotEmpty &&
            Get.isRegistered<SRideCommunicationController>(tag: rideId)) {
          final controller = Get.find<SRideCommunicationController>(tag: rideId);
          unawaited(
            controller.hydrateNotificationCall(
              callId,
              presentCallScreen: intent.presentAsCall,
            ),
          );
        }
        await sOpenDestinationWithGet(
          sRideCommunicationDestination(
            rideId: rideId,
            callId: callId,
            openCallOnLoad: intent.presentAsCall,
          ),
        );
        return;
      case SNotificationRouteKind.driverRequests:
      case SNotificationRouteKind.driverActiveRide:
        await sOpenDestinationWithGet(
          sDriverRequestsDestination(rideId: intent.rideId),
          ensureDriverMode: SAppModeController.instance.switchToDriverMode,
        );
        return;
      case SNotificationRouteKind.passengerRide:
        final rideId = intent.rideId;
        if (rideId != null && rideId.isNotEmpty) {
          await sOpenDestinationWithGet(sRideTrackingDestination(rideId));
        }
        return;
    }
  }
}

Map<String, dynamic>? _decodePayload(String? payload) {
  if (payload == null || payload.isEmpty) return null;
  try {
    final decoded = jsonDecode(payload);
    if (decoded is Map<String, dynamic>) {
      return decoded;
    }
    if (decoded is Map) {
      return Map<String, dynamic>.from(decoded);
    }
  } catch (_) {
    return null;
  }
  return null;
}

Future<void> _initializeLocalNotificationsPlugin(
  FlutterLocalNotificationsPlugin plugin, {
  DidReceiveNotificationResponseCallback? onDidReceiveNotificationResponse,
}) async {
  const android = AndroidInitializationSettings('@mipmap/ic_launcher');
  const darwin = DarwinInitializationSettings();
  await plugin.initialize(
    const InitializationSettings(android: android, iOS: darwin),
    onDidReceiveNotificationResponse: onDidReceiveNotificationResponse,
    onDidReceiveBackgroundNotificationResponse:
        safarPayNotificationTapBackground,
  );
  const androidChannel = AndroidNotificationChannel(
    _rideAlertsChannelId,
    'Ride alerts',
    description: 'Ride requests and active trip updates',
    importance: Importance.max,
  );
  const callChannel = AndroidNotificationChannel(
    _rideCallsChannelId,
    'Ride calls',
    description: 'Incoming ride voice calls',
    importance: Importance.max,
  );
  final androidPlatform = plugin.resolvePlatformSpecificImplementation<
      AndroidFlutterLocalNotificationsPlugin>();
  await androidPlatform?.createNotificationChannel(androidChannel);
  await androidPlatform?.createNotificationChannel(callChannel);
}

Future<void> _showDriverRideAlert(
  FlutterLocalNotificationsPlugin plugin,
  RemoteMessage message,
) async {
  final notification = message.notification;
  final title =
      notification?.title ?? message.data['title'] ?? 'New ride request';
  final body = notification?.body ??
      message.data['message'] ??
      message.data['body'] ??
      'A passenger request is available near you.';
  await plugin.show(
    message.data['ride_id']?.hashCode ?? message.hashCode,
    title,
    body,
    const NotificationDetails(
      android: AndroidNotificationDetails(
        _rideAlertsChannelId,
        'Ride alerts',
        channelDescription: 'Ride requests and active trip updates',
        importance: Importance.max,
        priority: Priority.max,
        category: AndroidNotificationCategory.transport,
        fullScreenIntent: true,
        ticker: 'New ride request',
      ),
      iOS: DarwinNotificationDetails(categoryIdentifier: 'driver_ride_request'),
    ),
    payload: jsonEncode(message.data),
  );
}

Future<bool> _showDriverRideOverlay(RemoteMessage message) async {
  final intent = sNotificationRouteIntentFromData(message.data);
  final rideId = intent?.rideId ?? message.data['ride_id']?.toString() ?? '';
  if (rideId.isEmpty) return false;
  final notification = message.notification;
  final title =
      notification?.title ?? message.data['title'] ?? 'New ride request';
  final body = notification?.body ??
      message.data['message'] ??
      message.data['body'] ??
      'A passenger request is available near you.';
  return const SDriverRideOverlayService().showRideRequest(
    rideId: rideId,
    title: title,
    body: body,
    deeplink: intent?.deeplink ?? 'safarpay://driver/requests/$rideId',
  );
}

Future<void> _showRideCallNotification(
  FlutterLocalNotificationsPlugin plugin,
  RemoteMessage message,
) async {
  final notification = message.notification;
  final title = notification?.title ?? message.data['title'] ?? 'Incoming call';
  final body =
      notification?.body ?? message.data['body'] ?? 'Ride communication call';
  await plugin.show(
    message.data['call_id']?.hashCode ?? message.hashCode,
    title,
    body,
    const NotificationDetails(
      android: AndroidNotificationDetails(
        _rideCallsChannelId,
        'Ride calls',
        channelDescription: 'Incoming ride voice calls',
        importance: Importance.max,
        priority: Priority.max,
        category: AndroidNotificationCategory.call,
        fullScreenIntent: true,
        actions: <AndroidNotificationAction>[
          AndroidNotificationAction(
            _callRejectActionId,
            'Reject',
            cancelNotification: true,
          ),
          AndroidNotificationAction(
            _callAcceptActionId,
            'Accept',
            showsUserInterface: true,
          ),
        ],
      ),
      iOS: DarwinNotificationDetails(categoryIdentifier: 'ride_call'),
    ),
    payload: jsonEncode(message.data),
  );
}

Future<void> _showRideMessageNotification(
  FlutterLocalNotificationsPlugin plugin,
  RemoteMessage message,
) async {
  final notification = message.notification;
  final title = notification?.title ?? message.data['title'] ?? 'New message';
  final body =
      notification?.body ?? message.data['body'] ?? 'New ride message';
  await plugin.show(
    message.data['message_id']?.hashCode ?? message.hashCode,
    title,
    body,
    const NotificationDetails(
      android: AndroidNotificationDetails(
        _rideAlertsChannelId,
        'Ride alerts',
        channelDescription: 'Ride requests and active trip updates',
        importance: Importance.high,
        priority: Priority.high,
        category: AndroidNotificationCategory.message,
        actions: <AndroidNotificationAction>[
          AndroidNotificationAction(
            _messageReplyActionId,
            'Reply',
            inputs: <AndroidNotificationActionInput>[
              AndroidNotificationActionInput(label: 'Reply'),
            ],
          ),
        ],
      ),
      iOS: DarwinNotificationDetails(categoryIdentifier: 'ride_message'),
    ),
    payload: jsonEncode(message.data),
  );
}

Future<void> _rejectCallFromNotificationPayload(
  Map<String, dynamic> data,
) async {
  final callId = data['call_id']?.toString();
  if (callId == null || callId.isEmpty) return;
  try {
    await SHttpClient.post(
      '/calls/$callId/end',
      service: SApiService.communication,
      requiresAuth: true,
      body: {
        'status': 'REJECTED',
        'reason': 'notification_action',
      },
    );
  } catch (error) {
    SLoggerHelper.warning('Unable to reject ride call from notification: $error');
  }
}

Future<void> _replyToMessageFromNotificationPayload(
  Map<String, dynamic> data,
  String? reply,
) async {
  final conversationId = data['conversation_id']?.toString();
  final body = reply?.trim();
  if (conversationId == null ||
      conversationId.isEmpty ||
      body == null ||
      body.isEmpty) {
    return;
  }
  try {
    await SHttpClient.post(
      '/conversations/$conversationId/messages',
      service: SApiService.communication,
      requiresAuth: true,
      body: {'body': body},
    );
  } catch (error) {
    SLoggerHelper.warning(
      'Unable to reply to ride message from notification: $error',
    );
  }
}
