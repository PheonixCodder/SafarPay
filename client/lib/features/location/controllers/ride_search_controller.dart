import 'dart:async';

import 'package:flutter/material.dart';
import 'package:get/get.dart';

import '../../../utils/helpers/helpers.dart';
import '../data/device_location_service.dart';
import '../data/location_repository.dart';
import '../domain/location_models.dart';

class SRideSearchController extends GetxController {
  SRideSearchController({
    SLocationRepository locationRepository = const SLocationRepository(),
    SDeviceLocationService deviceLocationService =
        const SDeviceLocationService(),
  })  : _locationRepository = locationRepository,
        _deviceLocationService = deviceLocationService;

  final SLocationRepository _locationRepository;
  final SDeviceLocationService _deviceLocationService;

  final TextEditingController queryController = TextEditingController();
  final RxBool isLoading = false.obs;
  final RxString errorMessage = ''.obs;
  final Rxn<SAddressResult> pickup = Rxn<SAddressResult>();
  final Rxn<SAddressResult> selectedDropoff = Rxn<SAddressResult>();
  final RxList<SAddressResult> results = <SAddressResult>[].obs;

  Timer? _debounce;

  @override
  void onInit() {
    super.onInit();
    loadCurrentPickup();
  }

  @override
  void onClose() {
    _debounce?.cancel();
    queryController.dispose();
    super.onClose();
  }

  Future<void> loadCurrentPickup() async {
    try {
      final coordinate = await _deviceLocationService.currentCoordinate();
      pickup.value = await _locationRepository.reverseGeocode(coordinate);
    } catch (error) {
      errorMessage.value = 'Use search to set your pickup.';
    }
  }

  void onQueryChanged(String value) {
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
    } catch (error) {
      errorMessage.value = 'Search is unavailable. Try again.';
    } finally {
      isLoading.value = false;
    }
  }

  void selectDropoff(SAddressResult result) {
    selectedDropoff.value = result;
    SHelperFunctions.showSnackBar('Dropoff selected.');
  }
}
