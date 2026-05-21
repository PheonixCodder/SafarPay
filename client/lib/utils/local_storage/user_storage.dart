import '../../features/authentication/models/auth_models.dart';
import 'storage.dart';

class SUserStorage {
  SUserStorage._();

  static const String _userKey = 'current_user';

  static Future<void> saveUser(SUserResponse user) {
    return SLocalStorage().saveData(_userKey, user.toJson());
  }

  static SUserResponse? currentUser() {
    final data = SLocalStorage().readData<Map<String, dynamic>>(_userKey);
    if (data == null) return null;
    return SUserResponse.fromJson(data);
  }

  static bool hasUser() {
    return SLocalStorage().containsKey(_userKey);
  }

  static Future<void> clear() {
    return SLocalStorage().removeData(_userKey);
  }
}
