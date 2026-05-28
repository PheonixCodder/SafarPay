import 'package:get/get.dart';

import '../../../data/rides/ride_models.dart';
import '../../../utils/logging/logger.dart';
import '../../location/data/ride_repository.dart';

enum STripsFilter {
  ongoing,
  scheduled,
  canceled,
  completed,
}

class STripsController extends GetxController {
  STripsController({SRideRepository repository = const SRideRepository()})
      : _repository = repository;

  final SRideRepository _repository;

  final RxInt selectedIndex = 0.obs;
  final RxBool isLoading = false.obs;
  final RxBool isRefreshing = false.obs;
  final RxString errorMessage = ''.obs;
  final RxList<RideSummaryResponse> rides = <RideSummaryResponse>[].obs;

  static const List<STripsFilter> filters = [
    STripsFilter.ongoing,
    STripsFilter.scheduled,
    STripsFilter.canceled,
    STripsFilter.completed,
  ];

  STripsFilter get selectedFilter => filters[selectedIndex.value];

  @override
  void onInit() {
    super.onInit();
    loadTrips();
  }

  Future<void> loadTrips() async {
    if (isLoading.value) return;
    isLoading.value = true;
    errorMessage.value = '';
    try {
      rides.assignAll(await _repository.listPassengerRides(limit: 80));
    } catch (error) {
      SLoggerHelper.error('Unable to load passenger trips', error);
      errorMessage.value = 'Unable to load your trips right now.';
    } finally {
      isLoading.value = false;
    }
  }

  Future<void> refreshTrips() async {
    if (isRefreshing.value) return;
    isRefreshing.value = true;
    errorMessage.value = '';
    try {
      rides.assignAll(await _repository.listPassengerRides(limit: 80));
    } catch (error) {
      SLoggerHelper.error('Unable to refresh passenger trips', error);
      errorMessage.value = 'Unable to refresh trips.';
    } finally {
      isRefreshing.value = false;
    }
  }

  List<RideSummaryResponse> ridesFor(STripsFilter filter) {
    return switch (filter) {
      STripsFilter.ongoing => rides
          .where((ride) => ride.isOngoing && !ride.isScheduled)
          .toList(growable: false),
      STripsFilter.scheduled => rides
          .where(
            (ride) =>
                ride.isScheduled &&
                ride.status != RideStatus.completed &&
                ride.status != RideStatus.cancelled,
          )
          .toList(growable: false),
      STripsFilter.canceled => rides
          .where((ride) => ride.status == RideStatus.cancelled)
          .toList(growable: false),
      STripsFilter.completed => rides
          .where((ride) => ride.status == RideStatus.completed)
          .toList(growable: false),
    };
  }
}
