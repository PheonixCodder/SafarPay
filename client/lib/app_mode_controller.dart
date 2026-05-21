import 'package:get/get.dart';

import 'features/authentication/controllers/current_user_controller.dart';
import 'features/authentication/models/auth_models.dart';
import 'utils/constants/app_mode.dart';
import 'utils/local_storage/app_mode_storage.dart';

class SAppModeController extends GetxController {
  static SAppModeController get instance {
    if (Get.isRegistered<SAppModeController>()) {
      return Get.find<SAppModeController>();
    }
    return Get.put(SAppModeController());
  }

  final Rx<SAppMode> currentMode = SAppMode.passenger.obs;

  bool get isDriverMode => currentMode.value == SAppMode.driver;

  bool get canUseDriverMode {
    final user = SCurrentUserController.instance.currentUser.value;
    return _hasDriverCapability(user);
  }

  @override
  void onInit() {
    super.onInit();
    currentMode.value = SAppModeStorage.currentMode();
    _enforceDriverAccess();
    ever<SUserResponse?>(
      SCurrentUserController.instance.currentUser,
      (_) => _enforceDriverAccess(),
    );
  }

  Future<void> switchToDriverMode() async {
    if (!canUseDriverMode) {
      await switchToPassengerMode();
      return;
    }
    await _setMode(SAppMode.driver);
  }

  Future<void> switchToPassengerMode() {
    return _setMode(SAppMode.passenger);
  }

  Future<void> toggleMode() {
    if (isDriverMode) return switchToPassengerMode();
    return switchToDriverMode();
  }

  Future<void> resetToPassengerMode() {
    return switchToPassengerMode();
  }

  Future<void> _setMode(SAppMode mode) async {
    currentMode.value = mode;
    await SAppModeStorage.saveMode(mode);
  }

  void _enforceDriverAccess() {
    if (currentMode.value == SAppMode.driver && !canUseDriverMode) {
      currentMode.value = SAppMode.passenger;
      SAppModeStorage.saveMode(SAppMode.passenger);
    }
  }

  bool _hasDriverCapability(SUserResponse? user) {
    final role = user?.role.toLowerCase();
    return role == 'driver' || role == 'admin';
  }
}
