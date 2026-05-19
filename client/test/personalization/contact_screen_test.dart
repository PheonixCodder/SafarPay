import 'package:client/features/personalization/screens/help_support/screens/contact/contact.dart';
import 'package:client/utils/constants/texts.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:get/get.dart';

void main() {
  test('contact constants expose support phone and email', () {
    expect(STexts.contactSupportPhone, '+92 317 805 9528');
    expect(STexts.contactSupportEmail, 'support@safarpay.com');
  });

  testWidgets('contact screen renders action cards and social links',
      (tester) async {
    await tester.pumpWidget(
      const GetMaterialApp(
        home: ContactScreen(),
      ),
    );

    expect(find.text("Let's get in touch!"), findsOneWidget);
    expect(find.text('Call Us'), findsOneWidget);
    expect(find.text('Email Us'), findsOneWidget);
    expect(find.text('Chat'), findsOneWidget);
    expect(find.text('Our social media'), findsOneWidget);
    expect(find.text('Twitter'), findsOneWidget);
    expect(find.text('Instagram'), findsOneWidget);
    expect(find.text('Facebook'), findsOneWidget);
    expect(find.text('Linked In'), findsOneWidget);
    expect(find.text('Medium'), findsOneWidget);
  });
}
