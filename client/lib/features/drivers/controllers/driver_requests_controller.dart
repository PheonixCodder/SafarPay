import 'dart:async';
import 'dart:math';

import 'package:geolocator/geolocator.dart';
import 'package:get/get.dart';

import '../../../common/widgets/maps/map_models.dart';
import '../../../utils/helpers/helpers.dart';
import '../../../utils/http/client.dart';
import '../../../utils/logging/logger.dart';
import '../../location/data/bidding_repository.dart';
import '../../location/data/bidding_socket_event.dart';
import '../../location/data/bidding_socket_repository.dart';
import '../../location/data/device_location_service.dart';
import '../../location/data/ride_repository.dart';
import '../../location/data/ride_socket_event.dart';
import '../../location/data/ride_socket_repository.dart';
import '../../location/domain/location_models.dart';
import '../data/driver_location_socket_repository.dart';
import '../data/driver_requests_repository.dart';
import '../domain/driver_request_models.dart';

class SDriverRequestsController extends GetxController {
  SDriverRequestsController({
    SDriverRequestsRepository requestsRepository =
        const SDriverRequestsRepository(),
    SDeviceLocationService deviceLocationService =
        const SDeviceLocationService(),
    SRideRepository rideRepository = const SRideRepository(),
    SBiddingRepository biddingRepository = const SBiddingRepository(),
    SRideSocketRepository? rideSocketRepository,
    SBiddingSocketRepository? biddingSocketRepository,
    SDriverLocationSocketRepository? locationSocketRepository,
  })  : _requestsRepository = requestsRepository,
        _deviceLocationService = deviceLocationService,
        _rideRepository = rideRepository,
        _biddingRepository = biddingRepository,
        _rideSocketRepository = rideSocketRepository ?? SRideSocketRepository(),
        _biddingSocketRepository =
            biddingSocketRepository ?? SBiddingSocketRepository(),
        _locationSocketRepository =
            locationSocketRepository ?? SDriverLocationSocketRepository();

  static const SCoordinate fallbackCenter = SCoordinate(
    latitude: 31.5204,
    longitude: 74.3587,
  );

  final SDriverRequestsRepository _requestsRepository;
  final SDeviceLocationService _deviceLocationService;
  final SRideRepository _rideRepository;
  final SBiddingRepository _biddingRepository;
  final SRideSocketRepository _rideSocketRepository;
  final SBiddingSocketRepository _biddingSocketRepository;
  final SDriverLocationSocketRepository _locationSocketRepository;

  final SMapController mapController = SMapController();
  final RxBool isOnline = false.obs;
  final RxBool isLoading = false.obs;
  final RxBool isSubmitting = false.obs;
  final RxString errorMessage = ''.obs;
  final RxString driverId = ''.obs;
  final Rxn<SCoordinate> currentLocation = Rxn<SCoordinate>();
  final RxList<SDriverRideRequest> requests = <SDriverRideRequest>[].obs;
  final Rxn<SDriverRideRequest> incomingRequest = Rxn<SDriverRideRequest>();
  final Rxn<SDriverActiveRide> activeRide = Rxn<SDriverActiveRide>();
  final RxDouble offerAmount = 0.0.obs;

  StreamSubscription<SRideSocketEvent>? _rideSocketSub;
  StreamSubscription<SBiddingSocketEvent>? _biddingSocketSub;
  StreamSubscription<Position>? _positionSub;
  Timer? _refreshTimer;
  Timer? _rideReconnectTimer;
  Timer? _locationHeartbeatTimer;

  SCoordinate get mapCenter {
    return currentLocation.value ??
        activeRide.value?.pickup?.coordinate ??
        fallbackCenter;
  }

  bool get canArriveAtPickup {
    final ride = activeRide.value;
    final current = currentLocation.value;
    final pickup = ride?.pickup;
    if (ride == null || current == null || pickup == null) return false;
    if (ride.hasArrivedAtPickup || ride.isInProgress) return false;
    return _distanceMeters(current, pickup.coordinate) <= 20;
  }

  double? get metersToDropoff {
    final ride = activeRide.value;
    final current = currentLocation.value;
    final dropoff = ride?.dropoff;
    if (ride == null || current == null || dropoff == null) return null;
    return _distanceMeters(current, dropoff.coordinate);
  }

