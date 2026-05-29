import 'demo/location_demo_data.dart';
import '../../../common/runtime/runtime_mode.dart';
import '../../../data/rides/ride_models.dart';
import '../domain/location_models.dart';
import '../domain/ride_booking_models.dart';
import '../../../utils/constants/api_constants.dart';
import '../../../utils/http/client.dart';

class SRideRepository {
  const SRideRepository({bool? useDemoData})
      : _delegate = (useDemoData ?? SRuntimeModeConfig.useLocationDemoData)
            ? const _DemoRideRepositoryDelegate()
            : const _HttpRideRepositoryDelegate();

  final _RideRepositoryDelegate _delegate;

  SRuntimeDataSource get runtimeDataSource => _delegate.runtimeDataSource;

  static Map<String, dynamic> buildCityRideRequest({
    required SAddressResult pickup,
    required SAddressResult dropoff,
  }) {
    return {
      'service_type': 'CITY_RIDE',
      'category': 'MINI',
      'pricing_mode': 'FIXED',
      'stops': [
        _stopPayload(
          sequenceOrder: 1,
          stopType: 'PICKUP',
          address: pickup,
        ),
        _stopPayload(
          sequenceOrder: 2,
          stopType: 'DROPOFF',
          address: dropoff,
        ),
      ],
      'detail': {
        'service_type': 'CITY_RIDE',
        'passenger_count': 1,
        'is_ac': false,
        'is_shared_ride': false,
        'requires_otp_start': false,
        'requires_otp_end': false,
      },
      'auto_accept_driver': true,
      'passenger_payment_method': 'CASH',
    };
  }

  static Map<String, dynamic> buildHybridRideRequest({
    required SAddressResult pickup,
    required SAddressResult dropoff,
    required SRideVehicleOffer offer,
    required double passengerOffer,
    required bool autoAcceptDriver,
  }) {
    return buildRideRequest(
      draft: SRideBookingDraft(
        pickup: pickup,
        dropoff: dropoff,
        offer: offer,
        passengerOffer: passengerOffer,
        autoAcceptDriver: autoAcceptDriver,
      ),
    );
  }

  static Map<String, dynamic> buildRideRequest({
    required SRideBookingDraft draft,
  }) {
    final offer = draft.offer;
    final passengerOffer =
        draft.passengerOffer <= 0 ? offer.baseFare : draft.passengerOffer;
    final body = <String, dynamic>{
      'service_type': offer.serviceType.value,
      'category': offer.category.value,
      'pricing_mode': draft.pricingMode.value,
      'stops': [
        _stopPayload(
          sequenceOrder: 1,
          stopType: 'PICKUP',
          address: draft.pickup,
        ),
        _stopPayload(
          sequenceOrder: 2,
          stopType: 'DROPOFF',
          address: draft.dropoff,
        ),
      ],
      'detail': _detailPayload(
        draft: draft,
        passengerOffer: passengerOffer,
      ),
      'auto_accept_driver': draft.autoAcceptDriver,
      'passenger_payment_method': draft.paymentMethod.value,
      if (draft.paymentMethodId != null)
        'passenger_payment_method_id': draft.paymentMethodId,
      if (draft.scheduledAt != null)
        'scheduled_at': draft.scheduledAt!.toIso8601String(),
    };

    if (draft.pricingMode == PricingMode.hybrid) {
      body['baseline_min_price'] = (passengerOffer * 0.85).roundToDouble();
      body['baseline_max_price'] = passengerOffer.roundToDouble();
    }

    return body;
  }

  Future<Map<String, dynamic>> createRide(Map<String, dynamic> body) {
    return _delegate.createRide(body);
  }

  Future<Map<String, dynamic>> fetchRide(String rideId) {
    return _delegate.fetchRide(rideId);
  }

  Future<Map<String, dynamic>> cancelRide({
    required String rideId,
    required String reason,
  }) {
    return _delegate.cancelRide(rideId: rideId, reason: reason);
  }

