import 'dart:io';

import 'package:client/common/widgets/drawers/edit_value_drawer.dart';
import 'package:client/features/authentication/controllers/current_user_controller.dart';
import 'package:client/features/authentication/models/auth_models.dart';
import 'package:client/features/personalization/screens/profile/profile.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:get/get.dart';
import 'package:get_storage/get_storage.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  setUpAll(() async {
    final tempDirectory = await Directory.systemTemp.createTemp(
      'profile-edit-popup',
    );
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

  setUp(() async {
    Get.testMode = true;
    await GetStorage.init();
    if (Get.isRegistered<SCurrentUserController>()) {
      await Get.delete<SCurrentUserController>(force: true);
    }
  });

  tearDown(() async {
    if (Get.isRegistered<SCurrentUserController>()) {
      await Get.delete<SCurrentUserController>(force: true);
    }
  });

  testWidgets('edit value helper opens a confirm cancel popup', (tester) async {
    String? savedValue;

    await tester.pumpWidget(
      MaterialApp(
        home: Builder(
          builder: (context) => Scaffold(
            body: TextButton(
              onPressed: () => showSEditValueDrawer(
                context: context,
                title: 'Edit Name',
                fieldLabel: 'Name',
                currentValue: 'Ayesha Khan',
                onSave: (value) => savedValue = value,
              ),
              child: const Text('Open'),
            ),
          ),
        ),
      ),
    );

    await tester.tap(find.text('Open'));
    await tester.pumpAndSettle();

    expect(find.byType(AlertDialog), findsOneWidget);
    expect(find.text('Edit Name'), findsOneWidget);
    expect(find.text('Cancel'), findsOneWidget);
    expect(find.text('Confirm'), findsOneWidget);

    await tester.enterText(find.byType(TextFormField), 'New Name');
    await tester.tap(find.text('Confirm'));
    await tester.pumpAndSettle();

    expect(savedValue, 'New Name');
    expect(find.byType(AlertDialog), findsNothing);
  });

  testWidgets('edit value popup validates before confirming', (tester) async {
    var didSave = false;

    await tester.pumpWidget(
      MaterialApp(
        home: Builder(
          builder: (context) => Scaffold(
            body: TextButton(
              onPressed: () => showSEditValueDrawer(
                context: context,
                title: 'Edit Email',
                fieldLabel: 'Email',
                currentValue: 'bad',
                validator: (_) => 'Invalid email',
                onSave: (_) => didSave = true,
              ),
              child: const Text('Open'),
            ),
          ),
        ),
      ),
    );

    await tester.tap(find.text('Open'));
    await tester.pumpAndSettle();
    await tester.tap(find.text('Confirm'));
    await tester.pumpAndSettle();

    expect(didSave, isFalse);
    expect(find.text('Invalid email'), findsOneWidget);
    expect(find.byType(AlertDialog), findsOneWidget);
  });

  testWidgets('profile date of birth edit opens date picker', (tester) async {
    Get.put(
      SCurrentUserController(
        initialUser: SUserResponse(
          id: 'user-001',
          role: 'user',
          isActive: true,
          isVerified: true,
          isOnboarded: true,
          fullName: 'Ayesha Khan',
          email: 'ayesha@safarpay.com',
          phone: '+923001112222',
          gender: 'female',
          dateOfBirth: '1998-05-17',
        ),
      ),
    );

    await tester.pumpWidget(
      const GetMaterialApp(
        home: ProfileScreen(),
      ),
    );

    final dateOfBirthMenu =
        find.byKey(const ValueKey('profile-date-of-birth-menu'));
    final dateOfBirthAction = find.descendant(
      of: dateOfBirthMenu,
      matching: find.byType(InkWell),
    );

    await tester.ensureVisible(dateOfBirthMenu);
    await tester.pumpAndSettle();
    await tester.tap(dateOfBirthAction);
    await tester.pumpAndSettle();

    expect(find.byType(DatePickerDialog), findsOneWidget);
  });
}
