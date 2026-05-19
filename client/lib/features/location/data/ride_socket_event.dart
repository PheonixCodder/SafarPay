enum SRideSocketEventType {
  rideUpdated,
  driverLocation,
  jobAssigned,
  jobCancelled,
  jobUpdated,
  newJob,
  ping,
  pong,
  error,
  unknown,
}

class SRideSocketEvent {
  const SRideSocketEvent({
    required this.type,
    this.rideId,
    this.status,
    this.data,
    this.detail,
  });

  final SRideSocketEventType type;
  final String? rideId;
  final String? status;
  final Map<String, dynamic>? data;
  final String? detail;

  factory SRideSocketEvent.fromJson(Map<String, dynamic> json) {
    final event = json['event']?.toString();
    final data = json['data'] is Map<String, dynamic>
        ? json['data'] as Map<String, dynamic>
        : null;

    return SRideSocketEvent(
      type: _typeFor(event),
      rideId: _stringValue(data, 'ride_id') ??
          _stringValue(data, 'id') ??
          _stringValue(json, 'ride_id'),
      status: _stringValue(data, 'status') ?? _stringValue(json, 'status'),
      data: data,
      detail: json['detail']?.toString() ?? json['message']?.toString(),
    );
  }
}

SRideSocketEventType _typeFor(String? event) {
  return switch (event) {
    'RIDE_UPDATED' => SRideSocketEventType.rideUpdated,
    'DRIVER_LOCATION' => SRideSocketEventType.driverLocation,
    'JOB_ASSIGNED' => SRideSocketEventType.jobAssigned,
    'JOB_CANCELLED' => SRideSocketEventType.jobCancelled,
    'JOB_UPDATED' => SRideSocketEventType.jobUpdated,
    'NEW_JOB' => SRideSocketEventType.newJob,
    'ping' => SRideSocketEventType.ping,
    'pong' => SRideSocketEventType.pong,
    'error' => SRideSocketEventType.error,
    _ => SRideSocketEventType.unknown,
  };
}

String? _stringValue(Map<String, dynamic>? json, String key) {
  return json?[key]?.toString();
}
