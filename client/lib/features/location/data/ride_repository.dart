import 'demo/location_demo_data.dart';
import '../domain/location_models.dart';
import '../domain/ride_booking_models.dart';

class SRideRepository {
  const SRideRepository();

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
        'requires_otp_start': true,
        'requires_otp_end': true,
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
    final minPrice = (passengerOffer * 0.85).roundToDouble();
    final maxPrice = passengerOffer.roundToDouble();

    return {
      'service_type': offer.serviceType.value,
      'category': offer.category.value,
      'pricing_mode': 'HYBRID',
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
      'detail': _detailPayload(
        offer: offer,
        pickup: pickup,
        dropoff: dropoff,
        passengerOffer: passengerOffer,
      ),
      'baseline_min_price': minPrice,
      'baseline_max_price': maxPrice,
      'auto_accept_driver': autoAcceptDriver,
      'passenger_payment_method': 'CASH',
    };
  }

  Future<Map<String, dynamic>> createRide(Map<String, dynamic> body) {
    return Future.value(SLocationDemoData.createdRide(body));
    // return SHttpClient.post(
    //   '/rides',
    //   service: SApiService.ride,
    //   requiresAuth: true,
    //   body: body,
    // );
  }

  Future<Map<String, dynamic>> fetchRide(String rideId) {
    return Future.value(SLocationDemoData.rideDetails(rideId));
    // return SHttpClient.get(
    //   '/rides/$rideId',
    //   service: SApiService.ride,
    //   requiresAuth: true,
    // );
  }

  Future<Map<String, dynamic>> cancelRide({
    required String rideId,
    required String reason,
  }) {
    return Future.value(SLocationDemoData.canceledRide(rideId, reason));
    // return SHttpClient.post(
    //   '/rides/$rideId/cancel',
    //   service: SApiService.ride,
    //   requiresAuth: true,
    //   body: {'reason': reason},
    // );
  }

  Future<List<dynamic>> listPassengerRides({
    List<String> statuses = const [],
    int limit = 20,
    int offset = 0,
  }) async {
    return SLocationDemoData.passengerRideSummaries();
    // final query = Uri(
    //   queryParameters: {
    //     'limit': limit.toString(),
    //     'offset': offset.toString(),
    //     if (statuses.isNotEmpty) 'status': statuses,
    //   },
    // ).query;
    //
    // final data = await SHttpClient.get(
    //   '/rides?$query',
    //   service: SApiService.ride,
    //   requiresAuth: true,
    // );
    // final values = data['data'];
    // return values is List ? values : const [];
  }

  Future<Map<String, dynamic>> acceptFixedRide(String rideId) {
    return Future.value(SLocationDemoData.rideAccepted(rideId));
    // return SHttpClient.post(
    //   '/rides/$rideId/accept',
    //   service: SApiService.ride,
    //   requiresAuth: true,
    // );
  }

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
    // return SHttpClient.post(
    //   '/rides/$rideId/start',
    //   service: SApiService.ride,
    //   requiresAuth: true,
    //   body: {
    //     if (verificationCode != null) 'verification_code': verificationCode,
    //   },
    // );
  }

  Future<Map<String, dynamic>> completeRide({
    required String rideId,
    String? verificationCode,
    double? finalPrice,
  }) {
    return Future.value(
      SLocationDemoData.rideCompleted(
        rideId: rideId,
        verificationCode: verificationCode,
        finalPrice: finalPrice,
      ),
    );
    // return SHttpClient.post(
    //   '/rides/$rideId/complete',
    //   service: SApiService.ride,
    //   requiresAuth: true,
    //   body: {
    //     if (verificationCode != null) 'verification_code': verificationCode,
    //     if (finalPrice != null) 'final_price': finalPrice,
    //   },
    // );
  }

  Future<Map<String, dynamic>> addStop({
    required String rideId,
    required Map<String, dynamic> stop,
  }) {
    return Future.value(
      SLocationDemoData.addedStop(rideId: rideId, stop: stop),
    );
    // return SHttpClient.post(
    //   '/rides/$rideId/stops',
    //   service: SApiService.ride,
    //   requiresAuth: true,
    //   body: stop,
    // );
  }

  Future<Map<String, dynamic>> markStopArrived(String stopId) {
    return Future.value(SLocationDemoData.stopArrived(stopId));
    // return SHttpClient.post(
    //   '/stops/$stopId/arrived',
    //   service: SApiService.ride,
    //   requiresAuth: true,
    // );
  }

  Future<Map<String, dynamic>> markStopCompleted(String stopId) {
    return Future.value(SLocationDemoData.stopCompleted(stopId));
    // return SHttpClient.post(
    //   '/stops/$stopId/completed',
    //   service: SApiService.ride,
    //   requiresAuth: true,
    // );
  }

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
    // return SHttpClient.post(
    //   '/rides/$rideId/verification-codes',
    //   service: SApiService.ride,
    //   requiresAuth: true,
    //   body: {
    //     if (stopId != null) 'stop_id': stopId,
    //     'expires_in_minutes': expiresInMinutes,
    //     'max_attempts': maxAttempts,
    //     'length': length,
    //   },
    // );
  }

  Future<Map<String, dynamic>> verifyCode({
    required String rideId,
    required String code,
    String? userId,
    String? driverId,
  }) {
    return Future.value(
      SLocationDemoData.verificationCode(rideId: rideId, isVerified: true),
    );
    // return SHttpClient.post(
    //   '/rides/$rideId/verification-codes/verify',
    //   service: SApiService.ride,
    //   requiresAuth: true,
    //   body: {
    //     'code': code,
    //     if (userId != null) 'user_id': userId,
    //     if (driverId != null) 'driver_id': driverId,
    //   },
    // );
  }

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
    // return SHttpClient.post(
    //   '/rides/$rideId/proofs/upload-url',
    //   service: SApiService.ride,
    //   requiresAuth: true,
    //   body: {
    //     'proof_type': proofType,
    //     if (fileName != null) 'file_name': fileName,
    //     'mime_type': mimeType,
    //     if (stopId != null) 'stop_id': stopId,
    //   },
    // );
  }

  Future<void> uploadProofBytes({
    required String presignedUrl,
    required List<int> bytes,
    String contentType = 'image/jpeg',
  }) {
    return Future.value();
    // return SHttpClient.putBytesToAbsoluteUrl(
    //   presignedUrl,
    //   bytes: bytes,
    //   contentType: contentType,
    // );
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
    // return SHttpClient.post(
    //   '/rides/$rideId/proofs',
    //   service: SApiService.ride,
    //   requiresAuth: true,
    //   body: {
    //     'proof_type': proofType,
    //     'file_key': fileKey,
    //     if (fileName != null) 'file_name': fileName,
    //     if (mimeType != null) 'mime_type': mimeType,
    //     if (fileSizeBytes != null) 'file_size_bytes': fileSizeBytes,
    //     if (checksumSha256 != null) 'checksum_sha256': checksumSha256,
    //     'is_primary': isPrimary,
    //     if (stopId != null) 'stop_id': stopId,
    //   },
    // );
  }

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
    // return SHttpClient.get(
    //   '/rides/$rideId/proofs/$proofId/url',
    //   service: SApiService.ride,
    //   requiresAuth: true,
    // );
  }

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
    // final query = Uri(
    //   queryParameters: {
    //     'lat': latitude.toString(),
    //     'lng': longitude.toString(),
    //     'radius': radiusKm.toString(),
    //     if (rideId != null) 'ride_id': rideId,
    //   },
    // ).query;
    //
    // return SHttpClient.get(
    //   '/drivers/nearby?$query',
    //   service: SApiService.ride,
    //   requiresAuth: true,
    // );
  }
}

