import 'dart:async';

import 'package:flutter/material.dart';
import 'package:get/get.dart';

import '../../../common/widgets/maps/map_models.dart';
import '../../../utils/helpers/helpers.dart';
import '../data/bidding_repository.dart';
import '../data/bidding_socket_event.dart';
import '../data/bidding_socket_repository.dart';
import '../data/demo/location_demo_data.dart';
import '../data/device_location_service.dart';
import '../data/geospatial_repository.dart';
import '../data/location_repository.dart';
import '../data/ride_repository.dart';
import '../domain/bidding_models.dart';
import '../domain/location_models.dart';
import '../domain/ride_booking_models.dart';

class SRideSearchController extends GetxController {
  SRideSearchController({
    SLocationRepository locationRepository = const SLocationRepository(),
    SDeviceLocationService deviceLocationService =
        const SDeviceLocationService(),
    SGeospatialRepository geospatialRepository = const SGeospatialRepository(),
    SRideRepository rideRepository = const SRideRepository(),
    SBiddingRepository biddingRepository = const SBiddingRepository(),
    SBiddingSocketRepository? biddingSocketRepository,
    SPassengerServiceCategory initialCategory =
        SPassengerServiceCategory.cityRides,
  })  : _locationRepository = locationRepository,
        _deviceLocationService = deviceLocationService,
        _geospatialRepository = geospatialRepository,
        _rideRepository = rideRepository,
        _biddingRepository = biddingRepository,
        _biddingSocketRepository =
            biddingSocketRepository ?? SBiddingSocketRepository(),
        _initialCategory = initialCategory;

  static const SCoordinate fallbackCenter = SCoordinate(
    latitude: 31.5204,
    longitude: 74.3587,
  );

  final SLocationRepository _locationRepository;
  final SDeviceLocationService _deviceLocationService;
  final SGeospatialRepository _geospatialRepository;
  final SRideRepository _rideRepository;
  final SBiddingRepository _biddingRepository;
  final SBiddingSocketRepository _biddingSocketRepository;
  final SPassengerServiceCategory _initialCategory;

  final SMapController mapController = SMapController();
  final TextEditingController pickupSearchController = TextEditingController();
  final TextEditingController dropoffSearchController = TextEditingController();

  final Rx<SBookingSheetMode> sheetMode = SBookingSheetMode.compose.obs;
  final Rx<SBookingLocationTarget> activeTarget =
      SBookingLocationTarget.dropoff.obs;
  final RxBool isLoading = false.obs;
  final RxBool isRouteLoading = false.obs;
  final RxBool isCreatingRide = false.obs;
  final RxBool isResolvingPin = false.obs;
  final RxBool autoAcceptOffer = false.obs;
  final RxString errorMessage = ''.obs;
  final RxString createdRideId = ''.obs;
  final RxString biddingSessionId = ''.obs;
  final RxList<SBid> driverBids = <SBid>[].obs;
  final RxList<SCounterOffer> counterOffers = <SCounterOffer>[].obs;
  final Rxn<SBid> acceptedBid = Rxn<SBid>();
  final Rxn<SAddressResult> pickup = Rxn<SAddressResult>();
  final Rxn<SAddressResult> selectedDropoff = Rxn<SAddressResult>();
  final Rxn<SRoutePreview> route = Rxn<SRoutePreview>();
  final RxList<SAddressResult> results = <SAddressResult>[].obs;
  final Rx<SPassengerServiceCategory> selectedCategory =
      SPassengerServiceCategory.cityRides.obs;
  final Rxn<SRideVehicleOffer> selectedVehicle = Rxn<SRideVehicleOffer>();
  final RxDouble passengerOffer = 0.0.obs;

  Timer? _debounce;
  StreamSubscription<SBiddingSocketEvent>? _biddingSocketSub;

  List<SRideVehicleOffer> get availableVehicles {
    return SRideBookingCatalog.vehiclesFor(selectedCategory.value);
  }

  bool get hasPickupAndDropoff {
    return pickup.value != null && selectedDropoff.value != null;
  }

  SCoordinate get mapCenter {
    return pickup.value?.coordinate ??
        selectedDropoff.value?.coordinate ??
        fallbackCenter;
  }

  @override
  void onInit() {
    super.onInit();
    selectCategory(_initialCategory);
    loadCurrentPickup();
  }

  @override
  void onClose() {
    _debounce?.cancel();
    _biddingSocketSub?.cancel();
    _biddingSocketRepository.close();
    pickupSearchController.dispose();
    dropoffSearchController.dispose();
    super.onClose();
  }

