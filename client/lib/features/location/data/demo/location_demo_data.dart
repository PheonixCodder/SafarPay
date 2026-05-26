import '../../domain/location_models.dart';

class SLocationDemoData {
  const SLocationDemoData._();

  static const pickup = SAddressResult(
    formatted: 'Street 8, Askari X, Lahore',
    coordinate: SCoordinate(latitude: 31.4821, longitude: 74.4096),
    street: 'Street 8',
    city: 'Lahore',
    country: 'Pakistan',
    postalCode: '54000',
  );

  static const dropoff = SAddressResult(
    formatted: 'Sector E, Block E Askari X, Lahore',
    coordinate: SCoordinate(latitude: 31.4886, longitude: 74.4018),
    street: 'Sector E',
    city: 'Lahore',
    country: 'Pakistan',
    postalCode: '54000',
  );

  static const searchResults = <SAddressResult>[
    SAddressResult(
      formatted: 'The Coon Luxury Suites, Lekki',
      coordinate: SCoordinate(latitude: 31.4901, longitude: 74.3988),
      street: 'The Coon Luxury Suites',
      city: 'Lahore',
      country: 'Pakistan',
      postalCode: '54000',
    ),
    SAddressResult(
      formatted: 'Niazi Adda Bus Stop Lahore, Band Road',
      coordinate: SCoordinate(latitude: 31.5517, longitude: 74.2633),
      street: 'Band Road',
      city: 'Lahore',
      country: 'Pakistan',
      postalCode: '54000',
    ),
    SAddressResult(
      formatted: 'European School of Excellence, Township',
      coordinate: SCoordinate(latitude: 31.4547, longitude: 74.3081),
      street: 'Township',
      city: 'Lahore',
      country: 'Pakistan',
      postalCode: '54770',
    ),
    SAddressResult(
      formatted: 'Ayesha Hospital, Lahore',
      coordinate: SCoordinate(latitude: 31.4697, longitude: 74.4111),
      street: 'Ayesha Hospital',
      city: 'Lahore',
      country: 'Pakistan',
      postalCode: '54000',
    ),
  ];

  static SAddressResult geocode(String query) {
    final normalized = query.trim().toLowerCase();
    if (normalized.isEmpty) return dropoff;
    return searchResults.firstWhere(
      (item) => item.formatted.toLowerCase().contains(normalized),
      orElse: () => searchResults.first,
    );
  }

  static SAddressResult reverseGeocode(SCoordinate coordinate) {
    return SAddressResult(
      formatted: 'Demo pin near Street 8, Askari X, Lahore',
      coordinate: coordinate,
      street: 'Street 8',
      city: 'Lahore',
      country: 'Pakistan',
      postalCode: '54000',
    );
  }

  static const routePreview = SRoutePreview(
    distanceKm: 4.2,
    durationMinutes: 11,
    polyline: 'czc_E_cdeM{EbLgJjMgJrIgJrI',
    steps: [
      SRouteStep(
        instruction: 'Head east on Street 8',
        distanceMeters: 900,
        durationSeconds: 150,
        polyline: 'czc_E_cdeM{EbL',
      ),
      SRouteStep(
        instruction: 'Continue toward Sector E',
        distanceMeters: 2100,
        durationSeconds: 380,
        polyline: '_ad_E{uceMgJjMgJrI',
      ),
      SRouteStep(
        instruction: 'Arrive at the selected dropoff',
        distanceMeters: 1200,
        durationSeconds: 130,
        polyline: 'owd_E{|beMgJrI',
      ),
    ],
  );

  static Map<String, dynamic> createdRide(Map<String, dynamic> request) {
    return {
      'id': 'demo-ride-001',
      'status': 'MATCHING',
      'pricing_mode': 'HYBRID',
      'service_type': request['service_type'],
      'category': request['category'],
      'baseline_min_price': request['baseline_min_price'],
      'baseline_max_price': request['baseline_max_price'],
      'auto_accept_driver': request['auto_accept_driver'],
    };
  }

