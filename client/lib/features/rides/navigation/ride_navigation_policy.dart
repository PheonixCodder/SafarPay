import '../domain/ride_lifecycle.dart';

enum SRideNavigationSurface {
  rideDetails,
  fixedWaiting,
  hybridMatching,
  liveTracking,
}

class SPassengerRideNavigationDecision {
  const SPassengerRideNavigationDecision({
    required this.surface,
    required this.actionLabel,
  });

  final SRideNavigationSurface surface;
  final String actionLabel;
}

SPassengerRideNavigationDecision sResolvePassengerRideEntry(
  SRideLifecycleSnapshot snapshot,
) {
  return switch (snapshot.stage) {
    SRideLifecycleStage.matchingForDriver =>
      const SPassengerRideNavigationDecision(
        surface: SRideNavigationSurface.hybridMatching,
        actionLabel: 'View offers',
      ),
    SRideLifecycleStage.waitingForDriverAssignment =>
      const SPassengerRideNavigationDecision(
        surface: SRideNavigationSurface.fixedWaiting,
        actionLabel: 'Finding driver',
      ),
    SRideLifecycleStage.driverAssigned ||
    SRideLifecycleStage.driverEnRouteToPickup ||
    SRideLifecycleStage.driverArrivedAtPickup ||
    SRideLifecycleStage.tripInProgress =>
      const SPassengerRideNavigationDecision(
        surface: SRideNavigationSurface.liveTracking,
        actionLabel: 'Track ride',
      ),
    SRideLifecycleStage.scheduled ||
    SRideLifecycleStage.completed ||
    SRideLifecycleStage.cancelled ||
    SRideLifecycleStage.unknown =>
      const SPassengerRideNavigationDecision(
        surface: SRideNavigationSurface.rideDetails,
        actionLabel: 'View details',
      ),
  };
}

enum SNotificationRouteKind {
  passengerRide,
  driverRequests,
  driverActiveRide,
  communication,
}

class SNotificationRouteIntent {
  const SNotificationRouteIntent({
    required this.kind,
    this.rideId,
    this.deeplink,
    this.callId,
    this.presentAsCall = false,
  });

  final SNotificationRouteKind kind;
  final String? rideId;
  final String? deeplink;
  final String? callId;
  final bool presentAsCall;
}

SNotificationRouteIntent? sNotificationRouteIntentFromData(
  Map<String, dynamic> data,
) {
  final deeplink = data['deeplink']?.toString() ?? '';
  final rideId =
      data['ride_id']?.toString() ?? sRideIdFromNotificationDeeplink(deeplink);
  final callId = sCallIdFromNotificationData(data);
  final presentAsCall = sIsIncomingRideCallNotificationData(data);
  final notificationKind = data['notification_kind']?.toString();

  if (deeplink.startsWith('safarpay://communication/rides') &&
      rideId != null &&
      rideId.isNotEmpty) {
    return SNotificationRouteIntent(
      kind: SNotificationRouteKind.communication,
      rideId: rideId,
      deeplink: deeplink,
      callId: callId,
      presentAsCall: presentAsCall,
    );
  }
  if ((notificationKind == 'communication_call' ||
          notificationKind == 'communication_message') &&
      rideId != null &&
      rideId.isNotEmpty) {
    return SNotificationRouteIntent(
      kind: SNotificationRouteKind.communication,
      rideId: rideId,
      deeplink: deeplink.isEmpty ? null : deeplink,
      callId: callId,
      presentAsCall: presentAsCall,
    );
  }
  if (deeplink.startsWith('safarpay://driver/requests')) {
    return SNotificationRouteIntent(
      kind: SNotificationRouteKind.driverRequests,
      rideId: rideId,
      deeplink: deeplink,
    );
  }
  if (notificationKind == 'driver_ride_request') {
    return SNotificationRouteIntent(
      kind: SNotificationRouteKind.driverRequests,
      rideId: rideId,
      deeplink: deeplink.isEmpty ? null : deeplink,
    );
  }
  if (deeplink.startsWith('safarpay://driver/active-rides')) {
    return SNotificationRouteIntent(
      kind: SNotificationRouteKind.driverActiveRide,
      rideId: rideId,
      deeplink: deeplink,
    );
  }
  if (rideId != null && rideId.isNotEmpty) {
    return SNotificationRouteIntent(
      kind: SNotificationRouteKind.passengerRide,
      rideId: rideId,
      deeplink: deeplink.isEmpty ? null : deeplink,
    );
  }
  return null;
}

String? sRideIdFromNotificationDeeplink(String deeplink) {
  final uri = Uri.tryParse(deeplink);
  if (uri == null) return null;
  if (uri.host == 'rides' && uri.pathSegments.isNotEmpty) {
    return uri.pathSegments.first;
  }
  if (uri.host == 'driver' && uri.pathSegments.length > 1) {
    return uri.pathSegments[1];
  }
  if (uri.host == 'communication' &&
      uri.pathSegments.length > 1 &&
      uri.pathSegments.first == 'rides') {
    return uri.pathSegments[1];
  }
  return null;
}

bool sIsIncomingRideCallNotificationData(Map<String, dynamic> data) {
  final kind = data['notification_kind']?.toString();
  final presentAsCall =
      data['present_as_call']?.toString().toLowerCase() == 'true';
  return kind == 'communication_call' || presentAsCall;
}

bool sIsRideCommunicationMessageNotificationData(Map<String, dynamic> data) {
  return data['notification_kind']?.toString() == 'communication_message';
}

String? sCallIdFromNotificationData(Map<String, dynamic> data) {
  final value = data['call_id']?.toString();
  if (value == null || value.isEmpty) {
    return null;
  }
  return value;
}