  Future<void> loadCurrentPickup() async {
    try {
      final coordinate = await _deviceLocationService.currentCoordinate();
      final address = await _locationRepository.reverseGeocode(coordinate);
      if (isClosed) return;
      pickup.value = address;
      pickupSearchController.text = address.formatted;
    } catch (_) {
      if (isClosed) return;
      pickup.value = SLocationDemoData.pickup;
      pickupSearchController.text = SLocationDemoData.pickup.formatted;
      errorMessage.value = '';
    }
  }

  void focusSearch(SBookingLocationTarget target) {
    activeTarget.value = target;
    sheetMode.value = SBookingSheetMode.search;
    errorMessage.value = '';
    results.clear();
    final currentText = target == SBookingLocationTarget.pickup
        ? pickupSearchController.text
        : dropoffSearchController.text;
    if (currentText.trim().isNotEmpty) search(currentText);
  }

  void startMapPinSelection(SBookingLocationTarget target) {
    activeTarget.value = target;
    sheetMode.value = SBookingSheetMode.compose;
    results.clear();
    errorMessage.value = '';
  }

  void onSearchChanged(String value) {
    _debounce?.cancel();
    _debounce = Timer(const Duration(milliseconds: 450), () {
      search(value);
    });
  }

  Future<void> search(String query) async {
    final trimmed = query.trim();
    if (trimmed.isEmpty) {
      results.clear();
      errorMessage.value = '';
      return;
    }

    isLoading.value = true;
    errorMessage.value = '';
    try {
      final result = await _locationRepository.geocode(trimmed);
      results.assignAll(result.formatted.isEmpty ? const [] : [result]);
      if (results.isEmpty) errorMessage.value = 'No matching places found.';
    } catch (_) {
      errorMessage.value = 'Search is unavailable. Try again.';
    } finally {
      isLoading.value = false;
    }
  }

  Future<void> confirmMapPin() async {
    isResolvingPin.value = true;
    errorMessage.value = '';
    try {
      final coordinate = await mapController.centerCoordinate();
      if (coordinate == null) {
        errorMessage.value = 'Move the map once, then try again.';
        return;
      }
      final address = await _locationRepository.reverseGeocode(coordinate);
      selectAddress(address);
    } catch (_) {
      errorMessage.value = 'Unable to read this map location.';
    } finally {
      isResolvingPin.value = false;
    }
  }

  void selectAddress(SAddressResult result) {
    if (activeTarget.value == SBookingLocationTarget.pickup) {
      pickup.value = result;
      pickupSearchController.text = result.formatted;
    } else {
      selectedDropoff.value = result;
      dropoffSearchController.text = result.formatted;
    }

    results.clear();
    sheetMode.value =
        hasPickupAndDropoff ? SBookingSheetMode.route : SBookingSheetMode.compose;
    if (hasPickupAndDropoff) loadRoutePreview();
  }

  void selectCategory(SPassengerServiceCategory category) {
    selectedCategory.value = category;
    final vehicles = SRideBookingCatalog.vehiclesFor(category);
    selectedVehicle.value = vehicles.isEmpty ? null : vehicles.first;
    _resetPassengerOffer();
  }

  void selectVehicle(SRideVehicleOffer offer) {
    selectedVehicle.value = offer;
    _resetPassengerOffer();
  }

  void showVehicleSelection() {
    if (!hasPickupAndDropoff) {
      SHelperFunctions.showSnackBar('Select pickup and dropoff first.');
      return;
    }
    sheetMode.value = SBookingSheetMode.vehicles;
  }

  void adjustPassengerOffer(double delta) {
    final nextValue = passengerOffer.value + delta;
    final minimum = (selectedVehicle.value?.baseFare ?? 100) * 0.7;
    passengerOffer.value = nextValue < minimum ? minimum : nextValue;
  }

  Future<void> loadRoutePreview() async {
    final origin = pickup.value;
    final destination = selectedDropoff.value;
    if (origin == null || destination == null) return;

    isRouteLoading.value = true;
    errorMessage.value = '';
    try {
      route.value = await _geospatialRepository.calculateRoute(
        origin: origin.coordinate,
        destination: destination.coordinate,
      );
      _resetPassengerOffer();
    } catch (_) {
      errorMessage.value = 'Route preview is unavailable.';
    } finally {
      isRouteLoading.value = false;
    }
  }

