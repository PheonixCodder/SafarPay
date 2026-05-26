import '../../location/domain/location_models.dart';

class SDriverRideStop {
  const SDriverRideStop({
    required this.id,
    required this.coordinate,
    required this.stopType,
    this.placeName,
    this.addressLine,
    this.arrivedAt,
    this.completedAt,
  });

  final String id;
  final SCoordinate coordinate;
  final String stopType;
  final String? placeName;
  final String? addressLine;
  final DateTime? arrivedAt;
  final DateTime? completedAt;

  String get displayName {
    final name = placeName?.trim();
    if (name != null && name.isNotEmpty) return name;
    final address = addressLine?.trim();
    if (address != null && address.isNotEmpty) return address;
    return '${coordinate.latitude.toStringAsFixed(5)}, '
        '${coordinate.longitude.toStringAsFixed(5)}';
  }

  factory SDriverRideStop.fromJson(Map<String, dynamic>? json) {
    final data = json ?? const <String, dynamic>{};
    return SDriverRideStop(
      id: data['id']?.toString() ?? '',
      coordinate: SCoordinate.fromJson(data),
      stopType: data['stop_type']?.toString() ?? '',
      placeName: data['place_name']?.toString(),
      addressLine: data['address_line_1']?.toString(),
      arrivedAt: _date(data['arrived_at']),
      completedAt: _date(data['completed_at']),
    );
  }
}

class SDriverRideRequest {
  const SDriverRideRequest({
    required this.id,
    required this.passengerId,
    required this.serviceType,
    required this.category,
    required this.pricingMode,
    required this.status,
    required this.paymentMethod,
    required this.collectionMode,
    required this.createdAt,
    this.baselineMinPrice,
    this.baselineMaxPrice,
    this.finalPrice,
    this.pickup,
    this.dropoff,
    this.driverToPickup,
    this.tripRoute,
  });

  final String id;
  final String passengerId;
  final String serviceType;
  final String category;
  final String pricingMode;
  final String status;
  final String paymentMethod;
  final String collectionMode;
  final DateTime? createdAt;
  final double? baselineMinPrice;
  final double? baselineMaxPrice;
  final double? finalPrice;
  final SDriverRideStop? pickup;
  final SDriverRideStop? dropoff;
  final SRoutePreview? driverToPickup;
  final SRoutePreview? tripRoute;

  double get displayFare {
    return finalPrice ?? baselineMaxPrice ?? baselineMinPrice ?? 0;
  }

  bool get isHybrid => pricingMode == 'HYBRID' || pricingMode == 'BID_BASED';

  factory SDriverRideRequest.fromJson(Map<String, dynamic> json) {
    return SDriverRideRequest(
      id: json['id']?.toString() ?? '',
      passengerId: json['passenger_id']?.toString() ?? '',
      serviceType: json['service_type']?.toString() ?? '',
      category: json['category']?.toString() ?? '',
      pricingMode: json['pricing_mode']?.toString() ?? '',
      status: json['status']?.toString() ?? '',
      paymentMethod: json['passenger_payment_method']?.toString() ?? 'CASH',
      collectionMode:
          json['payment_collection_mode']?.toString() ?? 'DRIVER_COLLECTED',
      createdAt: _date(json['created_at']),
      baselineMinPrice: _double(json['baseline_min_price']),
      baselineMaxPrice: _double(json['baseline_max_price']),
      finalPrice: _double(json['final_price']),
      pickup: json['pickup_stop'] is Map<String, dynamic>
          ? SDriverRideStop.fromJson(json['pickup_stop'] as Map<String, dynamic>)
          : null,
      dropoff: json['dropoff_stop'] is Map<String, dynamic>
          ? SDriverRideStop.fromJson(
              json['dropoff_stop'] as Map<String, dynamic>,
            )
          : null,
      driverToPickup: json['driver_to_pickup'] is Map<String, dynamic>
          ? SRoutePreview.fromJson(
              json['driver_to_pickup'] as Map<String, dynamic>,
            )
          : null,
      tripRoute: json['trip_route'] is Map<String, dynamic>
          ? SRoutePreview.fromJson(json['trip_route'] as Map<String, dynamic>)
          : null,
    );
  }
}

class SDriverActiveRide extends SDriverRideRequest {
  const SDriverActiveRide({
    required super.id,
    required super.passengerId,
    required super.serviceType,
    required super.category,
    required super.pricingMode,
    required super.status,
    required super.paymentMethod,
    required super.collectionMode,
    required super.createdAt,
    super.baselineMinPrice,
    super.baselineMaxPrice,
    super.finalPrice,
    super.pickup,
    super.dropoff,
    super.driverToPickup,
    super.tripRoute,
    required this.requiresOtpStart,
    required this.requiresOtpEnd,
  });

  final bool requiresOtpStart;
  final bool requiresOtpEnd;

  bool get hasArrivedAtPickup => pickup?.arrivedAt != null;
  bool get isInProgress => status == 'IN_PROGRESS';

  factory SDriverActiveRide.fromJson(Map<String, dynamic> json) {
    final request = SDriverRideRequest.fromJson(json);
    return SDriverActiveRide(
      id: request.id,
      passengerId: request.passengerId,
      serviceType: request.serviceType,
      category: request.category,
      pricingMode: request.pricingMode,
      status: request.status,
      paymentMethod: request.paymentMethod,
      collectionMode: request.collectionMode,
      createdAt: request.createdAt,
      baselineMinPrice: request.baselineMinPrice,
      baselineMaxPrice: request.baselineMaxPrice,
      finalPrice: request.finalPrice,
      pickup: request.pickup,
      dropoff: request.dropoff,
      driverToPickup: request.driverToPickup,
      tripRoute: request.tripRoute,
      requiresOtpStart: json['requires_otp_start'] == true,
      requiresOtpEnd: json['requires_otp_end'] == true,
    );
  }
}

double? _double(Object? value) {
  if (value is num) return value.toDouble();
  if (value is String) return double.tryParse(value);
  return null;
}

DateTime? _date(Object? value) {
  if (value is String && value.isNotEmpty) return DateTime.tryParse(value);
  return null;
}
