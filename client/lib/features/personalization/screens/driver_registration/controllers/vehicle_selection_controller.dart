import 'package:get/get.dart';

import '../models/driver_registration_models.dart';
import '../repositories/driver_verification_repository.dart';

class SDriverVehicleSelectionController extends GetxController {
  SDriverVehicleSelectionController({
    required this.serviceType,
    SDriverVerificationRepository repository =
        const SDriverVerificationRepository(),
  }) : _repository = repository;

  final SVerificationServiceType serviceType;
  final SDriverVerificationRepository _repository;

  final RxBool isLoading = true.obs;
  final RxBool isAttachingService = false.obs;
  final RxnString errorMessage = RxnString();
  final Rxn<SDriverVehicleSummaryResponse> summary = Rxn();

  Future<void> loadSummary() async {
    isLoading.value = true;
    errorMessage.value = null;

    try {
      summary.value = await _repository.getVehicleSummary(
        serviceType: serviceType,
      );
    } catch (error) {
      errorMessage.value = error.toString();
    } finally {
      isLoading.value = false;
    }
  }

  SDriverVehicleSummaryItem? itemFor(SDriverVehicleOption vehicle) {
    final vehicleType = SVerificationVehicleType.fromDisplayVehicle(
      vehicle.type,
    );
    return summary.value?.itemFor(vehicleType);
  }

  bool isRegisteredForSelectedService(SDriverVehicleOption vehicle) {
    return itemFor(vehicle)?.isRegisteredForService ?? false;
  }

  Future<void> attachExistingVehicleIfNeeded(
    SDriverVehicleOption vehicle,
  ) async {
    final item = itemFor(vehicle);
    if (item == null ||
        item.vehicleId == null ||
        item.isRegisteredForService) {
      return;
    }

    isAttachingService.value = true;
    errorMessage.value = null;

    try {
      await _repository.attachVehicleToService(
        vehicleId: item.vehicleId!,
        serviceType: serviceType,
      );
      await loadSummary();
    } catch (error) {
      errorMessage.value = error.toString();
      rethrow;
    } finally {
      isAttachingService.value = false;
    }
  }
}
