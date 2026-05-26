import 'package:get/get.dart';

import '../data/driver_earnings_repository.dart';
import '../domain/earnings_models.dart';

class SEarningsController extends GetxController {
  SEarningsController({
    SDriverEarningsRepository repository = const SDriverEarningsRepository(),
  }) : _repository = repository;

  final SDriverEarningsRepository _repository;

  final Rx<SDriverEarningsPeriod> selectedPeriod =
      SDriverEarningsPeriod.today.obs;
  final Rxn<SDriverEarnings> earnings = Rxn<SDriverEarnings>();
  final RxBool isLoading = false.obs;
  final RxString errorMessage = ''.obs;

  @override
  void onInit() {
    super.onInit();
    loadEarnings();
  }

  Future<void> selectPeriod(SDriverEarningsPeriod period) async {
    if (period == selectedPeriod.value) return;
    selectedPeriod.value = period;
    await loadEarnings();
  }

  Future<void> loadEarnings() async {
    isLoading.value = true;
    errorMessage.value = '';
    try {
      earnings.value = await _repository.fetchEarnings(selectedPeriod.value);
    } catch (_) {
      errorMessage.value = 'Earnings are unavailable. Pull to refresh.';
    } finally {
      isLoading.value = false;
    }
  }
}
