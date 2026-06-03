import 'dart:async';
import 'package:client/common/widgets/maps/map_models.dart';
import 'package:client/common/widgets/maps/map_view.dart';
import 'package:client/features/location/controllers/ride_tracking_controller.dart';
import 'package:client/features/location/data/location_repository.dart';
import 'package:client/features/location/domain/location_models.dart';
import 'package:client/features/location/screens/ride_search/widgets/booking_search_results.dart';
import 'package:client/utils/constants/colors.dart';
import 'package:client/utils/constants/sizes.dart';
import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'package:iconsax/iconsax.dart';

class SRideDestinationEditController extends GetxController {
  SRideDestinationEditController({
    required this.trackingController,
    SLocationRepository locationRepository = const SLocationRepository(),
  }) : _locationRepository = locationRepository;

  final SRideTrackingController trackingController;
  final SLocationRepository _locationRepository;

  final SMapController mapController = SMapController();
  final TextEditingController searchController = TextEditingController();

  final RxList<SAddressResult> results = <SAddressResult>[].obs;
  final RxBool isLoading = false.obs;
  final RxBool isResolvingPin = false.obs;
  final RxString errorMessage = ''.obs;

  final Rxn<SAddressResult> selectedAddress = Rxn<SAddressResult>();
  final RxBool isSearchMode = false.obs;
  final Rxn<SCoordinate> mapCenterOverride = Rxn<SCoordinate>();

  Timer? _debounce;

  SCoordinate get mapCenter {
    return mapCenterOverride.value ??
        trackingController.routeDestination.value ??
        const SCoordinate(latitude: 31.5204, longitude: 74.3587);
  }

  @override
  void onInit() {
    super.onInit();
    final initialStop = trackingController.dropoffStop.value;
    if (initialStop != null) {
      selectedAddress.value = SAddressResult(
        formatted: initialStop.placeName ?? initialStop.addressLine1 ?? 'Destination',
        coordinate: SCoordinate(latitude: initialStop.latitude, longitude: initialStop.longitude),
      );
      searchController.text = selectedAddress.value?.formatted ?? '';
    }
  }

  @override
  void onClose() {
    _debounce?.cancel();
    searchController.dispose();
    super.onClose();
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
      final matches = await _locationRepository.searchPlaces(
        trimmed,
        proximity: mapCenter,
      );
      results.assignAll(matches);
      if (results.isEmpty) errorMessage.value = 'No matching places found.';
    } catch (_) {
      errorMessage.value = 'Search is unavailable. Try again.';
    } finally {
      isLoading.value = false;
    }
  }

  void selectAddress(SAddressResult address) {
    selectedAddress.value = address;
    searchController.text = address.formatted;
    results.clear();
    isSearchMode.value = false;
    mapCenterOverride.value = address.coordinate;
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
      selectedAddress.value = address;
      searchController.text = address.formatted;
      isSearchMode.value = false;
    } catch (_) {
      errorMessage.value = 'Unable to read this map location.';
    } finally {
      isResolvingPin.value = false;
    }
  }
}

class RideDestinationEditScreen extends StatelessWidget {
  const RideDestinationEditScreen({
    super.key,
    required this.trackingController,
  });

  final SRideTrackingController trackingController;

