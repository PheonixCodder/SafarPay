import 'package:get/get.dart';

import '../data/geospatial_repository.dart';
import '../data/ride_repository.dart';
import '../domain/location_models.dart';

class SRidePreviewController extends GetxController {
  SRidePreviewController({
    required SAddressResult pickup,
    required SAddressResult dropoff,
    SGeospatialRepository geospatialRepository = const SGeospatialRepository(),
    SRideRepository rideRepository = const SRideRepository(),
  })  : pickupAddress = pickup,
        dropoffAddress = dropoff,
        _geospatialRepository = geospatialRepository,
        _rideRepository = rideRepository;

  final SAddressResult pickupAddress;
  final SAddressResult dropoffAddress;
  final SGeospatialRepository _geospatialRepository;
  final SRideRepository _rideRepository;

  final RxBool isLoading = false.obs;
  final RxBool isCreatingRide = false.obs;
  final RxString errorMessage = ''.obs;
  final Rxn<SRoutePreview> route = Rxn<SRoutePreview>();
  final RxBool pickupValid = true.obs;

  @override
  void onInit() {
    super.onInit();
    loadRoutePreview();
  }

  Future<void> loadRoutePreview() async {
    isLoading.value = true;
    errorMessage.value = '';
    try {
      final validation = await _geospatialRepository.validatePickup(
        pickupAddress.coordinate,
      );
      pickupValid.value = validation['is_in_service_area'] as bool? ?? true;
      if (!pickupValid.value) {
        errorMessage.value = 'Pickup is outside the current service area.';
      }
      route.value = await _geospatialRepository.calculateRoute(
        origin: pickupAddress.coordinate,
        destination: dropoffAddress.coordinate,
      );
    } catch (error) {
      errorMessage.value = 'Route preview is unavailable.';
    } finally {
      isLoading.value = false;
    }
  }

  Future<String?> createRide() async {
    isCreatingRide.value = true;
    errorMessage.value = '';
    try {
      final response = await _rideRepository.createRide(
        SRideRepository.buildCityRideRequest(
          pickup: pickupAddress,
          dropoff: dropoffAddress,
        ),
      );
      final rideId = response['id']?.toString();
      if (rideId == null || rideId.isEmpty) {
        errorMessage.value = 'Ride created without a valid id.';
        return null;
      }
      return rideId;
    } catch (error) {
      errorMessage.value = 'Ride request failed. Try again.';
      return null;
    } finally {
      isCreatingRide.value = false;
    }
  }
}
