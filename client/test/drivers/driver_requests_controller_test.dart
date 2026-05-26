import 'package:client/features/drivers/controllers/driver_requests_controller.dart';
import 'package:client/features/drivers/data/driver_location_socket_repository.dart';
import 'package:client/features/drivers/data/driver_requests_repository.dart';
import 'package:client/features/drivers/domain/driver_request_models.dart';
import 'package:client/features/location/data/ride_repository.dart';
import 'package:client/features/location/data/ride_socket_event.dart';
import 'package:client/features/location/domain/location_models.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  test('new ride socket event refreshes requests before opening sheet',
      () async {
    final request = _request(id: 'ride-1');
    final repository = _FakeRequestsRepository([request]);
    final controller = SDriverRequestsController(
      requestsRepository: repository,
    );
    controller.currentLocation.value = _FakeRequestsRepository.coordinate;

    await controller.handleRideSocketEvent(
      const SRideSocketEvent(
        type: SRideSocketEventType.newJob,
        rideId: 'ride-1',
      ),
    );

    expect(repository.fetchRequestsCalls, 1);
    expect(controller.incomingRequest.value?.id, 'ride-1');
  });

  test('driver bid eta is never sent as zero minutes', () {
    final request = _request(
      id: 'ride-1',
      driverToPickup: const SRoutePreview(
        distanceKm: 0.01,
        durationMinutes: 0.4,
        polyline: '',
        steps: [],
      ),
    );

    expect(driverBidEtaMinutes(request), 1);
  });

  test('online location heartbeat refreshes redis-backed driver location',
      () async {
    final repository = _FakeRequestsRepository(const []);
    final locationSocket = _FakeLocationSocketRepository();
    final controller = SDriverRequestsController(
      requestsRepository: repository,
      locationSocketRepository: locationSocket,
    );
    controller.driverId.value = 'driver-1';
    controller.isOnline.value = true;
    controller.currentLocation.value = _FakeRequestsRepository.coordinate;
    controller.activeRide.value = _activeRide(
      id: 'ride-1',
      status: 'IN_PROGRESS',
    );

    await controller.sendOnlineLocationHeartbeat();

    expect(repository.updateDriverLocationCalls, 1);
    expect(repository.updateDriverLocationRideId, 'ride-1');
    expect(locationSocket.sendLocationCalls, 1);
    expect(locationSocket.lastRideId, 'ride-1');
  });

  test('start trip submits passenger verification code when provided',
      () async {
    final rideRepository = _FakeRideRepository();
    final controller = SDriverRequestsController(
      requestsRepository: _FakeRequestsRepository(const []),
      rideRepository: rideRepository,
    );
    controller.activeRide.value = _activeRide(
      id: 'ride-otp',
      status: 'ARRIVING',
      requiresOtpStart: true,
    );

    await controller.startTrip(verificationCode: '123456');

    expect(rideRepository.startedRideId, 'ride-otp');
    expect(rideRepository.startVerificationCode, '123456');
    expect(controller.activeRide.value?.status, 'IN_PROGRESS');
  });

  test('complete trip is gated until driver is within 15m of dropoff',
      () async {
    final rideRepository = _FakeRideRepository();
    final controller = SDriverRequestsController(
      requestsRepository: _FakeRequestsRepository(const []),
      rideRepository: rideRepository,
    );
    controller.activeRide.value = _activeRide(
      id: 'ride-complete',
      status: 'IN_PROGRESS',
    );

    controller.currentLocation.value =
        const SCoordinate(latitude: 31.5104, longitude: 74.3587);
    expect(controller.canCompleteTrip, isFalse);

    await controller.completeTrip();
    expect(rideRepository.completedRideId, isNull);

    controller.currentLocation.value =
        const SCoordinate(latitude: 31.52051, longitude: 74.3587);
    expect(controller.canCompleteTrip, isTrue);

    await controller.completeTrip(verificationCode: '654321');

    expect(rideRepository.completedRideId, 'ride-complete');
    expect(rideRepository.completeVerificationCode, '654321');
    expect(rideRepository.completeDriverLocation?.latitude, 31.52051);
    expect(controller.activeRide.value, isNull);
  });
}

class _FakeRequestsRepository extends SDriverRequestsRepository {
  _FakeRequestsRepository(this.values);