  static Map<String, dynamic> rideDetails(String rideId) {
    return {
      'id': rideId,
      'status': 'MATCHING',
      'pricing_mode': 'HYBRID',
      'service_type': 'CITY_RIDE',
      'category': 'MINI',
      'baseline_min_price': 213,
      'baseline_max_price': 250,
      'final_price': null,
    };
  }

  static Map<String, dynamic> canceledRide(String rideId, String reason) {
    return {
      'id': rideId,
      'status': 'CANCELLED',
      'cancellation_reason': reason,
    };
  }

  static List<Map<String, dynamic>> passengerRideSummaries() {
    return [
      {
        'id': 'demo-ride-001',
        'passenger_id': 'demo-passenger-001',
        'assigned_driver_id': null,
        'service_type': 'CITY_RIDE',
        'category': 'MINI',
        'status': 'MATCHING',
        'passenger_payment_method': 'CASH',
        'payment_collection_mode': 'DRIVER_COLLECTED',
        'created_at': DateTime.now().toIso8601String(),
        'scheduled_at': null,
        'pickup_stop': demoStop(
          id: 'demo-stop-pickup',
          rideId: 'demo-ride-001',
          type: 'PICKUP',
          address: pickup,
          sequenceOrder: 1,
        ),
        'dropoff_stop': demoStop(
          id: 'demo-stop-dropoff',
          rideId: 'demo-ride-001',
          type: 'DROPOFF',
          address: dropoff,
          sequenceOrder: 2,
        ),
      },
    ];
  }

  static Map<String, dynamic> rideAccepted(String rideId) {
    return {
      ...rideDetails(rideId),
      'status': 'ACCEPTED',
      'assigned_driver_id': 'demo-driver-001',
      'accepted_at': DateTime.now().toIso8601String(),
    };
  }

  static Map<String, dynamic> rideStarted({
    required String rideId,
    String? verificationCode,
  }) {
    return {
      ...rideAccepted(rideId),
      'status': 'IN_PROGRESS',
      'verification_code': verificationCode,
    };
  }

  static Map<String, dynamic> rideCompleted({
    required String rideId,
    String? verificationCode,
    double? finalPrice,
  }) {
    return {
      ...rideAccepted(rideId),
      'status': 'COMPLETED',
      'final_price': finalPrice ?? 250,
      'verification_code': verificationCode,
      'completed_at': DateTime.now().toIso8601String(),
    };
  }

  static Map<String, dynamic> demoStop({
    required String id,
    required String rideId,
    required String type,
    required SAddressResult address,
    required int sequenceOrder,
  }) {
    return {
      'id': id,
      'service_request_id': rideId,
      'sequence_order': sequenceOrder,
      'stop_type': type,
      'latitude': address.coordinate.latitude,
      'longitude': address.coordinate.longitude,
      'place_name': address.formatted,
      'address_line_1': address.formatted,
      'address_line_2': null,
      'city': address.city,
      'state': null,
      'country': address.country,
      'postal_code': address.postalCode,
      'contact_name': null,
      'contact_phone': null,
      'instructions': null,
      'arrived_at': null,
      'completed_at': null,
    };
  }

  static Map<String, dynamic> addedStop({
    required String rideId,
    required Map<String, dynamic> stop,
  }) {
    return {
      'id': 'demo-added-stop-001',
      'service_request_id': rideId,
      ...stop,
      'address_line_2': stop['address_line_2'],
      'state': stop['state'],
      'postal_code': stop['postal_code'],
      'arrived_at': null,
      'completed_at': null,
    };
  }

  static Map<String, dynamic> stopArrived(String stopId) {
    return {
      ...demoStop(
        id: stopId,
        rideId: 'demo-ride-001',
        type: 'PICKUP',
        address: pickup,
        sequenceOrder: 1,
      ),
      'arrived_at': DateTime.now().toIso8601String(),
    };
  }

  static Map<String, dynamic> stopCompleted(String stopId) {
    return {
      ...stopArrived(stopId),
      'completed_at': DateTime.now().toIso8601String(),
    };
  }

