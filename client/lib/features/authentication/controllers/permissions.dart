import 'package:get/get.dart';
import 'package:permission_handler/permission_handler.dart';

import '../../home/screens/home.dart';
import '../../../utils/constants/texts.dart';
import '../../../utils/helpers/helpers.dart';
import '../../../utils/local_storage/storage.dart';
import '../utils/auth_navigation.dart';

enum SPermissionStep {
  location,
  notification,
}

class SPermissionsController extends GetxController {
  static const String _permissionsCompletedKey = 'permissions_completed';

  final Rx<SPermissionStep> currentStep = SPermissionStep.location.obs;
  final RxBool isRequesting = false.obs;

  @override
  void onInit() {
    super.onInit();
    checkInitialPermissions();
  }

  Future<void> checkInitialPermissions() async {
    if (await hasCompletedPermissions()) {
      await completePermissions();
      return;
    }

    final locationAccepted =
        await SPermissionsController.hasLocationPermission();
    if (!locationAccepted) {
      currentStep.value = SPermissionStep.location;
      return;
    }

    currentStep.value = SPermissionStep.notification;
  }

  Future<void> requestLocationPermission() async {
    if (isRequesting.value) return;

    isRequesting.value = true;
    try {
      final status = await Permission.locationWhenInUse.request();
      final hasLocationPermission =
          await SPermissionsController.hasLocationPermission();

      if (hasLocationPermission) {
        currentStep.value = SPermissionStep.notification;
      } else if (status.isPermanentlyDenied ||
          await _isLocationPermanentlyDenied()) {
        await _openPermissionSettings();
      } else {
        SHelperFunctions.showSnackBar(STexts.permissionDenied);
      }
    } finally {
      isRequesting.value = false;
    }
  }

  Future<void> requestNotificationPermission() async {
    if (isRequesting.value) return;

    isRequesting.value = true;
    try {
      final status = await Permission.notification.request();
      final hasNotificationPermission =
          await SPermissionsController.hasNotificationPermission();

      if (hasNotificationPermission) {
        await completePermissions();
      } else if (status.isPermanentlyDenied) {
        await _openPermissionSettings();
      } else {
        SHelperFunctions.showSnackBar(STexts.permissionDenied);
      }
    } finally {
      isRequesting.value = false;
    }
  }

  Future<void> completePermissions() async {
    await SLocalStorage().saveData(_permissionsCompletedKey, true);
    SHelperFunctions.showSnackBar(STexts.permissionsCompleted);
    SAuthNavigation.offAll(const HomeScreen());
  }

  static Future<bool> hasRequiredPermissions() async {
    return hasCompletedPermissions();
  }

  static Future<bool> hasCompletedPermissions() async {
    final permissionsCompleted =
        SLocalStorage().readData<bool>(_permissionsCompletedKey) ?? false;
    if (!permissionsCompleted) return false;

    return hasLocationPermission();
  }

  static Future<bool> hasLocationPermission() async {
    final locationWhenInUseStatus = await Permission.locationWhenInUse.status;
    if (locationWhenInUseStatus.isGranted) return true;

    final locationStatus = await Permission.location.status;
    return locationStatus.isGranted;
  }

  static Future<bool> hasNotificationPermission() async {
    final notificationStatus = await Permission.notification.status;
    return notificationStatus.isGranted;
  }

  Future<bool> _isLocationPermanentlyDenied() async {
    final locationWhenInUseStatus = await Permission.locationWhenInUse.status;
    final locationStatus = await Permission.location.status;

    return locationWhenInUseStatus.isPermanentlyDenied ||
        locationStatus.isPermanentlyDenied;
  }

  Future<void> _openPermissionSettings() async {
    SHelperFunctions.showSnackBar(STexts.permissionDenied);
    await openAppSettings();
  }
}
