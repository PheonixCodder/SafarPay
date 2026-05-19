enum ServiceType {
  cityRide('CITY_RIDE'),
  intercity('INTERCITY'),
  freight('FREIGHT'),
  courier('COURIER'),
  grocery('GROCERY');

  const ServiceType(this.value);

  final String value;

  static ServiceType fromJson(String value) {
    return ServiceType.values.firstWhere((type) => type.value == value);
  }
}

enum ServiceCategory {
  mini('MINI'),
  rickshaw('RICKSHAW'),
  rideAc('RIDE_AC'),
  premium('PREMIUM'),
  bike('BIKE'),
  comfort('COMFORT'),
  share('SHARE'),
  private('PRIVATE');

  const ServiceCategory(this.value);

  final String value;

  static ServiceCategory fromJson(String value) {
    return ServiceCategory.values
        .firstWhere((category) => category.value == value);
  }
}

enum PricingMode {
  fixed('FIXED'),
  bidBased('BID_BASED'),
  hybrid('HYBRID');

  const PricingMode(this.value);

  final String value;

  static PricingMode fromJson(String value) {
    return PricingMode.values.firstWhere((mode) => mode.value == value);
  }
}

enum RideStatus {
  created('CREATED'),
  matching('MATCHING'),
  accepted('ACCEPTED'),
  arriving('ARRIVING'),
  inProgress('IN_PROGRESS'),
  completed('COMPLETED'),
  cancelled('CANCELLED');

  const RideStatus(this.value);

  final String value;

  static RideStatus fromJson(String value) {
    return RideStatus.values.firstWhere((status) => status.value == value);
  }
}

enum PassengerPaymentMethod {
  card('CARD'),
  cash('CASH'),
  easypaisa('EASYPAISA'),
  jazzcash('JAZZCASH');

  const PassengerPaymentMethod(this.value);

  final String value;

  static PassengerPaymentMethod fromJson(String value) {
    return PassengerPaymentMethod.values
        .firstWhere((method) => method.value == value);
  }
}

enum PaymentCollectionMode {
  platformCollected('PLATFORM_COLLECTED'),
  driverCollected('DRIVER_COLLECTED');

  const PaymentCollectionMode(this.value);

  final String value;

  static PaymentCollectionMode fromJson(String value) {
    return PaymentCollectionMode.values
        .firstWhere((mode) => mode.value == value);
  }
}

enum StopType {
  pickup('PICKUP'),
  dropoff('DROPOFF'),
  waypoint('WAYPOINT');

  const StopType(this.value);

  final String value;

  static StopType fromJson(String value) {
    return StopType.values.firstWhere((type) => type.value == value);
  }
}

enum ProofType {
  pickup('PICKUP'),
  dropoff('DROPOFF');

  const ProofType(this.value);

  final String value;

  static ProofType fromJson(String value) {
    return ProofType.values.firstWhere((type) => type.value == value);
  }
}

class RideResponse {
  const RideResponse({
    required this.id,
    required this.passengerId,
    required this.assignedDriverId,
    required this.serviceType,
    required this.category,
    required this.pricingMode,
    required this.status,
    required this.baselineMinPrice,
    required this.baselineMaxPrice,
    required this.finalPrice,
    required this.passengerPaymentMethod,
    required this.passengerPaymentMethodId,
    required this.paymentCollectionMode,
    required this.scheduledAt,
    required this.isScheduled,
    required this.isRisky,
    required this.autoAcceptDriver,
    required this.acceptedAt,
    required this.completedAt,
    required this.cancelledAt,
    required this.cancellationReason,
    required this.createdAt,
    required this.stops,
    required this.proofImages,
    required this.verificationCodes,
    required this.pickupStop,
    required this.dropoffStop,
  });

  final String id;
  final String passengerId;
  final String? assignedDriverId;
  final ServiceType serviceType;
  final ServiceCategory category;
  final PricingMode pricingMode;
  final RideStatus status;
  final double? baselineMinPrice;
  final double? baselineMaxPrice;
  final double? finalPrice;
  final PassengerPaymentMethod passengerPaymentMethod;
  final String? passengerPaymentMethodId;
  final PaymentCollectionMode paymentCollectionMode;
  final DateTime? scheduledAt;
  final bool isScheduled;
  final bool isRisky;
  final bool autoAcceptDriver;
  final DateTime? acceptedAt;
  final DateTime? completedAt;
  final DateTime? cancelledAt;
  final String? cancellationReason;
  final DateTime createdAt;
  final List<StopResponse> stops;
  final List<ProofImageResponse> proofImages;
  final List<VerificationCodeResponse> verificationCodes;
  final StopResponse? pickupStop;
  final StopResponse? dropoffStop;

