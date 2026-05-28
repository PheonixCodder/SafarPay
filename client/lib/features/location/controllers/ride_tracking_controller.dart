import 'dart:async';

import 'package:flutter/widgets.dart';
import 'package:get/get.dart';

import '../../../common/runtime/app_lifecycle_controller.dart';
import '../../../common/runtime/runtime_diagnostics_controller.dart';
import '../../../common/widgets/maps/map_models.dart';
import '../../../data/rides/ride_models.dart';
import '../../rides/controllers/ride_lifecycle_coordinator.dart';
import '../../rides/domain/ride_lifecycle.dart';
import '../../rides/orchestration/ride_realtime_orchestrator.dart';
import '../data/device_location_service.dart';
import '../data/geospatial_repository.dart';
import '../data/live_ride_socket_event.dart';
import '../data/live_ride_socket_repository.dart';
import '../data/location_repository.dart';
import '../data/ride_repository.dart';
import '../data/ride_socket_event.dart';
import '../data/ride_socket_repository.dart';
import '../domain/location_models.dart';

class SRideTrackingController extends GetxController {
  SRideTrackingController({
    required this.rideId,
    SLocationRepository locationRepository = const SLocationRepository(),
    SRideRepository rideRepository = const SRideRepository(),
    SGeospatialRepository geospatialRepository = const SGeospatialRepository(),
    SLiveRideSocketRepository? socketRepository,
    SRideSocketRepository? rideSocketRepository,
    SDeviceLocationService deviceLocationService =
        const SDeviceLocationService(),
    SAppLifecycleController? appLifecycleController,
    SRideRealtimeOrchestrator? realtimeOrchestrator,
  })  : _locationRepository = locationRepository,
        _rideRepository = rideRepository,
        _geospatialRepository = geospatialRepository,
        _socketRepository = socketRepository ?? SLiveRideSocketRepository(),
        _rideSocketRepository = rideSocketRepository ?? SRideSocketRepository(),
        _deviceLocationService = deviceLocationService,
        _appLifecycleController =
            appLifecycleController ?? SAppLifecycleController.instance,
        _realtimeOrchestrator =
            realtimeOrchestrator ?? SRideRealtimeOrchestrator.instance;

  final String rideId;
  final SLocationRepository _locationRepository;
  final SRideRepository _rideRepository;
  final SGeospatialRepository _geospatialRepository;
  final SLiveRideSocketRepository _socketRepository;
  final SRideSocketRepository _rideSocketRepository;
  final SDeviceLocationService _deviceLocationService;
  final SAppLifecycleController _appLifecycleController;
  final SRideRealtimeOrchestrator _realtimeOrchestrator;

  final RxBool isConnecting = false.obs;
  final RxString statusMessage = 'Connecting to ride tracking...'.obs;
  final RxString rideStatus = ''.obs;
  final RxString assignedDriverId = ''.obs;
  final RxString startVerificationCode = ''.obs;
  final RxString endVerificationCode = ''.obs;
  final RxBool requiresOtpStart = false.obs;
  final RxBool requiresOtpEnd = false.obs;
  final RxBool isGeneratingVerificationCode = false.obs;
  final Rxn<SDriverLiveLocation> driverLocation = Rxn<SDriverLiveLocation>();
  final Rxn<SPassengerLiveLocation> passengerLocation =
      Rxn<SPassengerLiveLocation>();
  final Rxn<SCoordinate> routeDestination = Rxn<SCoordinate>();
  final Rxn<SRoutePreview> route = Rxn<SRoutePreview>();

  StreamSubscription<SLiveRideSocketEvent>? _socketSubscription;
  StreamSubscription<SRideSocketEvent>? _rideSocketSubscription;
  StreamSubscription<SCoordinate>? _passengerSubscription;
  Timer? _locationReconnectTimer;
  Worker? _appLifecycleWorker;
  DateTime? _lastRouteRefreshAt;
  bool _isClosed = false;