  bool get canCompleteTrip {
    final ride = activeRide.value;
    final distance = metersToDropoff;
    if (ride == null || !ride.isInProgress || distance == null) return false;
    return distance <= 15;
  }

  @override
  void onInit() {
    super.onInit();
    _bootstrap();
  }

  @override
  void onClose() {
    _refreshTimer?.cancel();
    _rideReconnectTimer?.cancel();
    _locationHeartbeatTimer?.cancel();
    _rideSocketSub?.cancel();
    _biddingSocketSub?.cancel();
    _positionSub?.cancel();
    _rideSocketRepository.close();
    _biddingSocketRepository.close();
    _locationSocketRepository.close();
    super.onClose();
  }

  Future<void> _bootstrap() async {
    try {
      final id = await _requestsRepository.fetchCurrentDriverId();
      driverId.value = id ?? '';
      currentLocation.value = await _deviceLocationService.currentCoordinate();
      await refreshActiveRide();
    } catch (_) {
      errorMessage.value = 'Driver request data is unavailable.';
    }
  }

  Future<void> toggleOnline() async {
    if (isOnline.value) {
      await goOffline();
    } else {
      await goOnline();
    }
  }

  Future<void> goOnline() async {
    if (driverId.value.isEmpty) await _bootstrap();
    if (driverId.value.isEmpty) {
      errorMessage.value = 'Driver profile is not ready for requests.';
      return;
    }

    isLoading.value = true;
    errorMessage.value = '';
    try {
      await _requestsRepository.setDriverStatus(
        driverId: driverId.value,
        isOnline: true,
      );
      final coordinate = currentLocation.value;
      if (coordinate != null) {
        await _requestsRepository.updateDriverLocation(
          driverId: driverId.value,
          coordinate: coordinate,
        );
      }
      isOnline.value = true;
      await _locationSocketRepository.connect();
      _sendCurrentLocationSnapshot();
      _startLocationHeartbeat();
      _startPositionStream();
      _connectRideSocket();
      await refreshAll();
      _refreshTimer?.cancel();
      _refreshTimer = Timer.periodic(
        const Duration(seconds: 20),
        (_) => refreshAll(),
      );
    } catch (_) {
      errorMessage.value = 'Unable to go online. Try again.';
      isOnline.value = false;
    } finally {
      isLoading.value = false;
    }
  }

  Future<void> goOffline() async {
    _refreshTimer?.cancel();
    _locationHeartbeatTimer?.cancel();
    await _rideSocketSub?.cancel();
    await _biddingSocketSub?.cancel();
    await _positionSub?.cancel();
    _rideReconnectTimer?.cancel();
    isOnline.value = false;
    await _rideSocketRepository.close();
    await _biddingSocketRepository.close();
    await _locationSocketRepository.close();
    requests.clear();
    incomingRequest.value = null;
    if (driverId.value.isNotEmpty) {
      await _requestsRepository.setDriverStatus(
        driverId: driverId.value,
        isOnline: false,
      );
    }
  }

  Future<void> refreshAll() async {
    await refreshActiveRide();
    if (activeRide.value == null && isOnline.value) {
      await refreshRequests();
    }
  }

  Future<void> refreshRequests() async {
    final location = currentLocation.value;
    if (location == null) return;
    try {
      final values = await _requestsRepository.fetchRequests(
        coordinate: location,
      );
      requests.assignAll(values);
    } catch (_) {
      errorMessage.value = 'Nearby requests are unavailable.';
    }
  }

  Future<void> refreshActiveRide() async {
    try {
      activeRide.value = await _requestsRepository.fetchActiveRide(
        coordinate: currentLocation.value,
      );
      if (activeRide.value != null) {
        requests.clear();
        incomingRequest.value = null;
        _sendCurrentLocationSnapshot();
      }
    } catch (_) {}
  }

  void openRequest(SDriverRideRequest request) {
    if (activeRide.value != null) return;
    incomingRequest.value = request;
    offerAmount.value = request.displayFare;
    if (request.isHybrid) _connectBiddingSocketForRide(request.id);
  }

  void dismissIncoming() {
    incomingRequest.value = null;
  }

