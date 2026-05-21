import 'package:get/get.dart';

import '../../../utils/local_storage/user_storage.dart';
import '../models/auth_models.dart';
import '../repositories/auth_repository.dart';

class SCurrentUserController extends GetxController {
  SCurrentUserController({SUserResponse? initialUser})
      : currentUser = Rxn<SUserResponse>(initialUser);

  static SCurrentUserController get instance {
    if (Get.isRegistered<SCurrentUserController>()) {
      return Get.find<SCurrentUserController>();
    }
    return Get.put(SCurrentUserController());
  }

  final Rxn<SUserResponse> currentUser;

  @override
  void onInit() {
    super.onInit();
    currentUser.value ??= SUserStorage.currentUser();
  }

  Future<SUserResponse> refreshFromBackend() async {
    final user = await SAuthRepository.instance.getCurrentUser();
    await cacheUser(user);
    return user;
  }

  Future<void> cacheUser(SUserResponse user) async {
    await SUserStorage.saveUser(user);
    currentUser.value = user;
  }

  Future<void> updateCachedUser({
    String? fullName,
    String? email,
    String? phone,
    String? gender,
    String? dateOfBirth,
    String? profileImage,
  }) async {
    final existing = currentUser.value ?? SUserStorage.currentUser();
    if (existing == null) return;

    await cacheUser(
      existing.copyWith(
        fullName: fullName,
        email: email,
        phone: phone,
        gender: gender,
        dateOfBirth: dateOfBirth,
        profileImage: profileImage,
      ),
    );
  }

  Future<void> clear() async {
    currentUser.value = null;
    await SUserStorage.clear();
  }
}