  factory RideResponse.fromJson(Map<String, dynamic> json) {
    return RideResponse(
      id: json['id'] as String,
      passengerId: json['passenger_id'] as String,
      assignedDriverId: json['assigned_driver_id'] as String?,
      serviceType: ServiceType.fromJson(json['service_type'] as String),
      category: ServiceCategory.fromJson(json['category'] as String),
      pricingMode: PricingMode.fromJson(json['pricing_mode'] as String),
      status: RideStatus.fromJson(json['status'] as String),
      baselineMinPrice: _toDouble(json['baseline_min_price']),
      baselineMaxPrice: _toDouble(json['baseline_max_price']),
      finalPrice: _toDouble(json['final_price']),
      passengerPaymentMethod: PassengerPaymentMethod.fromJson(
        json['passenger_payment_method'] as String,
      ),
      passengerPaymentMethodId: json['passenger_payment_method_id'] as String?,
      paymentCollectionMode: PaymentCollectionMode.fromJson(
        json['payment_collection_mode'] as String,
      ),
      scheduledAt: _toDateTime(json['scheduled_at']),
      isScheduled: json['is_scheduled'] as bool,
      isRisky: json['is_risky'] as bool,
      autoAcceptDriver: json['auto_accept_driver'] as bool,
      acceptedAt: _toDateTime(json['accepted_at']),
      completedAt: _toDateTime(json['completed_at']),
      cancelledAt: _toDateTime(json['cancelled_at']),
      cancellationReason: json['cancellation_reason'] as String?,
      createdAt: DateTime.parse(json['created_at'] as String),
      stops: _toList(json['stops'], StopResponse.fromJson),
      proofImages: _toList(json['proof_images'], ProofImageResponse.fromJson),
      verificationCodes: _toList(
        json['verification_codes'],
        VerificationCodeResponse.fromJson,
      ),
      pickupStop: _toNullableModel(json['pickup_stop'], StopResponse.fromJson),
      dropoffStop:
          _toNullableModel(json['dropoff_stop'], StopResponse.fromJson),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'passenger_id': passengerId,
      'assigned_driver_id': assignedDriverId,
      'service_type': serviceType.value,
      'category': category.value,
      'pricing_mode': pricingMode.value,
      'status': status.value,
      'baseline_min_price': baselineMinPrice,
      'baseline_max_price': baselineMaxPrice,
      'final_price': finalPrice,
      'passenger_payment_method': passengerPaymentMethod.value,
      'passenger_payment_method_id': passengerPaymentMethodId,
      'payment_collection_mode': paymentCollectionMode.value,
      'scheduled_at': scheduledAt?.toIso8601String(),
      'is_scheduled': isScheduled,
      'is_risky': isRisky,
      'auto_accept_driver': autoAcceptDriver,
      'accepted_at': acceptedAt?.toIso8601String(),
      'completed_at': completedAt?.toIso8601String(),
      'cancelled_at': cancelledAt?.toIso8601String(),
      'cancellation_reason': cancellationReason,
      'created_at': createdAt.toIso8601String(),
      'stops': stops.map((stop) => stop.toJson()).toList(),
      'proof_images': proofImages.map((proof) => proof.toJson()).toList(),
      'verification_codes':
          verificationCodes.map((code) => code.toJson()).toList(),
      'pickup_stop': pickupStop?.toJson(),
      'dropoff_stop': dropoffStop?.toJson(),
    };
  }
}

class StopResponse {
  const StopResponse({
    required this.id,
    required this.serviceRequestId,
    required this.sequenceOrder,
    required this.stopType,
    required this.latitude,
    required this.longitude,
    required this.placeName,
    required this.addressLine1,
    required this.addressLine2,
    required this.city,
    required this.state,
    required this.country,
    required this.postalCode,
    required this.contactName,
    required this.contactPhone,
    required this.instructions,
    required this.arrivedAt,
    required this.completedAt,
  });

  final String id;
  final String serviceRequestId;
  final int sequenceOrder;
  final StopType stopType;
  final double latitude;
  final double longitude;
  final String? placeName;
  final String? addressLine1;
  final String? addressLine2;
  final String? city;
  final String? state;
  final String? country;
  final String? postalCode;
  final String? contactName;
  final String? contactPhone;
  final String? instructions;
  final DateTime? arrivedAt;
  final DateTime? completedAt;

