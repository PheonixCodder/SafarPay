class SCoordinate {
  const SCoordinate({
    required this.latitude,
    required this.longitude,
  });

  final double latitude;
  final double longitude;

  factory SCoordinate.fromJson(Map<String, dynamic> json) {
    return SCoordinate(
      latitude: _readDouble(json, 'latitude', fallbackKey: 'lat'),
      longitude: _readDouble(json, 'longitude', fallbackKey: 'lng'),
    );
  }

  Map<String, double> toJson() {
    return {
      'latitude': latitude,
      'longitude': longitude,
    };
  }
}

class SAddressResult {
  const SAddressResult({
    required this.formatted,
    required this.coordinate,
    this.street,
    this.city,
    this.country,
    this.postalCode,
  });

  static final RegExp _coordinatePairPattern = RegExp(
    r'^\s*(-?\d+(?:\.\d+)?)\s*[,;\s]\s*(-?\d+(?:\.\d+)?)\s*$',
  );

  final String formatted;
  final SCoordinate coordinate;
  final String? street;
  final String? city;
  final String? country;
  final String? postalCode;

  /// True when [formatted] is only a lat/lng pair (e.g. Mapbox fallback text).
  bool get isCoordinateLikeFormatted => isCoordinateLikeQuery(formatted);

  /// User-visible label — never raw coordinates when structured fields exist.
  String get displayLabel {
    if (!isCoordinateLikeFormatted) return formatted;
    final parts = [street, city, country]
        .whereType<String>()
        .where((part) => part.trim().isNotEmpty);
    if (parts.isNotEmpty) return parts.join(', ');
    return 'Selected location';
  }

  static bool isCoordinateLikeQuery(String text) {
    return tryParseCoordinateQuery(text) != null;
  }

  static SCoordinate? tryParseCoordinateQuery(String text) {
    final match = _coordinatePairPattern.firstMatch(text.trim());
    if (match == null) return null;

    final first = double.tryParse(match.group(1)!);
    final second = double.tryParse(match.group(2)!);
    if (first == null || second == null) return null;

    if (_isValidLatitude(first) && _isValidLongitude(second)) {
      return SCoordinate(latitude: first, longitude: second);
    }
    if (_isValidLatitude(second) && _isValidLongitude(first)) {
      return SCoordinate(latitude: second, longitude: first);
    }
    return null;
  }

  static bool _isValidLatitude(double value) => value >= -90 && value <= 90;

  static bool _isValidLongitude(double value) => value >= -180 && value <= 180;

  factory SAddressResult.fromJson(Map<String, dynamic> json) {
    final coordinates = json['coordinates'];
    return SAddressResult(
      formatted: json['formatted'] as String? ?? '',
      coordinate: coordinates is Map<String, dynamic>
          ? SCoordinate.fromJson(coordinates)
          : SCoordinate.fromJson(json),
      street: json['street'] as String?,
      city: json['city'] as String?,
      country: json['country'] as String?,
      postalCode: json['postal_code'] as String?,
    );
  }
}

class SRouteStep {
  const SRouteStep({
    required this.instruction,
    required this.distanceMeters,
    required this.durationSeconds,
    required this.polyline,
  });

  final String instruction;
  final double distanceMeters;
  final double durationSeconds;
  final String polyline;

  factory SRouteStep.fromJson(Map<String, dynamic> json) {
    return SRouteStep(
      instruction: json['instruction'] as String? ?? '',
      distanceMeters: _readDouble(json, 'distance_meters'),
      durationSeconds: _readDouble(json, 'duration_seconds'),
      polyline: json['polyline'] as String? ?? '',
    );
  }
}

class SRoutePreview {
  const SRoutePreview({
    required this.distanceKm,
    required this.durationMinutes,
    required this.polyline,
    required this.steps,
  });

  final double distanceKm;
  final double durationMinutes;
  final String polyline;
  final List<SRouteStep> steps;

  factory SRoutePreview.fromJson(Map<String, dynamic> json) {
    final rawSteps = json['steps'];
    return SRoutePreview(
      distanceKm: _readDouble(json, 'distance_km'),
      durationMinutes: _readDouble(json, 'duration_minutes'),
      polyline: json['polyline'] as String? ?? '',
      steps: rawSteps is List
          ? rawSteps
              .whereType<Map<String, dynamic>>()
              .map(SRouteStep.fromJson)
              .toList()
          : const [],
    );
  }
}

class SDriverLiveLocation {
  const SDriverLiveLocation({
    required this.driverId,
    required this.coordinate,
    this.heading,
    this.speed,
    this.updatedAt,
  });

  final String driverId;
  final SCoordinate coordinate;
  final double? heading;
  final double? speed;
  final DateTime? updatedAt;

  factory SDriverLiveLocation.fromJson(Map<String, dynamic> json) {
    return SDriverLiveLocation(
      driverId: json['driver_id']?.toString() ?? '',
      coordinate: SCoordinate.fromJson(json),
      heading: _tryReadDouble(json['heading']),
      speed: _tryReadDouble(json['speed']),
      updatedAt: _tryReadDate(json['updated_at']),
    );
  }
}

class SPassengerLiveLocation {
  const SPassengerLiveLocation({
    required this.userId,
    required this.coordinate,
    this.updatedAt,
  });

  final String userId;
  final SCoordinate coordinate;
  final DateTime? updatedAt;

  factory SPassengerLiveLocation.fromJson(Map<String, dynamic> json) {
    return SPassengerLiveLocation(
      userId: json['user_id']?.toString() ?? '',
      coordinate: SCoordinate.fromJson(json),
      updatedAt: _tryReadDate(json['updated_at']),
    );
  }
}

class SLiveRideLocations {
  const SLiveRideLocations({
    required this.rideId,
    this.driver,
    this.passenger,
  });

  final String rideId;
  final SDriverLiveLocation? driver;
  final SPassengerLiveLocation? passenger;

  factory SLiveRideLocations.fromJson(Map<String, dynamic> json) {
    final driver = json['driver'];
    final passenger = json['passenger'];
    return SLiveRideLocations(
      rideId: json['ride_id']?.toString() ?? '',
      driver: driver is Map<String, dynamic>
          ? SDriverLiveLocation.fromJson(driver)
          : null,
      passenger: passenger is Map<String, dynamic>
          ? SPassengerLiveLocation.fromJson(passenger)
          : null,
    );
  }
}

double _readDouble(
  Map<String, dynamic> json,
  String key, {
  String? fallbackKey,
}) {
  final value = json[key] ?? (fallbackKey == null ? null : json[fallbackKey]);
  return _tryReadDouble(value) ?? 0.0;
}

double? _tryReadDouble(Object? value) {
  if (value is num) return value.toDouble();
  if (value is String) return double.tryParse(value);
  return null;
}

DateTime? _tryReadDate(Object? value) {
  if (value is String && value.isNotEmpty) return DateTime.tryParse(value);
  return null;
}
