import 'package:client/features/personalization/screens/help_support/screens/terms_conditions/data/terms_conditions_data.dart';
import 'package:client/features/personalization/screens/help_support/screens/terms_conditions/terms_conditions.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:get/get.dart';

void main() {
  test('terms data includes all policy categories and rider sections', () {
    final policies = STermsConditionsData.policies;

    expect(policies, hasLength(6));
    expect(
      policies.map((policy) => policy.title),
      containsAll(
        const [
          'Rider Terms of Service',
          'Driver Terms of Service',
          'Privacy Policy',
          'Refund Policy',
          'Community Guidelines',
          'Safety & Liability',
        ],
      ),
    );

    final riderTerms = STermsConditionsData.policyById('rider-terms');

    expect(riderTerms.lastUpdated, 'May 15, 2024');
    expect(riderTerms.sections, hasLength(7));
    expect(riderTerms.sections.first.title, 'Acceptance of Terms');
  });

  testWidgets('terms screen renders policy list and last updated label',
      (tester) async {
    await tester.pumpWidget(
      const GetMaterialApp(
        home: TermsConditionsScreen(),
      ),
    );

    expect(find.text('Terms & Conditions'), findsOneWidget);
    expect(find.text('Rider Terms of Service'), findsOneWidget);
    expect(find.text('Driver Terms of Service'), findsOneWidget);
    expect(find.text('Privacy Policy'), findsOneWidget);
    expect(find.text('Last Updated: May 15, 2024'), findsOneWidget);
  });

  testWidgets('tapping rider terms opens its detail sections', (tester) async {
    await tester.pumpWidget(
      const GetMaterialApp(
        home: TermsConditionsScreen(),
      ),
    );

    await tester.tap(find.text('Rider Terms of Service'));
    await tester.pumpAndSettle();

    expect(find.text('Rider Terms of Service'), findsOneWidget);
    expect(find.text('1. Acceptance of Terms'), findsOneWidget);
    expect(find.text('7. Limitation of Liability'), findsOneWidget);
  });
}