  Future<List<RideSummaryResponse>> listPassengerRides({
    List<String> statuses = const [],
    int limit = 20,
    int offset = 0,
  }) async {
    return _delegate.listPassengerRides(
      statuses: statuses,
      limit: limit,
      offset: offset,
    );
  }

  Future<List<RecentRideDestinationResponse>> listRecentDestinations({
    int limit = 5,
  }) async {
    return _delegate.listRecentDestinations(limit: limit);
  }

  Future<Map<String, dynamic>> acceptFixedRide(String rideId) {
    return _delegate.acceptFixedRide(rideId);
  }

  Future<Map<String, dynamic>> startRide({
    required String rideId,
    String? verificationCode,
  }) {
    return _delegate.startRide(
      rideId: rideId,
      verificationCode: verificationCode,
    );
  }

  Future<Map<String, dynamic>> completeRide({
    required String rideId,
    String? verificationCode,
    double? finalPrice,
    SCoordinate? driverLocation,
    double? accuracyMeters,
  }) {
    return _delegate.completeRide(
      rideId: rideId,
      verificationCode: verificationCode,
      finalPrice: finalPrice,
      driverLocation: driverLocation,
      accuracyMeters: accuracyMeters,
    );
  }

  Future<Map<String, dynamic>> addStop({
    required String rideId,
    required Map<String, dynamic> stop,
  }) {
    return _delegate.addStop(rideId: rideId, stop: stop);
  }

  Future<Map<String, dynamic>> updateStop({
    required String stopId,
    required double latitude,
    required double longitude,
    required String placeName,
    required String addressLine1,
  }) {
    return _delegate.updateStop(
      stopId: stopId,
      latitude: latitude,
      longitude: longitude,
      placeName: placeName,
      addressLine1: addressLine1,
    );
  }

  Future<Map<String, dynamic>> markStopArrived(String stopId) {
    return _delegate.markStopArrived(stopId);
  }

  Future<Map<String, dynamic>> markStopCompleted(String stopId) {
    return _delegate.markStopCompleted(stopId);
  }

  Future<Map<String, dynamic>> generateVerificationCode({
    required String rideId,
    String? stopId,
    int expiresInMinutes = 15,
    int maxAttempts = 5,
    int length = 6,
  }) {
    return _delegate.generateVerificationCode(
      rideId: rideId,
      stopId: stopId,
      expiresInMinutes: expiresInMinutes,
      maxAttempts: maxAttempts,
      length: length,
    );
  }

  Future<Map<String, dynamic>> verifyCode({
    required String rideId,
    required String code,
    String? userId,
    String? driverId,
  }) {
    return _delegate.verifyCode(
      rideId: rideId,
      code: code,
      userId: userId,
      driverId: driverId,
    );
  }

  Future<Map<String, dynamic>> requestProofUploadUrl({
    required String rideId,
    required String proofType,
    String? fileName,
    String mimeType = 'image/jpeg',
    String? stopId,
  }) {
    return _delegate.requestProofUploadUrl(
      rideId: rideId,
      proofType: proofType,
      fileName: fileName,
      mimeType: mimeType,
      stopId: stopId,
    );
  }

  Future<void> uploadProofBytes({
    required String presignedUrl,
    required List<int> bytes,
    String contentType = 'image/jpeg',
  }) {
    return _delegate.uploadProofBytes(
      presignedUrl: presignedUrl,
      bytes: bytes,
      contentType: contentType,
    );
  }

  Future<Map<String, dynamic>> registerProof({
    required String rideId,
    required String proofType,
    required String fileKey,
    String? fileName,
    String? mimeType,
    int? fileSizeBytes,
    String? checksumSha256,
    bool isPrimary = false,
    String? stopId,
  }) {
    return _delegate.registerProof(
      rideId: rideId,
      proofType: proofType,
      fileKey: fileKey,
      fileName: fileName,
      mimeType: mimeType,
      fileSizeBytes: fileSizeBytes,
      checksumSha256: checksumSha256,
      isPrimary: isPrimary,
      stopId: stopId,
    );
  }