  void adjustOffer(double delta) {
    final next = offerAmount.value + delta;
    offerAmount.value = next < 1 ? 1 : next.roundToDouble();
  }

  Future<void> acceptFixedRide(SDriverRideRequest request) async {
    isSubmitting.value = true;
    try {
      final data = await _rideRepository.acceptFixedRide(request.id);
      activeRide.value = SDriverActiveRide.fromJson(data);
      incomingRequest.value = null;
      requests.clear();
      _sendCurrentLocationSnapshot();
    } catch (_) {
      SHelperFunctions.showSnackBar('Unable to accept this ride.');
    } finally {
      isSubmitting.value = false;
    }
  }

  Future<void> submitHybridOffer(SDriverRideRequest request) async {
    isSubmitting.value = true;
    try {
      final sessionData =
          await _biddingRepository.getSessionForRide(request.id);
      final sessionId = sessionData['session_id']?.toString() ??
          sessionData['id']?.toString() ??
          '';
      if (sessionId.isEmpty) throw StateError('Missing bidding session');
      await _biddingRepository.placeBid(
        sessionId: sessionId,
        bidAmount: offerAmount.value,
        etaMinutes: driverBidEtaMinutes(request),
        message: 'Driver offer',
      );
      incomingRequest.value = null;
      SHelperFunctions.showSnackBar('Offer submitted.');
    } on SHttpException catch (error) {
      SLoggerHelper.warning(
        'Unable to submit driver offer: ${error.statusCode} ${error.message}',
      );
      SHelperFunctions.showSnackBar('Unable to submit this offer.');
    } catch (error) {
      SLoggerHelper.warning('Unable to submit driver offer: $error');
      SHelperFunctions.showSnackBar('Unable to submit this offer.');
    } finally {
      isSubmitting.value = false;
    }
  }

  Future<void> markArrivedAtPickup() async {
    final ride = activeRide.value;
    final stopId = ride?.pickup?.id;
    if (ride == null ||
        stopId == null ||
        stopId.isEmpty ||
        !canArriveAtPickup) {
      return;
    }
    isSubmitting.value = true;
    try {
      await _rideRepository.markStopArrived(stopId);
      await refreshActiveRide();
    } catch (_) {
      SHelperFunctions.showSnackBar('Unable to mark arrival yet.');
    } finally {
      isSubmitting.value = false;
    }
  }

  Future<void> startTrip({String? verificationCode}) async {
    final ride = activeRide.value;
    if (ride == null) return;
    isSubmitting.value = true;
    try {
      final data = await _rideRepository.startRide(
        rideId: ride.id,
        verificationCode: verificationCode,
      );
      activeRide.value = SDriverActiveRide.fromJson(data);
      _sendCurrentLocationSnapshot();
    } catch (_) {
      SHelperFunctions.showSnackBar('Unable to start trip.');
    } finally {
      isSubmitting.value = false;
    }
  }

  Future<void> completeTrip({String? verificationCode}) async {
    final ride = activeRide.value;
    final coordinate = currentLocation.value;
    if (ride == null) return;
    if (!canCompleteTrip || coordinate == null) {
      const message = 'Reach the dropoff to complete this trip.';
      errorMessage.value = message;
      if (Get.context != null) SHelperFunctions.showSnackBar(message);
      return;
    }
    isSubmitting.value = true;
    try {
      await _rideRepository.completeRide(
        rideId: ride.id,
        verificationCode: verificationCode,
        driverLocation: coordinate,
        accuracyMeters: 25,
      );
      activeRide.value = null;
      await refreshRequests();
    } catch (_) {
      SHelperFunctions.showSnackBar('Unable to complete trip.');
    } finally {
      isSubmitting.value = false;
    }
  }

  void _startPositionStream() {
    _positionSub?.cancel();
    _positionSub = Geolocator.getPositionStream(
      locationSettings: const LocationSettings(
        accuracy: LocationAccuracy.high,
        distanceFilter: 10,
      ),
    ).listen((position) {
      final coordinate = SCoordinate(
        latitude: position.latitude,
        longitude: position.longitude,
      );
      currentLocation.value = coordinate;
      _locationSocketRepository.sendLocation(
        coordinate: coordinate,
        accuracy: position.accuracy,
        speed: position.speed >= 0 ? position.speed * 3.6 : null,
        heading: position.heading >= 0 ? position.heading : null,
        rideId: activeRide.value?.id,
      );
    });
  }

