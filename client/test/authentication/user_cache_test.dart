import 'dart:io';

import 'package:client/features/authentication/controllers/current_user_controller.dart';
import 'package:client/features/authentication/models/auth_models.dart';
import 'package:client/features/personalization/screens/profile/profile.dart';
import 'package:client/features/personalization/screens/settings/widgets/settings_profile_tile.dart';
import 'package:client/utils/local_storage/user_storage.dart';
import 'package:flutter/services.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:get/get.dart';
import 'package:get_storage/get_storage.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  setUpAll(() async {
    final tempDirectory = await Directory.systemTemp.createTemp('user-cache');
    TestDefaultBinaryMessengerBinding.instance.defaultBinaryMessenger
        .setMockMethodCallHandler(
      const MethodChannel('plugins.flutter.io/path_provider'),
      (call) async {
        if (call.method == 'getApplicationDocumentsDirectory') {
          return tempDirectory.path;
        }
        return null;
      },
    );
  });

  const cachedUser = SUserResponse(
    id: 'user-001',
    role: 'user',
    isActive: true,
    isVerified: true,
    isOnboarded: true,
    fullName: 'Ayesha Khan',
    email: 'ayesha@safarpay.com',
    phone: '+92 300 111 2222',
    gender: 'female',
    dateOfBirth: '1998-05-17',
    profileImage: null,
  );

  setUp(() async {
    Get.testMode = true;
    await GetStorage.init();
    await SUserStorage.clear();
    if (Get.isRegistered<SCurrentUserController>()) {
      await Get.delete<SCurrentUserController>(force: true);
    }
  });

  tearDown(() async {
    await SUserStorage.clear();
    if (Get.isRegistered<SCurrentUserController>()) {
      await Get.delete<SCurrentUserController>(force: true);
    }
  });

  test('user response serializes to local cache contract', () {
    final json = cachedUser.toJson();

    expect(json['id'], 'user-001');
    expect(json['role'], 'user');
    expect(json['is_active'], isTrue);
    expect(json['is_verified'], isTrue);
    expect(json['is_onboarded'], isTrue);
    expect(json['full_name'], 'Ayesha Khan');
    expect(json['email'], 'ayesha@safarpay.com');
    expect(json['phone'], '+92 300 111 2222');
    expect(json['gender'], 'female');
    expect(json['date_of_birth'], '1998-05-17');
    expect(json['profile_img'], isNull);

    final parsed = SUserResponse.fromJson(json);
    expect(parsed.fullName, 'Ayesha Khan');
    expect(parsed.gender, 'female');
    expect(parsed.dateOfBirth, '1998-05-17');
  });

  test('user storage saves reads and clears cached user', () async {
    await SUserStorage.saveUser(cachedUser);

    final user = SUserStorage.currentUser();
    expect(user?.id, 'user-001');
    expect(user?.email, 'ayesha@safarpay.com');
    expect(user?.gender, 'female');
    expect(user?.dateOfBirth, '1998-05-17');
    expect(SUserStorage.hasUser(), isTrue);

    await SUserStorage.clear();
    expect(SUserStorage.currentUser(), isNull);
    expect(SUserStorage.hasUser(), isFalse);
  });

  testWidgets('settings profile tile renders cached user', (tester) async {
    Get.put(SCurrentUserController(initialUser: cachedUser));

    await tester.pumpWidget(
      const GetMaterialApp(
        home: SSettingsProfileTile(),
      ),
    );

    expect(find.text('Ayesha Khan'), findsOneWidget);
    expect(find.text('ayesha@safarpay.com'), findsOneWidget);
    expect(find.text('John Doe'), findsNothing);
  });

  testWidgets('profile screen renders cached user fields', (tester) async {
    Get.put(SCurrentUserController(initialUser: cachedUser));

    await tester.pumpWidget(
      const GetMaterialApp(
        home: ProfileScreen(),
      ),
    );

    expect(find.text('Ayesha Khan'), findsOneWidget);
    expect(find.text('ayesha@safarpay.com'), findsOneWidget);
    expect(find.text('+92 300 111 2222'), findsOneWidget);
    expect(find.text('Female'), findsOneWidget);
    expect(find.text('1998-05-17'), findsOneWidget);
    expect(find.text('Coding with T'), findsNothing);
  });
}