  Future<Map<String, dynamic>> getProofUrl({
    required String rideId,
    required String proofId,
  }) {
    return _delegate.getProofUrl(rideId: rideId, proofId: proofId);
  }

  Future<Map<String, dynamic>> nearbyDrivers({
    required double latitude,
    required double longitude,
    double radiusKm = 5,
    String? rideId,
  }) {
    return _delegate.nearbyDrivers(
      latitude: latitude,
      longitude: longitude,
      radiusKm: radiusKm,
      rideId: rideId,
    );
  }
}

abstract class _RideRepositoryDelegate {
  const _RideRepositoryDelegate();

  SRuntimeDataSource get runtimeDataSource;

  Future<Map<String, dynamic>> createRide(Map<String, dynamic> body);

  Future<Map<String, dynamic>> fetchRide(String rideId);

  Future<Map<String, dynamic>> cancelRide({
    required String rideId,
    required String reason,
  });

  Future<List<RideSummaryResponse>> listPassengerRides({
    List<String> statuses = const [],
    int limit = 20,
    int offset = 0,
  });

  Future<List<RecentRideDestinationResponse>> listRecentDestinations({
    int limit = 5,
  });

  Future<Map<String, dynamic>> acceptFixedRide(String rideId);

  Future<Map<String, dynamic>> startRide({
    required String rideId,
    String? verificationCode,
  });

  Future<Map<String, dynamic>> completeRide({
    required String rideId,
    String? verificationCode,
    double? finalPrice,
    SCoordinate? driverLocation,
    double? accuracyMeters,
  });

  Future<Map<String, dynamic>> addStop({
    required String rideId,
    required Map<String, dynamic> stop,
  });

  Future<Map<String, dynamic>> updateStop({
    required String stopId,
    required double latitude,
    required double longitude,
    required String placeName,
    required String addressLine1,
  });

  Future<Map<String, dynamic>> markStopArrived(String stopId);

  Future<Map<String, dynamic>> markStopCompleted(String stopId);

  Future<Map<String, dynamic>> generateVerificationCode({
    required String rideId,
    String? stopId,
    int expiresInMinutes = 15,
    int maxAttempts = 5,
    int length = 6,
  });

  Future<Map<String, dynamic>> verifyCode({
    required String rideId,
    required String code,
    String? userId,
    String? driverId,
  });

  Future<Map<String, dynamic>> requestProofUploadUrl({
    required String rideId,
    required String proofType,
    String? fileName,
    String mimeType = 'image/jpeg',
    String? stopId,
  });

  Future<void> uploadProofBytes({
    required String presignedUrl,
    required List<int> bytes,
    String contentType = 'image/jpeg',
  });

  Future<Map<String, dynamic>> registerProof({
    required String rideId,
    required String proofType,
    required String fileKey,
    String? fileName,
    String? mimeType,
    int? fileSizeBytes,
    String? checksumSha256,
    bool isPrimary = false,
    String? stopId,
  });

  Future<Map<String, dynamic>> getProofUrl({
    required String rideId,
    required String proofId,
  });

  Future<Map<String, dynamic>> nearbyDrivers({
    required double latitude,
    required double longitude,
    double radiusKm = 5,
    String? rideId,
  });
}

class _DemoRideRepositoryDelegate extends _RideRepositoryDelegate {
  const _DemoRideRepositoryDelegate();

  @override
  SRuntimeDataSource get runtimeDataSource => SRuntimeDataSource.demo;

  @override
  Future<Map<String, dynamic>> createRide(Map<String, dynamic> body) {
    return Future.value(SLocationDemoData.createdRide(body));
  }

