import '../constants/app_mode.dart';
import 'storage.dart';

class SAppModeStorage {
  SAppModeStorage._();

  static const String _modeKey = 'app_mode';

  static Future<void> saveMode(SAppMode mode) {
    return SLocalStorage().saveData(_modeKey, mode.value);
  }

  static SAppMode currentMode() {
    final value = SLocalStorage().readData<String>(_modeKey);
    return SAppModeX.fromValue(value);
  }

  static Future<void> clear() {
    return SLocalStorage().removeData(_modeKey);
  }
}