  static Map<String, dynamic> verificationCode({
    required String rideId,
    String? stopId,
    bool isVerified = false,
  }) {
    return {
      'id': 'demo-verification-code-001',
      'service_request_id': rideId,
      'stop_id': stopId,
      'is_verified': isVerified,
      'attempts': isVerified ? 1 : 0,
      'max_attempts': 5,
      'expires_at': DateTime.now()
          .add(const Duration(minutes: 15))
          .toIso8601String(),
      'generated_at': DateTime.now().toIso8601String(),
      'verified_at': isVerified ? DateTime.now().toIso8601String() : null,
    };
  }

  static Map<String, dynamic> proofUploadUrl({
    required String proofType,
    String mimeType = 'image/jpeg',
  }) {
    return {
      'presigned_url': 'https://demo-s3-presigned-put-url.local/proof.jpg',
      'file_key': 'demo/ride/proofs/${proofType.toLowerCase()}_proof.jpg',
      'expires_in_seconds': 900,
      'proof_type': proofType,
      'mime_type': mimeType,
    };
  }

  static Map<String, dynamic> proofImage({
    required String rideId,
    required String proofType,
    required String fileKey,
    String? fileName,
    String? mimeType,
    int? fileSizeBytes,
    String? stopId,
    bool withViewUrl = false,
  }) {
    return {
      'id': 'demo-proof-001',
      'service_request_id': rideId,
      'stop_id': stopId,
      'proof_type': proofType,
      'file_key': fileKey,
      'file_name': fileName,
      'mime_type': mimeType,
      'file_size_bytes': fileSizeBytes,
      'is_primary': true,
      'uploaded_by_user_id': 'demo-passenger-001',
      'uploaded_by_driver_id': null,
      'uploaded_at': DateTime.now().toIso8601String(),
      if (withViewUrl) 'view_url': 'https://demo-s3-view-url.local/proof.jpg',
    };
  }

  static Map<String, dynamic> nearbyDrivers({
    required double latitude,
    required double longitude,
    String? rideId,
  }) {
    return {
      'ride_id': rideId,
      'count': 2,
      'candidates': [
        {
          'driver_id': 'demo-driver-001',
          'distance_km': 1.2,
          'vehicle_type': 'CAR',
          'rating': 4.8,
          'priority_score': 0.96,
          'estimated_arrival_minutes': 4,
        },
        {
          'driver_id': 'demo-driver-002',
          'distance_km': 2.4,
          'vehicle_type': 'MOTORCYCLE',
          'rating': 4.6,
          'priority_score': 0.88,
          'estimated_arrival_minutes': 6,
        },
      ],
    };
  }

  static Map<String, dynamic> hybridSession(String rideId) {
    return {
      'session_id': 'demo-hybrid-session-001',
      'service_request_id': rideId,
      'status': 'OPEN',
      'pricing_mode': 'HYBRID',
      'passenger_user_id': 'demo-passenger-001',
      'baseline_price': 250,
      'bids': const [],
      'lowest_bid': null,
      'counter_offers': const [],
    };
  }

  static Map<String, dynamic> acceptedBid(String sessionId, String bidId) {
    return {
      'id': bidId,
      'bidding_session_id': sessionId,
      'driver_id': 'demo-driver-001',
      'driver_vehicle_id': null,
      'bid_amount': 250,
      'currency': 'PKR',
      'eta_minutes': 4,
      'message': 'Demo driver offer',
      'status': 'ACCEPTED',
      'placed_at': DateTime.now().toIso8601String(),
    };
  }

  static Map<String, dynamic> placedBid({
    required String sessionId,
    required double bidAmount,
    String? driverVehicleId,
    int? etaMinutes,
    String? message,
  }) {
    return {
      'id': 'demo-driver-bid-001',
      'bidding_session_id': sessionId,
      'driver_id': 'demo-driver-001',
      'driver_vehicle_id': driverVehicleId,
      'bid_amount': bidAmount,
      'currency': 'PKR',
      'eta_minutes': etaMinutes ?? 4,
      'message': message ?? 'Demo driver can arrive soon',
      'status': 'PLACED',
      'placed_at': DateTime.now().toIso8601String(),
    };
  }