  @override
  Future<Map<String, dynamic>> fetchRide(String rideId) {
    return Future.value(SLocationDemoData.rideDetails(rideId));
  }

  @override
  Future<Map<String, dynamic>> cancelRide({
    required String rideId,
    required String reason,
  }) {
    return Future.value(SLocationDemoData.canceledRide(rideId, reason));
  }

  @override
  Future<List<RideSummaryResponse>> listPassengerRides({
    List<String> statuses = const [],
    int limit = 20,
    int offset = 0,
  }) async {
    return SLocationDemoData.passengerRideSummaries()
        .map((item) => RideSummaryResponse.fromJson(item))
        .toList(growable: false);
  }

  @override
  Future<List<RecentRideDestinationResponse>> listRecentDestinations({
    int limit = 5,
  }) async {
    return SLocationDemoData.recentRideDestinations()
        .map(RecentRideDestinationResponse.fromJson)
        .take(limit)
        .toList(growable: false);
  }

  @override
  Future<Map<String, dynamic>> acceptFixedRide(String rideId) {
    return Future.value(SLocationDemoData.rideAccepted(rideId));
  }

  @override
  Future<Map<String, dynamic>> startRide({
    required String rideId,
    String? verificationCode,
  }) {
    return Future.value(
      SLocationDemoData.rideStarted(
        rideId: rideId,
        verificationCode: verificationCode,
      ),
    );
  }

  @override
  Future<Map<String, dynamic>> completeRide({
    required String rideId,
    String? verificationCode,
    double? finalPrice,
    SCoordinate? driverLocation,
    double? accuracyMeters,
  }) {
    return Future.value(
      SLocationDemoData.rideCompleted(
        rideId: rideId,
        verificationCode: verificationCode,
        finalPrice: finalPrice,
      ),
    );
  }

  @override
  Future<Map<String, dynamic>> addStop({
    required String rideId,
    required Map<String, dynamic> stop,
  }) {
    return Future.value(SLocationDemoData.addedStop(rideId: rideId, stop: stop));
  }

  @override
  Future<Map<String, dynamic>> updateStop({
    required String stopId,
    required double latitude,
    required double longitude,
    required String placeName,
    required String addressLine1,
  }) {
    return Future.value({
      'id': stopId,
      'latitude': latitude,
      'longitude': longitude,
      'place_name': placeName,
      'address_line_1': addressLine1,
      'stop_type': 'DROPOFF',
    });
  }

  @override
  Future<Map<String, dynamic>> markStopArrived(String stopId) {
    return Future.value(SLocationDemoData.stopArrived(stopId));
  }

  @override
  Future<Map<String, dynamic>> markStopCompleted(String stopId) {
    return Future.value(SLocationDemoData.stopCompleted(stopId));
  }

  @override
  Future<Map<String, dynamic>> generateVerificationCode({
    required String rideId,
    String? stopId,
    int expiresInMinutes = 15,
    int maxAttempts = 5,
    int length = 6,
  }) {
    return Future.value(
      SLocationDemoData.verificationCode(rideId: rideId, stopId: stopId),
    );
  }

  @override
  Future<Map<String, dynamic>> verifyCode({
    required String rideId,
    required String code,
    String? userId,
    String? driverId,
  }) {
    return Future.value(
      SLocationDemoData.verificationCode(rideId: rideId, isVerified: true),
    );
  }

  @override
  Future<Map<String, dynamic>> requestProofUploadUrl({
    required String rideId,
    required String proofType,
    String? fileName,
    String mimeType = 'image/jpeg',
    String? stopId,
  }) {
    return Future.value(
      SLocationDemoData.proofUploadUrl(
        proofType: proofType,
        mimeType: mimeType,
      ),
    );
  }

  @override
  Future<void> uploadProofBytes({
    required String presignedUrl,
    required List<int> bytes,
    String contentType = 'image/jpeg',
  }) {
    return Future.value();
  }