  final List<SDriverRideRequest> values;
  static const coordinate = SCoordinate(latitude: 31.5204, longitude: 74.3587);
  int get fetchRequestsCalls => _fetchRequestsCalls;
  int get updateDriverLocationCalls => _updateDriverLocationCalls;
  String? updateDriverLocationRideId;
  int _fetchRequestsCalls = 0;
  int _updateDriverLocationCalls = 0;

  @override
  Future<List<SDriverRideRequest>> fetchRequests({
    required SCoordinate coordinate,
    double radiusKm = 10,
    int limit = 20,
  }) async {
    _fetchRequestsCalls += 1;
    return values;
  }

  @override
  Future<void> updateDriverLocation({
    required String driverId,
    required SCoordinate coordinate,
    double accuracy = 25,
    String? rideId,
  }) async {
    _updateDriverLocationCalls += 1;
    updateDriverLocationRideId = rideId;
  }
}

class _FakeLocationSocketRepository extends SDriverLocationSocketRepository {
  int sendLocationCalls = 0;
  String? lastRideId;

  @override
  void sendLocation({
    required SCoordinate coordinate,
    required double accuracy,
    double? speed,
    double? heading,
    String? rideId,
  }) {
    sendLocationCalls += 1;
    lastRideId = rideId;
  }
}

class _FakeRideRepository extends SRideRepository {
  String? startedRideId;
  String? startVerificationCode;
  String? completedRideId;
  String? completeVerificationCode;
  SCoordinate? completeDriverLocation;

  @override
  Future<Map<String, dynamic>> startRide({
    required String rideId,
    String? verificationCode,
  }) async {
    startedRideId = rideId;
    startVerificationCode = verificationCode;
    return {
      ..._activeRideJson(
        id: rideId,
        status: 'IN_PROGRESS',
        requiresOtpStart: true,
      ),
    };
  }

  @override
  Future<Map<String, dynamic>> completeRide({
    required String rideId,
    String? verificationCode,
    double? finalPrice,
    SCoordinate? driverLocation,
    double? accuracyMeters,
  }) async {
    completedRideId = rideId;
    completeVerificationCode = verificationCode;
    completeDriverLocation = driverLocation;
    return {
      ..._activeRideJson(
        id: rideId,
        status: 'COMPLETED',
      ),
    };
  }
}

SDriverRideRequest _request({
  required String id,
  SRoutePreview? driverToPickup,
}) {
  return SDriverRideRequest(
    id: id,
    passengerId: 'passenger-1',
    serviceType: 'CITY_RIDE',
    category: 'Mini',
    pricingMode: 'HYBRID',
    status: 'MATCHING',
    paymentMethod: 'CASH',
    collectionMode: 'DRIVER_COLLECTED',
    createdAt: DateTime.utc(2026, 5, 24),
    baselineMinPrice: 250,
    baselineMaxPrice: 300,
    driverToPickup: driverToPickup,
  );
}

SDriverActiveRide _activeRide({
  required String id,
  required String status,
  bool requiresOtpStart = false,
  bool requiresOtpEnd = false,
}) {
  return SDriverActiveRide.fromJson(
    _activeRideJson(
      id: id,
      status: status,
      requiresOtpStart: requiresOtpStart,
      requiresOtpEnd: requiresOtpEnd,
    ),
  );
}

Map<String, dynamic> _activeRideJson({
  required String id,
  required String status,
  bool requiresOtpStart = false,
  bool requiresOtpEnd = false,
}) {
  return {
    'id': id,
    'passenger_id': 'passenger-1',
    'service_type': 'CITY_RIDE',
    'category': 'Mini',
    'pricing_mode': 'HYBRID',
    'status': status,
    'passenger_payment_method': 'CASH',
    'payment_collection_mode': 'DRIVER_COLLECTED',
    'created_at': DateTime.utc(2026, 5, 24).toIso8601String(),
    'baseline_min_price': 250,
    'baseline_max_price': 300,
    'requires_otp_start': requiresOtpStart,
    'requires_otp_end': requiresOtpEnd,
    'pickup_stop': {
      'id': 'pickup-$id',
      'stop_type': 'PICKUP',
      'latitude': 31.5104,
      'longitude': 74.3587,
      'place_name': 'Pickup',
    },
    'dropoff_stop': {
      'id': 'dropoff-$id',
      'stop_type': 'DROPOFF',
      'latitude': 31.52051,
      'longitude': 74.3587,
      'place_name': 'Dropoff',
    },
  };
}
