import 'package:client/features/authentication/controllers/profile.dart';
import 'package:client/features/authentication/screens/profile/widgets/profile_form.dart';
import 'package:client/utils/constants/texts.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:get/get.dart';

void main() {
  testWidgets('complete profile form renders gender and date of birth inputs',
      (tester) async {
    final controller = SProfileController(registrationToken: 'registration');
    addTearDown(controller.dispose);

    await tester.pumpWidget(
      GetMaterialApp(
        home: Scaffold(
          body: SProfileForm(controller: controller),
        ),
      ),
    );

    expect(find.text(STexts.profileGender), findsOneWidget);
    expect(find.text(STexts.profileDateOfBirth), findsOneWidget);
    expect(find.text(STexts.profileGenderMale), findsOneWidget);
    expect(find.text(STexts.profileGenderFemale), findsOneWidget);
    expect(find.text(STexts.profileGenderOther), findsOneWidget);
  });
}