  @override
  Future<Map<String, dynamic>> registerProof({
    required String rideId,
    required String proofType,
    required String fileKey,
    String? fileName,
    String? mimeType,
    int? fileSizeBytes,
    String? checksumSha256,
    bool isPrimary = false,
    String? stopId,
  }) {
    return Future.value(
      SLocationDemoData.proofImage(
        rideId: rideId,
        proofType: proofType,
        fileKey: fileKey,
        fileName: fileName,
        mimeType: mimeType,
        fileSizeBytes: fileSizeBytes,
        stopId: stopId,
      ),
    );
  }

  @override
  Future<Map<String, dynamic>> getProofUrl({
    required String rideId,
    required String proofId,
  }) {
    return Future.value(
      SLocationDemoData.proofImage(
        rideId: rideId,
        proofType: 'PICKUP',
        fileKey: 'demo/ride/proofs/pickup_proof.jpg',
        withViewUrl: true,
      ),
    );
  }

  @override
  Future<Map<String, dynamic>> nearbyDrivers({
    required double latitude,
    required double longitude,
    double radiusKm = 5,
    String? rideId,
  }) {
    return Future.value(
      SLocationDemoData.nearbyDrivers(
        latitude: latitude,
        longitude: longitude,
        rideId: rideId,
      ),
    );
  }
}

class _HttpRideRepositoryDelegate extends _RideRepositoryDelegate {
  const _HttpRideRepositoryDelegate();

  @override
  SRuntimeDataSource get runtimeDataSource => SRuntimeDataSource.real;

  @override
  Future<Map<String, dynamic>> createRide(Map<String, dynamic> body) {
    return SHttpClient.post(
      '/rides',
      service: SApiService.ride,
      requiresAuth: true,
      body: body,
    );
  }

  @override
  Future<Map<String, dynamic>> fetchRide(String rideId) {
    return SHttpClient.get(
      '/rides/$rideId',
      service: SApiService.ride,
      requiresAuth: true,
    );
  }

  @override
  Future<Map<String, dynamic>> cancelRide({
    required String rideId,
    required String reason,
  }) {
    return SHttpClient.post(
      '/rides/$rideId/cancel',
      service: SApiService.ride,
      requiresAuth: true,
      body: {'reason': reason},
    );
  }

  @override
  Future<List<RideSummaryResponse>> listPassengerRides({
    List<String> statuses = const [],
    int limit = 20,
    int offset = 0,
  }) async {
    final baseQuery = Uri(
      queryParameters: {
        'limit': limit.toString(),
        'offset': offset.toString(),
      },
    ).query;
    final statusQuery = statuses
        .map((status) => 'status=${Uri.encodeQueryComponent(status)}')
        .join('&');
    final query = [
      baseQuery,
      if (statusQuery.isNotEmpty) statusQuery,
    ].join('&');

    final data = await SHttpClient.get(
      query.isEmpty ? '/rides' : '/rides?$query',
      service: SApiService.ride,
      requiresAuth: true,
    );
    final values = data['data'];
    if (values is! List) return const [];
    return values
        .whereType<Map<String, dynamic>>()
        .map(RideSummaryResponse.fromJson)
        .toList(growable: false);
  }

  @override
  Future<List<RecentRideDestinationResponse>> listRecentDestinations({
    int limit = 5,
  }) async {
    final query = Uri(queryParameters: {'limit': limit.toString()}).query;
    final data = await SHttpClient.get(
      '/rides/recent-destinations?$query',
      service: SApiService.ride,
      requiresAuth: true,
    );
    final values = data['data'] ?? data;
    if (values is! List) return const [];
    return values
        .whereType<Map<String, dynamic>>()
        .map(RecentRideDestinationResponse.fromJson)
        .toList(growable: false);
  }

