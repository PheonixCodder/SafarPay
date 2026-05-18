import '../../../../../utils/constants/images.dart';

enum SDriverWorkCategoryType {
  city,
  courier,
  intercity,
  freight,
  grocery,
}

enum SDriverVehicleType {
  car,
  motorcycle,
  rickshaw,
  van,
  pickup,
  miniTruck,
  truck,
}

enum SVerificationVehicleType {
  moto('moto'),
  economy('economy'),
  comfort('comfort'),
  freight('freight');

  const SVerificationVehicleType(this.value);

  final String value;

  String get label {
    return switch (this) {
      SVerificationVehicleType.moto => 'Moto',
      SVerificationVehicleType.economy => 'Economy',
      SVerificationVehicleType.comfort => 'Comfort',
      SVerificationVehicleType.freight => 'Freight',
    };
  }

  static SVerificationVehicleType fromDisplayVehicle(
    SDriverVehicleType vehicle,
  ) {
    return switch (vehicle) {
      SDriverVehicleType.motorcycle => SVerificationVehicleType.moto,
      SDriverVehicleType.pickup ||
      SDriverVehicleType.miniTruck ||
      SDriverVehicleType.truck =>
        SVerificationVehicleType.freight,
      SDriverVehicleType.car ||
      SDriverVehicleType.rickshaw ||
      SDriverVehicleType.van =>
        SVerificationVehicleType.economy,
    };
  }
}

enum SVerificationOverallStatus {
  notStarted,
  pending,
  underReview,
  verified,
  rejected,
}

enum SVerificationGroupStatus {
  notSubmitted,
  pending,
  verified,
  rejected,
}

enum SVerificationStep {
  identity,
  license,
  selfie,
  vehicle,
}

String _formatBackendDate(DateTime date) {
  final month = date.month.toString().padLeft(2, '0');
  final day = date.day.toString().padLeft(2, '0');
  return '${date.year}-$month-$day';
}

class SDriverWorkCategory {
  const SDriverWorkCategory({
    required this.type,
    required this.title,
    required this.subtitle,
    required this.image,
  });

  final SDriverWorkCategoryType type;
  final String title;
  final String subtitle;
  final String image;
}

class SDriverVehicleOption {
  const SDriverVehicleOption({
    required this.type,
    required this.title,
    required this.image,
  });

  final SDriverVehicleType type;
  final String title;
  final String image;
}

class SDriverRegistrationCatalog {
  SDriverRegistrationCatalog._();

  static const List<SDriverWorkCategory> categories = [
    SDriverWorkCategory(
      type: SDriverWorkCategoryType.city,
      title: 'City driver',
      subtitle: 'Drive passengers around the city',
      image: SImages.cityRides,
    ),
    SDriverWorkCategory(
      type: SDriverWorkCategoryType.courier,
      title: 'Courier',
      subtitle: 'Deliver packages up to 20kg within the city',
      image: SImages.courier,
    ),
    SDriverWorkCategory(
      type: SDriverWorkCategoryType.intercity,
      title: 'City to City driver',
      subtitle: 'Transport passengers between cities',
      image: SImages.cityToCity,
    ),
    SDriverWorkCategory(
      type: SDriverWorkCategoryType.freight,
      title: 'Freight driver',
      subtitle: 'Deliver cargoes over 20kg',
      image: SImages.freight,
    ),
    SDriverWorkCategory(
      type: SDriverWorkCategoryType.grocery,
      title: 'Grocery delivery',
      subtitle: 'Deliver groceries from local stores',
      image: SImages.groceries,
    ),
  ];