  static Map<String, dynamic> withdrawnBid({
    required String sessionId,
    required String bidId,
  }) {
    return {
      ...acceptedBid(sessionId, bidId),
      'status': 'WITHDRAWN',
    };
  }

  static Map<String, dynamic> acceptedCounter({
    required String sessionId,
    required String counterOfferId,
  }) {
    return {
      'id': 'demo-accepted-counter-bid-001',
      'bidding_session_id': sessionId,
      'driver_id': 'demo-driver-001',
      'driver_vehicle_id': null,
      'bid_amount': 250,
      'currency': 'PKR',
      'eta_minutes': 4,
      'message': 'Accepted passenger counter $counterOfferId',
      'status': 'ACCEPTED',
      'placed_at': DateTime.now().toIso8601String(),
    };
  }

  static List<Map<String, dynamic>> demoRideSocketEvents(String rideId) {
    return [
      {
        'event': 'RIDE_UPDATED',
        'data': {
          'ride_id': rideId,
          'status': 'ACCEPTED',
        },
      },
      {
        'event': 'RIDE_UPDATED',
        'data': {
          'ride_id': rideId,
          'status': 'ARRIVING',
        },
      },
      {
        'event': 'DRIVER_LOCATION',
        'data': {
          'ride_id': rideId,
          'driver_id': 'demo-driver-001',
          'latitude': 31.4871,
          'longitude': 74.4052,
        },
      },
    ];
  }

  static List<Map<String, dynamic>> demoBiddingSocketEvents(String sessionId) {
    return [
      {
        'event': 'BID_PLACED',
        'data': {
          'session_id': sessionId,
          'bid': placedBid(
            sessionId: sessionId,
            bidAmount: 245,
            etaMinutes: 4,
            message: 'Demo live offer',
          ),
        },
      },
      {
        'event': 'PASSENGER_COUNTER_OFFER_CREATED',
        'data': {
          'session_id': sessionId,
          'counter_offer': counterOffer(
            sessionId: sessionId,
            counterPrice: 250,
            counterEtaMinutes: 4,
          ),
        },
      },
    ];
  }

  static Map<String, dynamic> counterOffer({
    required String sessionId,
    required double counterPrice,
    int? counterEtaMinutes,
  }) {
    return {
      'id': 'demo-counter-offer-001',
      'session_id': sessionId,
      'price': counterPrice,
      'eta_minutes': counterEtaMinutes,
      'user_id': 'demo-passenger-001',
      'driver_id': null,
      'bid_id': null,
      'status': 'PENDING',
      'responded_at': null,
      'reason': null,
      'created_at': DateTime.now().toIso8601String(),
    };
  }

  static List<Map<String, dynamic>> counterOffers(String sessionId) {
    return [
      counterOffer(
        sessionId: sessionId,
        counterPrice: 250,
        counterEtaMinutes: 4,
      ),
    ];
  }

  static Map<String, dynamic> pickupValidation(SCoordinate coordinate) {
    return {
      'valid': true,
      'coordinate': coordinate.toJson(),
      'message': 'Demo pickup is inside the service area.',
    };
  }

  static Map<String, dynamic> surge(SCoordinate coordinate) {
    return {
      'coordinate': coordinate.toJson(),
      'surge_multiplier': 1.0,
      'zone': 'demo-lahore-central',
    };
  }

  static SLiveRideLocations liveRideLocations(String rideId) {
    return SLiveRideLocations(
      rideId: rideId,
      driver: SDriverLiveLocation(
        driverId: 'demo-driver-001',
        coordinate: const SCoordinate(latitude: 31.4871, longitude: 74.4052),
        heading: 90,
        speed: 22,
        updatedAt: DateTime.now(),
      ),
      passenger: SPassengerLiveLocation(
        userId: 'demo-passenger-001',
        coordinate: pickup.coordinate,
        updatedAt: DateTime.now(),
      ),
    );
  }
}