  void _sendCurrentLocationSnapshot() {
    final coordinate = currentLocation.value;
    if (coordinate == null) return;
    _locationSocketRepository.sendLocation(
      coordinate: coordinate,
      accuracy: 25,
      rideId: activeRide.value?.id,
    );
  }

  void _startLocationHeartbeat() {
    _locationHeartbeatTimer?.cancel();
    _locationHeartbeatTimer = Timer.periodic(
      const Duration(seconds: 30),
      (_) => unawaited(sendOnlineLocationHeartbeat()),
    );
  }

  Future<void> sendOnlineLocationHeartbeat() async {
    if (!isOnline.value || driverId.value.isEmpty) return;
    final coordinate = currentLocation.value;
    if (coordinate == null) return;
    try {
      await _requestsRepository.updateDriverLocation(
        driverId: driverId.value,
        coordinate: coordinate,
        rideId: activeRide.value?.id,
      );
      _locationSocketRepository.sendLocation(
        coordinate: coordinate,
        accuracy: 25,
        rideId: activeRide.value?.id,
      );
    } catch (error) {
      SLoggerHelper.warning(
          'Unable to refresh driver location heartbeat: $error');
    }
  }

  void _connectRideSocket() {
    _rideReconnectTimer?.cancel();
    _rideSocketSub?.cancel();
    _rideSocketSub = _rideSocketRepository.connectDriver().listen(
      (event) => unawaited(handleRideSocketEvent(event)),
      onError: (Object error) {
        SLoggerHelper.warning('Driver ride socket error: $error');
        _scheduleRideSocketReconnect();
      },
      onDone: _scheduleRideSocketReconnect,
    );
  }

  Future<void> handleRideSocketEvent(SRideSocketEvent event) async {
    if (event.type == SRideSocketEventType.newJob && activeRide.value == null) {
      await refreshRequests();
      final rideId = event.rideId;
      if (rideId != null) {
        final matches = requests.where((item) => item.id == rideId);
        final match = matches.isEmpty ? null : matches.first;
        if (match != null) openRequest(match);
      }
    }
    if (event.type == SRideSocketEventType.jobAssigned) {
      await refreshActiveRide();
    }
    if (event.type == SRideSocketEventType.jobCancelled) {
      await refreshAll();
    }
  }

  void _scheduleRideSocketReconnect() {
    if (!isOnline.value) return;
    _rideReconnectTimer?.cancel();
    _rideReconnectTimer = Timer(
      const Duration(seconds: 2),
      () {
        if (isOnline.value) {
          _connectRideSocket();
        }
      },
    );
  }

  void _connectBiddingSocketForRide(String rideId) async {
    try {
      final data = await _biddingRepository.getSessionForRide(rideId);
      final sessionId =
          data['session_id']?.toString() ?? data['id']?.toString();
      if (sessionId == null || sessionId.isEmpty) return;
      await _biddingSocketSub?.cancel();
      _biddingSocketSub = _biddingSocketRepository
          .connectDriver(sessionId: sessionId)
          .listen((event) {
        if (event.type == SBiddingSocketEventType.bidAccepted) {
          refreshActiveRide();
        }
      });
    } catch (_) {}
  }
}

double _distanceMeters(SCoordinate a, SCoordinate b) {
  const radius = 6371000.0;
  final lat1 = _radians(a.latitude);
  final lat2 = _radians(b.latitude);
  final deltaLat = _radians(b.latitude - a.latitude);
  final deltaLng = _radians(b.longitude - a.longitude);
  final value = sin(deltaLat / 2) * sin(deltaLat / 2) +
      cos(lat1) * cos(lat2) * sin(deltaLng / 2) * sin(deltaLng / 2);
  return radius * 2 * atan2(sqrt(value), sqrt(1 - value));
}

double _radians(double degrees) => degrees * pi / 180.0;

int? driverBidEtaMinutes(SDriverRideRequest request) {
  final duration = request.driverToPickup?.durationMinutes;
  if (duration == null) return null;
  return max(1, duration.round());
}
