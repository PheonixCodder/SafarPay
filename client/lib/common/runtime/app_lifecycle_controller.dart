import 'package:flutter/widgets.dart';
import 'package:get/get.dart';

class SAppLifecycleController extends GetxController
    with WidgetsBindingObserver {
  static SAppLifecycleController get instance {
    if (Get.isRegistered<SAppLifecycleController>()) {
      return Get.find<SAppLifecycleController>();
    }
    return Get.put(SAppLifecycleController());
  }

  final Rx<AppLifecycleState> state = AppLifecycleState.resumed.obs;

  bool get isResumed => state.value == AppLifecycleState.resumed;

  @override
  void onInit() {
    super.onInit();
    WidgetsBinding.instance.addObserver(this);
  }

  @override
  void didChangeAppLifecycleState(AppLifecycleState state) {
    this.state.value = state;
  }

  @override
  void onClose() {
    WidgetsBinding.instance.removeObserver(this);
    super.onClose();
  }

  @visibleForTesting
  void setStateForTest(AppLifecycleState state) {
    this.state.value = state;
  }
}