  List<SMapMarker> get markers {
    return [
      if (driverLocation.value != null)
        SMapMarker(
          id: driverLocation.value!.driverId,
          coordinate: driverLocation.value!.coordinate,
          type: SMapMarkerType.driver,
          label: 'Driver',
          heading: driverLocation.value!.heading,
        ),
      if (routeDestination.value != null)
        SMapMarker(
          id: 'ride-destination',
          coordinate: routeDestination.value!,
          type: rideStatus.value == 'IN_PROGRESS'
              ? SMapMarkerType.dropoff
              : SMapMarkerType.pickup,
          label: rideStatus.value == 'IN_PROGRESS' ? 'Dropoff' : 'Pickup',
        ),
      if (passengerLocation.value != null)
        SMapMarker(
          id: passengerLocation.value!.userId,
          coordinate: passengerLocation.value!.coordinate,
          type: SMapMarkerType.passenger,
          label: 'You',
        ),
    ];
  }

  @override
  void onInit() {
    super.onInit();
    _appLifecycleWorker = ever<AppLifecycleState>(
      _appLifecycleController.state,
      (state) {
        if (state == AppLifecycleState.resumed) {
          unawaited(recoverRealtimeState());
        }
      },
    );
    connect();
  }

  @override
  void onClose() {
    _isClosed = true;
    _locationReconnectTimer?.cancel();
    _socketSubscription?.cancel();
    _rideSocketSubscription?.cancel();
    _passengerSubscription?.cancel();
    _appLifecycleWorker?.dispose();
    _socketRepository.close();
    _rideSocketRepository.close();
    SRuntimeDiagnosticsController.instance.updateRealtimeChannel(
      SRuntimeRealtimeChannel.passengerRide,
      isConnected: false,
    );
    SRuntimeDiagnosticsController.instance.updateRealtimeChannel(
      SRuntimeRealtimeChannel.passengerLocation,
      isConnected: false,
    );
    super.onClose();
  }

  Future<void> connect() async {
    isConnecting.value = true;
    unawaited(_seedPassengerLocation());
    try {
      await _refreshRideDetails();
      if (_canTrackLiveLocation) {
        final snapshot = await _locationRepository.getRideLocations(rideId);
        driverLocation.value = snapshot.driver;
        passengerLocation.value = snapshot.passenger;
        unawaited(_refreshTrackingRoute(force: true));
      } else {
        statusMessage.value = 'Waiting for a driver to accept.';
      }
    } catch (_) {
      statusMessage.value = 'Waiting for live ride location...';
    }

    if (_canTrackLiveLocation) _connectLocationSocket();

    if (_shouldConnectRideLifecycleSocket) _connectRideLifecycleSocket();

    _startPassengerLocationStream();

    isConnecting.value = false;
  }

  Future<void> recoverRealtimeState() async {
    if (_isClosed) return;
    await _refreshRideDetails();
    if (_canTrackLiveLocation) {
      try {
        final snapshot = await _locationRepository.getRideLocations(rideId);
        driverLocation.value = snapshot.driver;
        passengerLocation.value = snapshot.passenger;
        unawaited(_refreshTrackingRoute(force: true));
      } catch (_) {}
      if (_socketSubscription == null) _connectLocationSocket();
    } else {
      await _disconnectLocationSocket();
    }
    if (_shouldConnectRideLifecycleSocket && _rideSocketSubscription == null) {
      _connectRideLifecycleSocket();
    }
    _startPassengerLocationStream();
  }

  void _startPassengerLocationStream() {
    if (_passengerSubscription != null) return;
    _passengerSubscription =
        _deviceLocationService.positionStream().listen((coordinate) {
      passengerLocation.value = SPassengerLiveLocation(
        userId: 'passenger',
        coordinate: coordinate,
        updatedAt: DateTime.now(),
      );
      if (routeDestination.value == null) unawaited(_refreshTrackingRoute());
    }, onError: (_) {});
  }

  Future<void> _seedPassengerLocation() async {
    try {
      final coordinate = await _deviceLocationService.currentCoordinate();
      passengerLocation.value = SPassengerLiveLocation(
        userId: 'passenger',
        coordinate: coordinate,
        updatedAt: DateTime.now(),
      );
      if (routeDestination.value == null) unawaited(_refreshTrackingRoute());
    } catch (_) {}
  }

  void _handleSocketEvent(SLiveRideSocketEvent event) {
    if (event.type == SLiveRideSocketEventType.driverLocationUpdated &&
        event.driverLocation != null) {
      driverLocation.value = event.driverLocation;
      statusMessage.value = 'Driver location updated.';
      unawaited(_refreshTrackingRoute());
    } else if (event.type == SLiveRideSocketEventType.error) {
      statusMessage.value = event.detail ?? 'Ride tracking error.';
    }
  }