  static List<SDriverVehicleOption> vehiclesFor(
    SDriverWorkCategoryType category,
  ) {
    return switch (category) {
      SDriverWorkCategoryType.city => const [
          SDriverVehicleOption(
            type: SDriverVehicleType.car,
            title: 'Car',
            image: SImages.driverVehicleCar,
          ),
          SDriverVehicleOption(
            type: SDriverVehicleType.motorcycle,
            title: 'Motorcycle',
            image: SImages.driverVehicleMotorcycle,
          ),
          SDriverVehicleOption(
            type: SDriverVehicleType.rickshaw,
            title: 'Rickshaw',
            image: SImages.driverVehicleRickshaw,
          ),
        ],
      SDriverWorkCategoryType.courier => const [
          SDriverVehicleOption(
            type: SDriverVehicleType.motorcycle,
            title: 'Motorcycle',
            image: SImages.driverVehicleMotorcycle,
          ),
          SDriverVehicleOption(
            type: SDriverVehicleType.car,
            title: 'Car',
            image: SImages.driverVehicleCar,
          ),
          SDriverVehicleOption(
            type: SDriverVehicleType.rickshaw,
            title: 'Rickshaw',
            image: SImages.driverVehicleRickshaw,
          ),
        ],
      SDriverWorkCategoryType.intercity => const [
          SDriverVehicleOption(
            type: SDriverVehicleType.car,
            title: 'Car',
            image: SImages.driverVehicleCar,
          ),
          SDriverVehicleOption(
            type: SDriverVehicleType.van,
            title: 'Van',
            image: SImages.driverVehicleVan,
          ),
        ],
      SDriverWorkCategoryType.freight => const [
          SDriverVehicleOption(
            type: SDriverVehicleType.pickup,
            title: 'Pickup',
            image: SImages.driverVehiclePickup,
          ),
          SDriverVehicleOption(
            type: SDriverVehicleType.miniTruck,
            title: 'Mini truck',
            image: SImages.driverVehicleMiniTruck,
          ),
          SDriverVehicleOption(
            type: SDriverVehicleType.truck,
            title: 'Truck',
            image: SImages.driverVehicleTruck,
          ),
        ],
      SDriverWorkCategoryType.grocery => const [
          SDriverVehicleOption(
            type: SDriverVehicleType.motorcycle,
            title: 'Motorcycle',
            image: SImages.driverVehicleMotorcycle,
          ),
          SDriverVehicleOption(
            type: SDriverVehicleType.car,
            title: 'Car',
            image: SImages.driverVehicleCar,
          ),
        ],
    };
  }
}

class SPresignedUrlResponse {
  const SPresignedUrlResponse({
    required this.key,
    required this.url,
  });

  final String key;
  final String url;

  factory SPresignedUrlResponse.fromJson(Map<String, dynamic> json) {
    return SPresignedUrlResponse(
      key: json['key']?.toString() ?? '',
      url: json['url']?.toString() ?? '',
    );
  }
}

class SDocumentUploadUrlsResponse {
  const SDocumentUploadUrlsResponse({
    required this.message,
    required this.urls,
  });

  final String message;
  final Map<String, SPresignedUrlResponse> urls;

  factory SDocumentUploadUrlsResponse.fromJson(Map<String, dynamic> json) {
    final rawUrls = json['urls'];
    final urls = <String, SPresignedUrlResponse>{};

    if (rawUrls is Map<String, dynamic>) {
      for (final entry in rawUrls.entries) {
        final value = entry.value;
        if (value is Map<String, dynamic>) {
          urls[entry.key] = SPresignedUrlResponse.fromJson(value);
        }
      }
    }

    return SDocumentUploadUrlsResponse(
      message: json['message']?.toString() ?? '',
      urls: urls,
    );
  }
}

class SCnicSubmissionRequest {
  const SCnicSubmissionRequest({
    required this.idNumber,
    required this.expiryDate,
  });

  final String idNumber;
  final DateTime expiryDate;

  Map<String, dynamic> toJson() {
    return {
      'id_number': idNumber,
      'expiry_date': _formatBackendDate(expiryDate),
    };
  }
}

class SDriverLicenseSubmissionRequest {
  const SDriverLicenseSubmissionRequest({
    required this.licenseNumber,
    required this.expiryDate,
  });

  final String licenseNumber;
  final DateTime expiryDate;

  Map<String, dynamic> toJson() {
    return {
      'license_number': licenseNumber,
      'expiry_date': _formatBackendDate(expiryDate),
    };
  }
}

class SSelfieSubmissionRequest {
  const SSelfieSubmissionRequest();

  Map<String, dynamic> toJson() => {};
}

class SVehicleSubmissionRequest {
  const SVehicleSubmissionRequest({
    required this.brand,
    required this.model,
    required this.color,
    required this.vehicleType,
    required this.maxPassengers,
    required this.plateNumber,
    required this.productionYear,
    this.vehicleId,
  });

  final String? vehicleId;
  final String brand;
  final String model;
  final String color;
  final SVerificationVehicleType vehicleType;
  final int maxPassengers;
  final String plateNumber;
  final int productionYear;

  Map<String, dynamic> toJson() {
    return {
      'vehicle_id': vehicleId,
      'brand': brand,
      'model': model,
      'color': color,
      'vehicle_type': vehicleType.value,
      'max_passengers': maxPassengers,
      'plate_number': plateNumber,
      'production_year': productionYear,
    };
  }
}