  @override
  Widget build(BuildContext context) {
    final controller = Get.put(
      SRideDestinationEditController(trackingController: trackingController),
    );

    return Scaffold(
      backgroundColor: SColors.primaryBackground,
      resizeToAvoidBottomInset: false,
      body: Stack(
        children: [
          // Map Background
          Positioned.fill(
            child: Obx(
              () => SMapView(
                controller: controller.mapController,
                initialCenter: controller.mapCenter,
                cameraMode: SMapCameraMode.manual,
                showCenterPin: true,
                showUserLocation: false,
                isLoading: controller.isResolvingPin.value,
              ),
            ),
          ),

          // Top Header & Search Panel
          Positioned(
            top: 0,
            left: 0,
            right: 0,
            child: SafeArea(
              child: Padding(
                padding: const EdgeInsets.all(SSizes.md),
                child: Column(
                  children: [
                    Row(
                      children: [
                        DecoratedBox(
                          decoration: BoxDecoration(
                            color: SColors.white,
                            borderRadius: BorderRadius.circular(SSizes.radiusFull),
                            boxShadow: [
                              BoxShadow(
                                color: SColors.pureBlack.withOpacity(0.08),
                                blurRadius: 8,
                                offset: const Offset(0, 4),
                              ),
                            ],
                          ),
                          child: IconButton(
                            icon: const Icon(Iconsax.arrow_left, color: SColors.textPrimary),
                            onPressed: () => Get.back(),
                          ),
                        ),
                        const SizedBox(width: SSizes.md),
                        Expanded(
                          child: Container(
                            decoration: BoxDecoration(
                              color: SColors.white,
                              borderRadius: BorderRadius.circular(SSizes.inputFieldRadius),
                              boxShadow: [
                                BoxShadow(
                                  color: SColors.pureBlack.withOpacity(0.08),
                                  blurRadius: 8,
                                  offset: const Offset(0, 4),
                                ),
                              ],
                            ),
                            child: TextField(
                              controller: controller.searchController,
                              textInputAction: TextInputAction.search,
                              onChanged: controller.onSearchChanged,
                              onTap: () => controller.isSearchMode.value = true,
                              decoration: InputDecoration(
                                hintText: 'Search new destination',
                                prefixIcon: const Icon(Iconsax.flag, color: SColors.primary),
                                suffixIcon: Obx(
                                  () => controller.searchController.text.isNotEmpty
                                      ? IconButton(
                                          icon: const Icon(Iconsax.close_circle, color: SColors.secondary),
                                          onPressed: () {
                                            controller.searchController.clear();
                                            controller.results.clear();
                                          },
                                        )
                                      : const SizedBox.shrink(),
                                ),
                                border: InputBorder.none,
                                enabledBorder: InputBorder.none,
                                focusedBorder: InputBorder.none,
                                contentPadding: const EdgeInsets.symmetric(
                                  horizontal: SSizes.md,
                                  vertical: SSizes.sm + 4,
                                ),
                              ),
                            ),
                          ),
                        ),
                      ],
                    ),
                    Obx(() {
                      if (!controller.isSearchMode.value) return const SizedBox.shrink();
                      return Container(
                        margin: const EdgeInsets.only(top: SSizes.sm),
                        padding: const EdgeInsets.all(SSizes.md),
                        constraints: const BoxConstraints(maxHeight: 300),
                        decoration: BoxDecoration(
                          color: SColors.white,
                          borderRadius: BorderRadius.circular(SSizes.cardRadiusLg),
                          boxShadow: [
                            BoxShadow(
                              color: SColors.pureBlack.withOpacity(0.08),
                              blurRadius: 8,
                              offset: const Offset(0, 4),
                            ),
                          ],
                        ),
                        child: SBookingSearchResults(
                          isLoading: controller.isLoading.value,
                          errorMessage: controller.errorMessage.value,
                          results: controller.results,
                          onSelected: controller.selectAddress,
                        ),
                      );
                    }),
                  ],
                ),
              ),
            ),
          ),

          // Map Geocoding Check Button (Recenter/Verify Pin)
          Positioned(
            right: SSizes.md,
            bottom: 180,
            child: Obx(
              () => Container(
                decoration: BoxDecoration(
                  color: SColors.white,
                  borderRadius: BorderRadius.circular(SSizes.radiusFull),
                  boxShadow: [
                    BoxShadow(
                      color: SColors.pureBlack.withOpacity(0.12),
                      blurRadius: 8,
                      offset: const Offset(0, 4),
                    ),
                  ],
                ),
                child: FloatingActionButton(
                  onPressed: controller.confirmMapPin,
                  backgroundColor: SColors.surfaceContainer,
                  child: controller.isResolvingPin.value
                      ? const SizedBox(
                          width: SSizes.iconMd,
                          height: SSizes.iconMd,
                          child: CircularProgressIndicator(strokeWidth: 2.5),
                        )
                      : const Icon(Iconsax.gps, color: SColors.primary),
                ),
              ),
            ),
          ),

          // Bottom Confirmation Panel
          Positioned(
            bottom: 0,
            left: 0,
            right: 0,
            child: Container(
              padding: const EdgeInsets.all(SSizes.defaultSpace),
              decoration: const BoxDecoration(
                color: SColors.white,
                borderRadius: BorderRadius.vertical(top: Radius.circular(SSizes.rideSheetRadius)),
                boxShadow: [
                  BoxShadow(
                    color: SColors.borderPrimary,
                    blurRadius: 16,
                    spreadRadius: 1,
                  ),
                ],
              ),
              child: SafeArea(
                top: false,
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Confirm new destination',
                      style: Theme.of(context).textTheme.titleMedium?.copyWith(
                            fontWeight: FontWeight.w800,
                            color: SColors.textPrimary,
                          ),
                    ),
                    const SizedBox(height: SSizes.sm),
                    Obx(
                      () => Text(
                        controller.selectedAddress.value?.formatted ??
                            'Drag map to pick coordinates',
                        style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                              color: SColors.textSecondary,
                            ),
                        maxLines: 2,
                        overflow: TextOverflow.ellipsis,
                      ),
                    ),
                    const SizedBox(height: SSizes.md),
                    SizedBox(
                      width: double.infinity,
                      child: Obx(
                        () => ElevatedButton(
                          onPressed: controller.selectedAddress.value != null &&
                                  !controller.isResolvingPin.value
                              ? () {
                                  trackingController.updateRideDestination(
                                    controller.selectedAddress.value!,
                                  );
                                  Get.back();
                                }
                              : null,
                          child: const Text('Update Destination'),
                        ),
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }
}