  void _handleRideSocketEvent(SRideSocketEvent event) {
    if (event.type == SRideSocketEventType.rideUpdated) {
      rideStatus.value = event.status ?? rideStatus.value;
      statusMessage.value = 'Ride status updated.';
      unawaited(_handleRideUpdated());
    } else if (event.type == SRideSocketEventType.error) {
      statusMessage.value = event.detail ?? 'Ride status error.';
    }
  }

  Future<void> _handleRideUpdated() async {
    await _refreshRideDetails();
    if (_canTrackLiveLocation && _socketSubscription == null) {
      _scheduleLocationReconnect();
    } else if (!_canTrackLiveLocation) {
      await _disconnectLocationSocket();
    }
    if (!_shouldConnectRideLifecycleSocket) {
      await _rideSocketSubscription?.cancel();
      _rideSocketSubscription = null;
    }
  }

  void _connectRideLifecycleSocket() {
    if (_isClosed || !_shouldConnectRideLifecycleSocket) return;
    _rideSocketSubscription?.cancel();
    SRuntimeDiagnosticsController.instance.updateRealtimeChannel(
      SRuntimeRealtimeChannel.passengerRide,
      isConnected: true,
    );
    _rideSocketSubscription = _rideSocketRepository
        .connectPassenger(rideId: rideId)
        .listen(_handleRideSocketEvent, onError: (_) {
      _rideSocketSubscription = null;
      SRuntimeDiagnosticsController.instance.updateRealtimeChannel(
        SRuntimeRealtimeChannel.passengerRide,
        isConnected: false,
      );
      statusMessage.value = 'Ride status updates are reconnecting...';
    }, onDone: () {
      _rideSocketSubscription = null;
      SRuntimeDiagnosticsController.instance.updateRealtimeChannel(
        SRuntimeRealtimeChannel.passengerRide,
        isConnected: false,
      );
    });
  }

  void _connectLocationSocket() {
    if (_isClosed || !_canTrackLiveLocation) return;
    _locationReconnectTimer?.cancel();
    _socketSubscription?.cancel();
    SRuntimeDiagnosticsController.instance.updateRealtimeChannel(
      SRuntimeRealtimeChannel.passengerLocation,
      isConnected: true,
    );
    _socketSubscription = _socketRepository.connect(rideId).listen(
      _handleSocketEvent,
      onError: (_) {
        _socketSubscription = null;
        SRuntimeDiagnosticsController.instance.updateRealtimeChannel(
          SRuntimeRealtimeChannel.passengerLocation,
          isConnected: false,
        );
        statusMessage.value = 'Ride tracking is reconnecting...';
        isConnecting.value = false;
        _scheduleLocationReconnect();
      },
      onDone: () {
        _socketSubscription = null;
        SRuntimeDiagnosticsController.instance.updateRealtimeChannel(
          SRuntimeRealtimeChannel.passengerLocation,
          isConnected: false,
        );
        if (_isClosed) return;
        statusMessage.value = 'Ride tracking disconnected.';
        isConnecting.value = false;
        _scheduleLocationReconnect();
      },
    );
  }

  void _scheduleLocationReconnect() {
    if (_isClosed ||
        !_canTrackLiveLocation ||
        _locationReconnectTimer?.isActive == true) {
      return;
    }
    _locationReconnectTimer = Timer(const Duration(seconds: 2), () async {
      if (_isClosed || !_canTrackLiveLocation) return;
      try {
        final snapshot = await _locationRepository.getRideLocations(rideId);
        driverLocation.value = snapshot.driver;
        passengerLocation.value = snapshot.passenger;
        unawaited(_refreshTrackingRoute(force: true));
      } catch (_) {}
      _connectLocationSocket();
    });
  }

  Future<void> _disconnectLocationSocket() async {
    _locationReconnectTimer?.cancel();
    await _socketSubscription?.cancel();
    _socketSubscription = null;
    await _socketRepository.close();
    SRuntimeDiagnosticsController.instance.updateRealtimeChannel(
      SRuntimeRealtimeChannel.passengerLocation,
      isConnected: false,
    );
  }

