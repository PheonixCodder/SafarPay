import 'demo/location_demo_data.dart';
import '../../../data/rides/ride_models.dart';
import '../domain/location_models.dart';
import '../domain/ride_booking_models.dart';
import '../../../utils/constants/api_constants.dart';
import '../../../utils/http/client.dart';

class SRideRepository {
  const SRideRepository({bool? useDemoData})
      : _useDemoData = useDemoData ?? SApiConstants.useLocationDemoData;

  final bool _useDemoData;

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
    if (_useDemoData) return Future.value(SLocationDemoData.createdRide(body));
    return SHttpClient.post(
      '/rides',
      service: SApiService.ride,
      requiresAuth: true,
      body: body,
    );
  }

  Future<Map<String, dynamic>> fetchRide(String rideId) {
    if (_useDemoData) {
      return Future.value(SLocationDemoData.rideDetails(rideId));
    }
    return SHttpClient.get(
      '/rides/$rideId',
      service: SApiService.ride,
      requiresAuth: true,
    );
  }

  Future<Map<String, dynamic>> cancelRide({
    required String rideId,
    required String reason,
  }) {
    if (_useDemoData) {
      return Future.value(SLocationDemoData.canceledRide(rideId, reason));
    }
    return SHttpClient.post(
      '/rides/$rideId/cancel',
      service: SApiService.ride,
      requiresAuth: true,
      body: {'reason': reason},
    );
  }

  Future<List<RideSummaryResponse>> listPassengerRides({
    List<String> statuses = const [],
    int limit = 20,
    int offset = 0,
  }) async {
    if (_useDemoData) {
      return SLocationDemoData.passengerRideSummaries()
          .map((item) => RideSummaryResponse.fromJson(item))
          .toList(growable: false);
    }
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

  Future<Map<String, dynamic>> acceptFixedRide(String rideId) {
    if (_useDemoData) {
      return Future.value(SLocationDemoData.rideAccepted(rideId));
    }
    return SHttpClient.post(
      '/rides/$rideId/accept',
      service: SApiService.ride,
      requiresAuth: true,
    );
  }

  Future<Map<String, dynamic>> startRide({
    required String rideId,
    String? verificationCode,
  }) {
    if (_useDemoData) {
      return Future.value(
        SLocationDemoData.rideStarted(
          rideId: rideId,
          verificationCode: verificationCode,
        ),
      );
    }
    return SHttpClient.post(
      '/rides/$rideId/start',
      service: SApiService.ride,
      requiresAuth: true,
      body: {
        if (verificationCode != null) 'verification_code': verificationCode,
      },
    );
  }

  Future<Map<String, dynamic>> completeRide({
    required String rideId,
    String? verificationCode,
    double? finalPrice,
    SCoordinate? driverLocation,
    double? accuracyMeters,
  }) {
    if (_useDemoData) {
      return Future.value(
        SLocationDemoData.rideCompleted(
          rideId: rideId,
          verificationCode: verificationCode,
          finalPrice: finalPrice,
        ),
      );
    }
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

  Future<Map<String, dynamic>> addStop({
    required String rideId,
    required Map<String, dynamic> stop,
  }) {
    if (_useDemoData) {
      return Future.value(
        SLocationDemoData.addedStop(rideId: rideId, stop: stop),
      );
    }
    return SHttpClient.post(
      '/rides/$rideId/stops',
      service: SApiService.ride,
      requiresAuth: true,
      body: stop,
    );
  }

  Future<Map<String, dynamic>> markStopArrived(String stopId) {
    if (_useDemoData) {
      return Future.value(SLocationDemoData.stopArrived(stopId));
    }
    return SHttpClient.post(
      '/stops/$stopId/arrived',
      service: SApiService.ride,
      requiresAuth: true,
    );
  }

  Future<Map<String, dynamic>> markStopCompleted(String stopId) {
    if (_useDemoData) {
      return Future.value(SLocationDemoData.stopCompleted(stopId));
    }
    return SHttpClient.post(
      '/stops/$stopId/completed',
      service: SApiService.ride,
      requiresAuth: true,
    );
  }

  Future<Map<String, dynamic>> generateVerificationCode({
    required String rideId,
    String? stopId,
    int expiresInMinutes = 15,
    int maxAttempts = 5,
    int length = 6,
  }) {
    if (_useDemoData) {
      return Future.value(
        SLocationDemoData.verificationCode(rideId: rideId, stopId: stopId),
      );
    }
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

  Future<Map<String, dynamic>> verifyCode({
    required String rideId,
    required String code,
    String? userId,
    String? driverId,
  }) {
    if (_useDemoData) {
      return Future.value(
        SLocationDemoData.verificationCode(rideId: rideId, isVerified: true),
      );
    }
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

  Future<Map<String, dynamic>> requestProofUploadUrl({
    required String rideId,
    required String proofType,
    String? fileName,
    String mimeType = 'image/jpeg',
    String? stopId,
  }) {
    if (_useDemoData) {
      return Future.value(
        SLocationDemoData.proofUploadUrl(
          proofType: proofType,
          mimeType: mimeType,
        ),
      );
    }
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

  Future<void> uploadProofBytes({
    required String presignedUrl,
    required List<int> bytes,
    String contentType = 'image/jpeg',
  }) {
    if (_useDemoData) return Future.value();
    return SHttpClient.putBytesToAbsoluteUrl(
      presignedUrl,
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
    if (_useDemoData) {
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

  Future<Map<String, dynamic>> getProofUrl({
    required String rideId,
    required String proofId,
  }) {
    if (_useDemoData) {
      return Future.value(
        SLocationDemoData.proofImage(
          rideId: rideId,
          proofType: 'PICKUP',
          fileKey: 'demo/ride/proofs/pickup_proof.jpg',
          withViewUrl: true,
        ),
      );
    }
    return SHttpClient.get(
      '/rides/$rideId/proofs/$proofId/url',
      service: SApiService.ride,
      requiresAuth: true,
    );
  }

  Future<Map<String, dynamic>> nearbyDrivers({
    required double latitude,
    required double longitude,
    double radiusKm = 5,
    String? rideId,
  }) {
    if (_useDemoData) {
      return Future.value(
        SLocationDemoData.nearbyDrivers(
          latitude: latitude,
          longitude: longitude,
          rideId: rideId,
        ),
      );
    }
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
