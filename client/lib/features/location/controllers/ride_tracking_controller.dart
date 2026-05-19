import 'dart:async';

import 'package:get/get.dart';

import '../../../common/widgets/maps/map_models.dart';
import '../data/device_location_service.dart';
import '../data/live_ride_socket_event.dart';
import '../data/live_ride_socket_repository.dart';
import '../data/location_repository.dart';
import '../data/ride_socket_event.dart';
import '../data/ride_socket_repository.dart';
import '../domain/location_models.dart';

class SRideTrackingController extends GetxController {
  SRideTrackingController({
    required this.rideId,
    SLocationRepository locationRepository = const SLocationRepository(),
    SLiveRideSocketRepository? socketRepository,
    SRideSocketRepository? rideSocketRepository,
    SDeviceLocationService deviceLocationService =
        const SDeviceLocationService(),
  })  : _locationRepository = locationRepository,
        _socketRepository = socketRepository ?? SLiveRideSocketRepository(),
        _rideSocketRepository = rideSocketRepository ?? SRideSocketRepository(),
        _deviceLocationService = deviceLocationService;

  final String rideId;
  final SLocationRepository _locationRepository;
  final SLiveRideSocketRepository _socketRepository;
  final SRideSocketRepository _rideSocketRepository;
  final SDeviceLocationService _deviceLocationService;

  final RxBool isConnecting = false.obs;
  final RxString statusMessage = 'Connecting to ride tracking...'.obs;
  final RxString rideStatus = ''.obs;
  final Rxn<SDriverLiveLocation> driverLocation = Rxn<SDriverLiveLocation>();
  final Rxn<SPassengerLiveLocation> passengerLocation =
      Rxn<SPassengerLiveLocation>();

  StreamSubscription<SLiveRideSocketEvent>? _socketSubscription;
  StreamSubscription<SRideSocketEvent>? _rideSocketSubscription;
  StreamSubscription<SCoordinate>? _passengerSubscription;

  List<SMapMarker> get markers {
    return [
      if (driverLocation.value != null)
        SMapMarker(
          id: driverLocation.value!.driverId,
          coordinate: driverLocation.value!.coordinate,
          type: SMapMarkerType.driver,
          label: 'Driver',
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
    connect();
  }

  @override
  void onClose() {
    _socketSubscription?.cancel();
    _rideSocketSubscription?.cancel();
    _passengerSubscription?.cancel();
    _socketRepository.close();
    _rideSocketRepository.close();
    super.onClose();
  }

  Future<void> connect() async {
    isConnecting.value = true;
    try {
      final snapshot = await _locationRepository.getRideLocations(rideId);
      driverLocation.value = snapshot.driver;
      passengerLocation.value = snapshot.passenger;
    } catch (_) {
      statusMessage.value = 'Waiting for live ride location...';
    }

    _socketSubscription = _socketRepository.connect(rideId).listen(
      _handleSocketEvent,
      onError: (_) {
        statusMessage.value = 'Ride tracking is reconnecting...';
        isConnecting.value = false;
      },
      onDone: () {
        statusMessage.value = 'Ride tracking disconnected.';
        isConnecting.value = false;
      },
    );

    _rideSocketSubscription = _rideSocketRepository
        .connectPassenger(rideId: rideId)
        .listen(_handleRideSocketEvent, onError: (_) {
      statusMessage.value = 'Ride status updates are reconnecting...';
    });

    _passengerSubscription =
        _deviceLocationService.positionStream().listen((coordinate) {
      passengerLocation.value = SPassengerLiveLocation(
        userId: 'passenger',
        coordinate: coordinate,
        updatedAt: DateTime.now(),
      );
    }, onError: (_) {});

    isConnecting.value = false;
  }

  void _handleSocketEvent(SLiveRideSocketEvent event) {
    if (event.type == SLiveRideSocketEventType.driverLocationUpdated &&
        event.driverLocation != null) {
      driverLocation.value = event.driverLocation;
      statusMessage.value = 'Driver location updated.';
    } else if (event.type == SLiveRideSocketEventType.error) {
      statusMessage.value = event.detail ?? 'Ride tracking error.';
    }
  }

  void _handleRideSocketEvent(SRideSocketEvent event) {
    if (event.type == SRideSocketEventType.rideUpdated) {
      rideStatus.value = event.status ?? rideStatus.value;
      statusMessage.value = 'Ride status updated.';
    } else if (event.type == SRideSocketEventType.error) {
      statusMessage.value = event.detail ?? 'Ride status error.';
    }
  }
}