  factory StopResponse.fromJson(Map<String, dynamic> json) {
    return StopResponse(
      id: json['id'] as String,
      serviceRequestId: json['service_request_id'] as String,
      sequenceOrder: json['sequence_order'] as int,
      stopType: StopType.fromJson(json['stop_type'] as String),
      latitude: _toDouble(json['latitude']) ?? 0,
      longitude: _toDouble(json['longitude']) ?? 0,
      placeName: json['place_name'] as String?,
      addressLine1: json['address_line_1'] as String?,
      addressLine2: json['address_line_2'] as String?,
      city: json['city'] as String?,
      state: json['state'] as String?,
      country: json['country'] as String?,
      postalCode: json['postal_code'] as String?,
      contactName: json['contact_name'] as String?,
      contactPhone: json['contact_phone'] as String?,
      instructions: json['instructions'] as String?,
      arrivedAt: _toDateTime(json['arrived_at']),
      completedAt: _toDateTime(json['completed_at']),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'service_request_id': serviceRequestId,
      'sequence_order': sequenceOrder,
      'stop_type': stopType.value,
      'latitude': latitude,
      'longitude': longitude,
      'place_name': placeName,
      'address_line_1': addressLine1,
      'address_line_2': addressLine2,
      'city': city,
      'state': state,
      'country': country,
      'postal_code': postalCode,
      'contact_name': contactName,
      'contact_phone': contactPhone,
      'instructions': instructions,
      'arrived_at': arrivedAt?.toIso8601String(),
      'completed_at': completedAt?.toIso8601String(),
    };
  }
}

class ProofImageResponse {
  const ProofImageResponse({
    required this.id,
    required this.serviceRequestId,
    required this.stopId,
    required this.proofType,
    required this.fileKey,
    required this.fileName,
    required this.mimeType,
    required this.fileSizeBytes,
    required this.isPrimary,
    required this.uploadedByUserId,
    required this.uploadedByDriverId,
    required this.uploadedAt,
  });

  final String id;
  final String serviceRequestId;
  final String? stopId;
  final ProofType proofType;
  final String fileKey;
  final String? fileName;
  final String? mimeType;
  final int? fileSizeBytes;
  final bool isPrimary;
  final String? uploadedByUserId;
  final String? uploadedByDriverId;
  final DateTime uploadedAt;

  factory ProofImageResponse.fromJson(Map<String, dynamic> json) {
    return ProofImageResponse(
      id: json['id'] as String,
      serviceRequestId: json['service_request_id'] as String,
      stopId: json['stop_id'] as String?,
      proofType: ProofType.fromJson(json['proof_type'] as String),
      fileKey: json['file_key'] as String,
      fileName: json['file_name'] as String?,
      mimeType: json['mime_type'] as String?,
      fileSizeBytes: json['file_size_bytes'] as int?,
      isPrimary: json['is_primary'] as bool,
      uploadedByUserId: json['uploaded_by_user_id'] as String?,
      uploadedByDriverId: json['uploaded_by_driver_id'] as String?,
      uploadedAt: DateTime.parse(json['uploaded_at'] as String),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'service_request_id': serviceRequestId,
      'stop_id': stopId,
      'proof_type': proofType.value,
      'file_key': fileKey,
      'file_name': fileName,
      'mime_type': mimeType,
      'file_size_bytes': fileSizeBytes,
      'is_primary': isPrimary,
      'uploaded_by_user_id': uploadedByUserId,
      'uploaded_by_driver_id': uploadedByDriverId,
      'uploaded_at': uploadedAt.toIso8601String(),
    };
  }
}

class VerificationCodeResponse {
  const VerificationCodeResponse({
    required this.id,
    required this.serviceRequestId,
    required this.stopId,
    required this.isVerified,
    required this.attempts,
    required this.maxAttempts,
    required this.expiresAt,
    required this.generatedAt,
    required this.verifiedAt,
  });

  final String id;
  final String serviceRequestId;
  final String? stopId;
  final bool isVerified;
  final int attempts;
  final int maxAttempts;
  final DateTime? expiresAt;
  final DateTime generatedAt;
  final DateTime? verifiedAt;

  factory VerificationCodeResponse.fromJson(Map<String, dynamic> json) {
    return VerificationCodeResponse(
      id: json['id'] as String,
      serviceRequestId: json['service_request_id'] as String,
      stopId: json['stop_id'] as String?,
      isVerified: json['is_verified'] as bool,
      attempts: json['attempts'] as int,
      maxAttempts: json['max_attempts'] as int,
      expiresAt: _toDateTime(json['expires_at']),
      generatedAt: DateTime.parse(json['generated_at'] as String),
      verifiedAt: _toDateTime(json['verified_at']),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'service_request_id': serviceRequestId,
      'stop_id': stopId,
      'is_verified': isVerified,
      'attempts': attempts,
      'max_attempts': maxAttempts,
      'expires_at': expiresAt?.toIso8601String(),
      'generated_at': generatedAt.toIso8601String(),
      'verified_at': verifiedAt?.toIso8601String(),
    };
  }
}