  @override
  Future<Map<String, dynamic>> acceptFixedRide(String rideId) {
    return SHttpClient.post(
      '/rides/$rideId/accept',
      service: SApiService.ride,
      requiresAuth: true,
    );
  }

  @override
  Future<Map<String, dynamic>> startRide({
    required String rideId,
    String? verificationCode,
  }) {
    return SHttpClient.post(
      '/rides/$rideId/start',
      service: SApiService.ride,
      requiresAuth: true,
      body: {
        if (verificationCode != null) 'verification_code': verificationCode,
      },
    );
  }

  @override
  Future<Map<String, dynamic>> completeRide({
    required String rideId,
    String? verificationCode,
    double? finalPrice,
    SCoordinate? driverLocation,
    double? accuracyMeters,
  }) {
    return SHttpClient.post(
      '/rides/$rideId/complete',
      service: SApiService.ride,
      requiresAuth: true,
      body: {
        if (verificationCode != null) 'verification_code': verificationCode,
        if (finalPrice != null) 'final_price': finalPrice,
        if (driverLocation != null) ...{
          'driver_latitude': driverLocation.latitude,
          'driver_longitude': driverLocation.longitude,
        },
        if (accuracyMeters != null) 'accuracy_meters': accuracyMeters,
      },
    );
  }

  @override
  Future<Map<String, dynamic>> addStop({
    required String rideId,
    required Map<String, dynamic> stop,
  }) {
    return SHttpClient.post(
      '/rides/$rideId/stops',
      service: SApiService.ride,
      requiresAuth: true,
      body: stop,
    );
  }

  @override
  Future<Map<String, dynamic>> updateStop({
    required String stopId,
    required double latitude,
    required double longitude,
    required String placeName,
    required String addressLine1,
  }) {
    return SHttpClient.patch(
      '/stops/$stopId',
      service: SApiService.ride,
      requiresAuth: true,
      body: {
        'latitude': latitude,
        'longitude': longitude,
        'place_name': placeName,
        'address_line_1': addressLine1,
      },
    );
  }

  @override
  Future<Map<String, dynamic>> markStopArrived(String stopId) {
    return SHttpClient.post(
      '/stops/$stopId/arrived',
      service: SApiService.ride,
      requiresAuth: true,
    );
  }

  @override
  Future<Map<String, dynamic>> markStopCompleted(String stopId) {
    return SHttpClient.post(
      '/stops/$stopId/completed',
      service: SApiService.ride,
      requiresAuth: true,
    );
  }

  @override
  Future<Map<String, dynamic>> generateVerificationCode({
    required String rideId,
    String? stopId,
    int expiresInMinutes = 15,
    int maxAttempts = 5,
    int length = 6,
  }) {
    return SHttpClient.post(
      '/rides/$rideId/verification-codes',
      service: SApiService.ride,
      requiresAuth: true,
      body: {
        if (stopId != null) 'stop_id': stopId,
        'expires_in_minutes': expiresInMinutes,
        'max_attempts': maxAttempts,
        'length': length,
      },
    );
  }

  @override
  Future<Map<String, dynamic>> verifyCode({
    required String rideId,
    required String code,
    String? userId,
    String? driverId,
  }) {
    return SHttpClient.post(
      '/rides/$rideId/verification-codes/verify',
      service: SApiService.ride,
      requiresAuth: true,
      body: {
        'code': code,
        if (userId != null) 'user_id': userId,
        if (driverId != null) 'driver_id': driverId,
      },
    );
  }

  @override
  Future<Map<String, dynamic>> requestProofUploadUrl({
    required String rideId,
    required String proofType,
    String? fileName,
    String mimeType = 'image/jpeg',
    String? stopId,
  }) {
    return SHttpClient.post(
      '/rides/$rideId/proofs/upload-url',
      service: SApiService.ride,
      requiresAuth: true,
      body: {
        'proof_type': proofType,
        if (fileName != null) 'file_name': fileName,
        'mime_type': mimeType,
        if (stopId != null) 'stop_id': stopId,
      },
    );
  }