  Future<String?> createHybridRide() async {
    final origin = pickup.value;
    final destination = selectedDropoff.value;
    final offer = selectedVehicle.value;
    if (origin == null || destination == null || offer == null) return null;

    if (!offer.isBookable) {
      errorMessage.value = 'This category needs one more backend screen first.';
      return null;
    }

    isCreatingRide.value = true;
    errorMessage.value = '';
    try {
      final response = await _rideRepository.createRide(
        SRideRepository.buildHybridRideRequest(
          pickup: origin,
          dropoff: destination,
          offer: offer,
          passengerOffer: passengerOffer.value,
          autoAcceptDriver: autoAcceptOffer.value,
        ),
      );
      final rideId = response['id']?.toString() ?? '';
      final sessionId = rideId.isEmpty
          ? ''
          : await _loadBiddingSessionForRide(rideId);
      createdRideId.value = rideId;
      biddingSessionId.value = sessionId;
      if (sessionId.isNotEmpty) {
        _connectBiddingSocket(sessionId);
      }
      sheetMode.value = SBookingSheetMode.matching;
      return rideId.isEmpty ? null : rideId;
    } catch (_) {
      errorMessage.value = 'Offer request failed. Try again.';
      return null;
    } finally {
      isCreatingRide.value = false;
    }
  }

  Future<String> _loadBiddingSessionForRide(String rideId) async {
    for (var attempt = 0; attempt < 3; attempt++) {
      try {
        final response = await _biddingRepository.getSessionForRide(rideId);
        final session = SBiddingSession.fromJson(response);
        driverBids.assignAll(session.bids);
        counterOffers.assignAll(session.counterOffers);
        final sessionId = response['session_id']?.toString() ??
            response['id']?.toString() ??
            '';
        if (sessionId.isNotEmpty) return sessionId;
      } catch (_) {}
      await Future<void>.delayed(const Duration(milliseconds: 700));
    }
    return '';
  }

  Future<bool> acceptDriverBid(SBid bid) async {
    if (biddingSessionId.value.isEmpty) return false;

    isCreatingRide.value = true;
    errorMessage.value = '';
    try {
      final response = await _biddingRepository.acceptBid(
        sessionId: biddingSessionId.value,
        bidId: bid.id,
      );
      acceptedBid.value = SBid.fromJson(response);
      sheetMode.value = SBookingSheetMode.matching;
      return true;
    } catch (_) {
      errorMessage.value = 'Unable to accept this offer. Try again.';
      return false;
    } finally {
      isCreatingRide.value = false;
    }
  }

  Future<void> sendCounterOffer() async {
    if (biddingSessionId.value.isEmpty) return;

    try {
      final response = await _biddingRepository.sendPassengerCounter(
        sessionId: biddingSessionId.value,
        counterPrice: passengerOffer.value,
      );
      counterOffers.add(SCounterOffer.fromJson(response));
    } catch (_) {
      errorMessage.value = 'Unable to send counter offer.';
    }
  }

  void _connectBiddingSocket(String sessionId) {
    _biddingSocketSub?.cancel();

    _biddingSocketSub = _biddingSocketRepository
        .connectPassenger(sessionId: sessionId)
        .listen(_handleBiddingEvent, onError: (_) {
      errorMessage.value = 'Live offers disconnected. Retrying soon.';
    });
  }

  void _handleBiddingEvent(SBiddingSocketEvent event) {
    switch (event.type) {
      case SBiddingSocketEventType.bidPlaced:
        final bid = event.bid;
        if (bid != null) {
          driverBids.removeWhere((item) => item.id == bid.id);
          driverBids.insert(0, bid);
        }
      case SBiddingSocketEventType.bidAccepted:
        if (event.bid != null) acceptedBid.value = event.bid;
      case SBiddingSocketEventType.counterOfferCreated:
      case SBiddingSocketEventType.counterOfferAccepted:
        final counter = event.counterOffer;
        if (counter != null) {
          counterOffers.removeWhere((item) => item.id == counter.id);
          counterOffers.insert(0, counter);
        }
      case SBiddingSocketEventType.bidWithdrawn:
        final bid = event.bid;
        if (bid != null) driverBids.removeWhere((item) => item.id == bid.id);
      case SBiddingSocketEventType.sessionUpdated:
      case SBiddingSocketEventType.ping:
      case SBiddingSocketEventType.pong:
      case SBiddingSocketEventType.error:
      case SBiddingSocketEventType.unknown:
        break;
    }
  }

  void _resetPassengerOffer() {
    final offer = selectedVehicle.value;
    if (offer == null) {
      passengerOffer.value = 0;
      return;
    }

    final routeMultiplier = route.value == null ? 1 : route.value!.distanceKm;
    final estimate = offer.baseFare + (routeMultiplier * 18);
    passengerOffer.value = estimate.roundToDouble();
  }
}