class ProofUploadUrlResponse {
  const ProofUploadUrlResponse({
    required this.presignedUrl,
    required this.fileKey,
    required this.expiresInSeconds,
    required this.proofType,
    required this.mimeType,
  });

  final String presignedUrl;
  final String fileKey;
  final int expiresInSeconds;
  final ProofType proofType;
  final String mimeType;

  factory ProofUploadUrlResponse.fromJson(Map<String, dynamic> json) {
    return ProofUploadUrlResponse(
      presignedUrl: json['presigned_url'] as String,
      fileKey: json['file_key'] as String,
      expiresInSeconds: json['expires_in_seconds'] as int,
      proofType: ProofType.fromJson(json['proof_type'] as String),
      mimeType: json['mime_type'] as String,
    );
  }
}

class ProofImageWithUrlResponse extends ProofImageResponse {
  const ProofImageWithUrlResponse({
    required super.id,
    required super.serviceRequestId,
    required super.stopId,
    required super.proofType,
    required super.fileKey,
    required super.fileName,
    required super.mimeType,
    required super.fileSizeBytes,
    required super.isPrimary,
    required super.uploadedByUserId,
    required super.uploadedByDriverId,
    required super.uploadedAt,
    required this.viewUrl,
  });

  final String viewUrl;

  factory ProofImageWithUrlResponse.fromJson(Map<String, dynamic> json) {
    final proof = ProofImageResponse.fromJson(json);
    return ProofImageWithUrlResponse(
      id: proof.id,
      serviceRequestId: proof.serviceRequestId,
      stopId: proof.stopId,
      proofType: proof.proofType,
      fileKey: proof.fileKey,
      fileName: proof.fileName,
      mimeType: proof.mimeType,
      fileSizeBytes: proof.fileSizeBytes,
      isPrimary: proof.isPrimary,
      uploadedByUserId: proof.uploadedByUserId,
      uploadedByDriverId: proof.uploadedByDriverId,
      uploadedAt: proof.uploadedAt,
      viewUrl: json['view_url'] as String,
    );
  }
}

class DriverCandidateResponse {
  const DriverCandidateResponse({
    required this.driverId,
    required this.distanceKm,
    required this.vehicleType,
    required this.rating,
    required this.priorityScore,
    required this.estimatedArrivalMinutes,
  });

  final String driverId;
  final double distanceKm;
  final String vehicleType;
  final double? rating;
  final double priorityScore;
  final double? estimatedArrivalMinutes;

  factory DriverCandidateResponse.fromJson(Map<String, dynamic> json) {
    return DriverCandidateResponse(
      driverId: json['driver_id'] as String,
      distanceKm: _toDouble(json['distance_km']) ?? 0,
      vehicleType: json['vehicle_type'] as String,
      rating: _toDouble(json['rating']),
      priorityScore: _toDouble(json['priority_score']) ?? 0,
      estimatedArrivalMinutes: _toDouble(json['estimated_arrival_minutes']),
    );
  }
}

class NearbyDriversResponse {
  const NearbyDriversResponse({
    required this.rideId,
    required this.candidates,
    required this.count,
  });

  final String? rideId;
  final List<DriverCandidateResponse> candidates;
  final int count;

  factory NearbyDriversResponse.fromJson(Map<String, dynamic> json) {
    return NearbyDriversResponse(
      rideId: json['ride_id'] as String?,
      candidates: _toList(
        json['candidates'],
        DriverCandidateResponse.fromJson,
      ),
      count: json['count'] as int,
    );
  }
}

double? _toDouble(Object? value) {
  if (value == null) return null;
  if (value is double) return value;
  if (value is int) return value.toDouble();
  return double.parse(value.toString());
}

DateTime? _toDateTime(Object? value) {
  if (value == null) return null;
  if (value is DateTime) return value;
  return DateTime.parse(value.toString());
}

List<T> _toList<T>(
  Object? value,
  T Function(Map<String, dynamic> json) fromJson,
) {
  final items = (value as List<dynamic>? ?? <dynamic>[]);
  return items.map((item) => fromJson(item as Map<String, dynamic>)).toList();
}

T? _toNullableModel<T>(
  Object? value,
  T Function(Map<String, dynamic> json) fromJson,
) {
  if (value == null) return null;
  return fromJson(value as Map<String, dynamic>);
}