  @override
  Future<void> uploadProofBytes({
    required String presignedUrl,
    required List<int> bytes,
    String contentType = 'image/jpeg',
  }) {
    return SHttpClient.putBytesToAbsoluteUrl(
      presignedUrl,
      bytes: bytes,
      contentType: contentType,
    );
  }

  @override
  Future<Map<String, dynamic>> registerProof({
    required String rideId,
    required String proofType,
    required String fileKey,
    String? fileName,
    String? mimeType,
    int? fileSizeBytes,
    String? checksumSha256,
    bool isPrimary = false,
    String? stopId,
  }) {
    return SHttpClient.post(
      '/rides/$rideId/proofs',
      service: SApiService.ride,
      requiresAuth: true,
      body: {
        'proof_type': proofType,
        'file_key': fileKey,
        if (fileName != null) 'file_name': fileName,
        if (mimeType != null) 'mime_type': mimeType,
        if (fileSizeBytes != null) 'file_size_bytes': fileSizeBytes,
        if (checksumSha256 != null) 'checksum_sha256': checksumSha256,
        'is_primary': isPrimary,
        if (stopId != null) 'stop_id': stopId,
      },
    );
  }

  @override
  Future<Map<String, dynamic>> getProofUrl({
    required String rideId,
    required String proofId,
  }) {
    return SHttpClient.get(
      '/rides/$rideId/proofs/$proofId/url',
      service: SApiService.ride,
      requiresAuth: true,
    );
  }

  @override
  Future<Map<String, dynamic>> nearbyDrivers({
    required double latitude,
    required double longitude,
    double radiusKm = 5,
    String? rideId,
  }) {
    final query = Uri(
      queryParameters: {
        'lat': latitude.toString(),
        'lng': longitude.toString(),
        'radius': radiusKm.toString(),
        if (rideId != null) 'ride_id': rideId,
      },
    ).query;

    return SHttpClient.get(
      '/drivers/nearby?$query',
      service: SApiService.ride,
      requiresAuth: true,
    );
  }
}