  Future<void> _refreshRideDetails() async {
    try {
      final rideData = await _rideRepository.fetchRide(rideId);
      final ride = RideResponse.fromJson(rideData);
      SRideLifecycleCoordinator.instance.syncPassengerSnapshot(
        SRideLifecycleSnapshot.fromRide(ride),
      );
      final status = ride.status.value;
      rideStatus.value = status;
      assignedDriverId.value = ride.assignedDriverId ?? '';
      _applyRouteDestination(ride, status);
      requiresOtpStart.value = rideData['requires_otp_start'] == true;
      requiresOtpEnd.value = rideData['requires_otp_end'] == true;
      _applyExistingVerificationCode(rideData);
      await _ensureVerificationCodeFor(status);
      unawaited(_refreshTrackingRoute(force: true));
    } catch (_) {
      statusMessage.value = 'Ride details are reconnecting...';
    }
  }

  bool get _canTrackLiveLocation {
    final snapshot = SRideLifecycleCoordinator.instance.snapshotForRide(rideId);
    if (snapshot == null) return false;
    return _realtimeOrchestrator.shouldConnectPassengerLiveLocationSocket(
      snapshot,
    );
  }

  bool get _shouldConnectRideLifecycleSocket {
    final snapshot = SRideLifecycleCoordinator.instance.snapshotForRide(rideId);
    if (snapshot == null) return true;
    return _realtimeOrchestrator.shouldConnectPassengerRideLifecycleSocket(
      snapshot,
    );
  }

  void _applyRouteDestination(RideResponse ride, String status) {
    final preferredStop =
        status == 'IN_PROGRESS' ? ride.dropoffStop : ride.pickupStop;
    if (preferredStop != null) {
      routeDestination.value = SCoordinate(
        latitude: preferredStop.latitude,
        longitude: preferredStop.longitude,
      );
      return;
    }

    final preferredType = status == 'IN_PROGRESS' ? StopType.dropoff : StopType.pickup;
    for (final stop in ride.stops) {
      if (stop.stopType != preferredType) continue;
      routeDestination.value = SCoordinate(
        latitude: stop.latitude,
        longitude: stop.longitude,
      );
      return;
    }
  }

  Future<void> _refreshTrackingRoute({bool force = false}) async {
    final origin = driverLocation.value?.coordinate;
    final destination =
        routeDestination.value ?? passengerLocation.value?.coordinate;
    if (origin == null || destination == null) return;

    final now = DateTime.now();
    final lastRefresh = _lastRouteRefreshAt;
    if (!force &&
        lastRefresh != null &&
        now.difference(lastRefresh) < const Duration(seconds: 15)) {
      return;
    }

    _lastRouteRefreshAt = now;
    try {
      route.value = await _geospatialRepository.calculateRoute(
        origin: origin,
        destination: destination,
      );
    } catch (_) {}
  }

  void _applyExistingVerificationCode(Map<String, dynamic> ride) {
    final values = ride['verification_codes'];
    if (values is! List) return;
    for (final value in values.reversed) {
      if (value is! Map<String, dynamic>) continue;
      if (value['is_verified'] == true) continue;
      final code = value['code']?.toString();
      if (code == null || code.isEmpty) continue;
      if (rideStatus.value == 'IN_PROGRESS') {
        endVerificationCode.value = code;
      } else {
        startVerificationCode.value = code;
      }
      return;
    }
  }

  Future<void> _ensureVerificationCodeFor(String status) async {
    if (isGeneratingVerificationCode.value) return;
    final needsStartCode = requiresOtpStart.value &&
        (status == 'ACCEPTED' || status == 'ARRIVING') &&
        startVerificationCode.value.isEmpty;
    final needsEndCode = requiresOtpEnd.value &&
        status == 'IN_PROGRESS' &&
        endVerificationCode.value.isEmpty;
    if (!needsStartCode && !needsEndCode) return;

    isGeneratingVerificationCode.value = true;
    try {
      final data = await _rideRepository.generateVerificationCode(
        rideId: rideId,
      );
      final code = data['code']?.toString() ?? '';
      if (code.isEmpty) return;
      if (needsEndCode) {
        endVerificationCode.value = code;
      } else {
        startVerificationCode.value = code;
      }
    } catch (_) {
      statusMessage.value = 'Unable to prepare trip verification code.';
    } finally {
      isGeneratingVerificationCode.value = false;
    }
  }
}
