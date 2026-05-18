import '../domain/location_models.dart';

enum SLiveRideSocketEventType {
  driverLocationUpdated,
  ping,
  pong,
  error,
  unknown,
}

class SLiveRideSocketEvent {
  const SLiveRideSocketEvent({
    required this.type,
    this.driverLocation,
    this.detail,
  });

  final SLiveRideSocketEventType type;
  final SDriverLiveLocation? driverLocation;
  final String? detail;

  factory SLiveRideSocketEvent.fromJson(Map<String, dynamic> json) {
    final event = json['event']?.toString();

    if (event == 'ping') {
      return const SLiveRideSocketEvent(type: SLiveRideSocketEventType.ping);
    }
    if (event == 'pong') {
      return const SLiveRideSocketEvent(type: SLiveRideSocketEventType.pong);
    }
    if (event == 'error') {
      return SLiveRideSocketEvent(
        type: SLiveRideSocketEventType.error,
        detail: json['detail']?.toString(),
      );
    }
    if (event == 'DRIVER_LOCATION_UPDATED') {
      final data = json['data'];
      return SLiveRideSocketEvent(
        type: SLiveRideSocketEventType.driverLocationUpdated,
        driverLocation: data is Map<String, dynamic>
            ? SDriverLiveLocation.fromJson(data)
            : null,
      );
    }

    return const SLiveRideSocketEvent(type: SLiveRideSocketEventType.unknown);
  }
}