Map<String, dynamic> _detailPayload({
  required SRideVehicleOffer offer,
  required SAddressResult pickup,
  required SAddressResult dropoff,
  required double passengerOffer,
}) {
  return switch (offer.serviceType.value) {
    'INTERCITY' => {
        'service_type': 'INTERCITY',
        'passenger_count': offer.passengerCapacity,
        'luggage_count': 1,
        'vehicle_type_requested': offer.vehicleType,
        'pickup_city': pickup.city,
        'dropoff_city': dropoff.city,
        'estimated_price': passengerOffer,
      },
    'FREIGHT' => {
        'service_type': 'FREIGHT',
        'cargo_weight': 20,
        'cargo_type': 'General cargo',
        'vehicle_type': offer.vehicleType,
        'requires_loader': false,
        'is_fragile': false,
        'declared_value': null,
      },
    'COURIER' => {
        'service_type': 'COURIER',
        'item_description': 'Package',
        'item_weight': 1,
        'total_parcels': 1,
        'recipient_name': 'Recipient',
        'recipient_phone': '03000000000',
        'requires_signature': false,
        'is_fragile': false,
        'declared_value': null,
      },
    'GROCERY' => {
        'service_type': 'GROCERY',
        'store_id': '',
        'total_items': 1,
        'contactless_delivery': false,
        'estimated_price': passengerOffer,
      },
    _ => {
        'service_type': 'CITY_RIDE',
        'passenger_count': offer.passengerCapacity,
        'is_ac': offer.requiresAc,
        'preferred_vehicle_type': offer.vehicleType,
        'is_shared_ride': offer.isShared,
        'requires_otp_start': true,
        'requires_otp_end': true,
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