Map<String, dynamic> _detailPayload({
  required SRideBookingDraft draft,
  required double passengerOffer,
}) {
  final offer = draft.offer;
  return switch (offer.serviceType.value) {
    'INTERCITY' => {
        'service_type': 'INTERCITY',
        'passenger_count': draft.intercity.passengerCount,
        'luggage_count': draft.intercity.luggageCount,
        'child_count': draft.intercity.childCount,
        'senior_count': draft.intercity.seniorCount,
        'allowed_fuel_types':
            draft.intercity.allowedFuelTypes.map((type) => type.value).toList(),
        if (draft.intercity.preferredDepartureTime != null)
          'preferred_departure_time':
              draft.intercity.preferredDepartureTime!.toIso8601String(),
        if (draft.intercity.departureFlexibilityMinutes != null)
          'departure_time_flexibility_minutes':
              draft.intercity.departureFlexibilityMinutes,
        'is_round_trip': draft.intercity.isRoundTrip,
        if (draft.intercity.returnTime != null)
          'return_time': draft.intercity.returnTime!.toIso8601String(),
        'vehicle_type_requested': offer.vehicleType,
        if (draft.intercity.minVehicleCapacity != null)
          'min_vehicle_capacity': draft.intercity.minVehicleCapacity,
        'requires_luggage_carrier': draft.intercity.requiresLuggageCarrier,
        'is_shared_ride': draft.intercity.isSharedRide,
        if (draft.intercity.isSharedRide &&
            draft.intercity.maxCoPassengers != null)
          'max_co_passengers': draft.intercity.maxCoPassengers,
        'requires_identity_verification':
            draft.intercity.requiresIdentityVerification,
        if ((draft.intercity.emergencyContactName ?? '').trim().isNotEmpty)
          'emergency_contact_name': draft.intercity.emergencyContactName,
        if ((draft.intercity.emergencyContactNumber ?? '').trim().isNotEmpty)
          'emergency_contact_number': draft.intercity.emergencyContactNumber,
        'estimated_price': passengerOffer,
      },
    'FREIGHT' => {
        'service_type': 'FREIGHT',
        'cargo_weight': draft.freight.cargoWeight,
        'cargo_type': draft.freight.cargoType,
        'vehicle_type': offer.vehicleType,
        'requires_loader': draft.freight.requiresLoader,
        'is_fragile': draft.freight.isFragile,
        'requires_temperature_control':
            draft.freight.requiresTemperatureControl,
        if (draft.freight.declaredValue != null)
          'declared_value': draft.freight.declaredValue,
        if ((draft.freight.commodityNotes ?? '').trim().isNotEmpty)
          'commodity_notes': draft.freight.commodityNotes,
        if (draft.freight.estimatedLoadHours != null)
          'estimated_load_hours': draft.freight.estimatedLoadHours,
      },
    'COURIER' => {
        'service_type': 'COURIER',
        'item_description': draft.courier.itemDescription,
        if (draft.courier.itemWeight != null)
          'item_weight': draft.courier.itemWeight,
        'total_parcels': draft.courier.totalParcels,
        'recipient_name': draft.courier.recipientName,
        'recipient_phone': draft.courier.recipientPhone,
        if ((draft.courier.recipientEmail ?? '').trim().isNotEmpty)
          'recipient_email': draft.courier.recipientEmail,
        'requires_signature': draft.courier.requiresSignature,
        'is_fragile': draft.courier.isFragile,
        if (draft.courier.declaredValue != null)
          'declared_value': draft.courier.declaredValue,
        if ((draft.courier.specialHandlingNotes ?? '').trim().isNotEmpty)
          'special_handling_notes': draft.courier.specialHandlingNotes,
      },
    'GROCERY' => {
        'service_type': 'GROCERY',
        'store_id': draft.grocery.storeId,
        'total_items': draft.grocery.totalItems,
        if ((draft.grocery.specialNotes ?? '').trim().isNotEmpty)
          'special_notes': draft.grocery.specialNotes,
        'contactless_delivery': draft.grocery.contactlessDelivery,
        if (draft.grocery.estimatedBagCount != null)
          'estimated_bag_count': draft.grocery.estimatedBagCount,
      },
    _ => {
        'service_type': 'CITY_RIDE',
        'passenger_count': draft.city.passengerCount,
        'is_ac': offer.requiresAc,
        'preferred_vehicle_type': offer.vehicleType,
        'driver_gender_preference': draft.city.driverGenderPreference.value,
        'is_shared_ride': false,
        'allowed_fuel_types':
            draft.city.allowedFuelTypes.map((type) => type.value).toList(),
        'is_smoking_allowed': draft.city.isSmokingAllowed,
        'is_pet_allowed': draft.city.isPetAllowed,
        'requires_wheelchair_access': draft.city.requiresWheelchairAccess,
        if (draft.city.maxWaitTimeMinutes != null)
          'max_wait_time_minutes': draft.city.maxWaitTimeMinutes,
        'requires_otp_start': draft.city.requiresOtpStart,
        'requires_otp_end': draft.city.requiresOtpEnd,
        'estimated_price': passengerOffer,
      },
  };
}

Map<String, dynamic> _stopPayload({
  required int sequenceOrder,
  required String stopType,
  required SAddressResult address,
}) {
  return {
    'sequence_order': sequenceOrder,
    'stop_type': stopType,
    'latitude': address.coordinate.latitude,
    'longitude': address.coordinate.longitude,
    'place_name': address.formatted,
    'address_line_1': address.formatted,
    'city': address.city,
    'country': address.country,
    'postal_code': address.postalCode,
  };
}