class SVerificationDocumentStatus {
  const SVerificationDocumentStatus({
    required this.id,
    required this.documentType,
    required this.status,
    this.rejectionReason,
    this.submittedAt,
  });

  final String id;
  final String documentType;
  final SVerificationGroupStatus status;
  final String? rejectionReason;
  final DateTime? submittedAt;

  factory SVerificationDocumentStatus.fromJson(Map<String, dynamic> json) {
    return SVerificationDocumentStatus(
      id: json['id']?.toString() ?? '',
      documentType: json['document_type']?.toString() ?? '',
      status: SVerificationStatusParser.group(json['status']?.toString()),
      rejectionReason: json['rejection_reason'] as String?,
      submittedAt: DateTime.tryParse(json['submitted_at']?.toString() ?? ''),
    );
  }
}

class SRequirementGroupStatus {
  const SRequirementGroupStatus({
    required this.status,
    required this.documents,
    this.rejectionReason,
  });

  final SVerificationGroupStatus status;
  final List<SVerificationDocumentStatus> documents;
  final String? rejectionReason;

  factory SRequirementGroupStatus.fromJson(Map<String, dynamic>? json) {
    if (json == null) {
      return const SRequirementGroupStatus(
        status: SVerificationGroupStatus.notSubmitted,
        documents: [],
      );
    }

    final documents = json['documents'];
    return SRequirementGroupStatus(
      status: SVerificationStatusParser.group(json['status']?.toString()),
      documents: documents is List
          ? documents
              .whereType<Map<String, dynamic>>()
              .map(SVerificationDocumentStatus.fromJson)
              .toList()
          : const [],
      rejectionReason: json['rejection_reason'] as String?,
    );
  }
}

class SVerificationStatusResponse {
  const SVerificationStatusResponse({
    required this.overallStatus,
    required this.identity,
    required this.license,
    required this.selfie,
    required this.vehicle,
    this.driverId,
  });

  final String? driverId;
  final SVerificationOverallStatus overallStatus;
  final SRequirementGroupStatus identity;
  final SRequirementGroupStatus license;
  final SRequirementGroupStatus selfie;
  final SRequirementGroupStatus vehicle;

  factory SVerificationStatusResponse.fromJson(Map<String, dynamic> json) {
    return SVerificationStatusResponse(
      driverId: json['driver_id']?.toString(),
      overallStatus:
          SVerificationStatusParser.overall(json['overall_status']?.toString()),
      identity: SRequirementGroupStatus.fromJson(
        json['identity'] as Map<String, dynamic>?,
      ),
      license: SRequirementGroupStatus.fromJson(
        json['license'] as Map<String, dynamic>?,
      ),
      selfie: SRequirementGroupStatus.fromJson(
        json['selfie'] as Map<String, dynamic>?,
      ),
      vehicle: SRequirementGroupStatus.fromJson(
        json['vehicle'] as Map<String, dynamic>?,
      ),
    );
  }

  SRequirementGroupStatus groupFor(SVerificationStep step) {
    return switch (step) {
      SVerificationStep.identity => identity,
      SVerificationStep.license => license,
      SVerificationStep.selfie => selfie,
      SVerificationStep.vehicle => vehicle,
    };
  }
}

class SReviewSubmissionResponse {
  const SReviewSubmissionResponse({
    required this.status,
    required this.estimatedTimeSeconds,
  });

  final String status;
  final int estimatedTimeSeconds;

  factory SReviewSubmissionResponse.fromJson(Map<String, dynamic> json) {
    return SReviewSubmissionResponse(
      status: json['status']?.toString() ?? '',
      estimatedTimeSeconds:
          int.tryParse(json['estimated_time_seconds']?.toString() ?? '') ?? 0,
    );
  }
}

class SVerificationStatusParser {
  SVerificationStatusParser._();

  static SVerificationOverallStatus overall(String? value) {
    return switch (value) {
      'pending' => SVerificationOverallStatus.pending,
      'under_review' => SVerificationOverallStatus.underReview,
      'verified' => SVerificationOverallStatus.verified,
      'rejected' => SVerificationOverallStatus.rejected,
      _ => SVerificationOverallStatus.notStarted,
    };
  }

  static SVerificationGroupStatus group(String? value) {
    return switch (value) {
      'pending' => SVerificationGroupStatus.pending,
      'verified' => SVerificationGroupStatus.verified,
      'rejected' => SVerificationGroupStatus.rejected,
      _ => SVerificationGroupStatus.notSubmitted,
    };
  }
}
