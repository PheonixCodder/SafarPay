import 'package:client/features/personalization/screens/help_support/screens/faqs/data/faqs_data.dart';
import 'package:client/features/personalization/screens/help_support/screens/faqs/faqs.dart';
import 'package:flutter/widgets.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:get/get.dart';

void main() {
  test('faq data includes categories and popular articles', () {
    final categories = SFaqsData.categories;
    final popularArticles = SFaqsData.popularArticles;

    expect(categories, hasLength(6));
    expect(
      categories.map((category) => category.title),
      containsAll(
        const [
          'Rider',
          'Payments',
          'Safety',
          'Account',
          'Technical',
          'Driver',
        ],
      ),
    );
    expect(popularArticles, hasLength(6));
    expect(
      popularArticles.map((article) => article.title),
      contains('How do refunds work?'),
    );

    final refundArticle = SFaqsData.articleById('refunds-work');
    expect(refundArticle.bullets, contains('Driver canceled the ride'));
    expect(refundArticle.relatedArticleIds, contains('cancel-ride'));
  });

  testWidgets('faq screen renders categories and popular articles',
      (tester) async {
    await tester.pumpWidget(
      const GetMaterialApp(
        home: FaqsScreen(),
      ),
    );

    expect(find.text("FAQ's"), findsOneWidget);
    expect(find.text('Search help articles...'), findsOneWidget);
    expect(find.text('Categories'), findsOneWidget);
    expect(find.text('Rider'), findsOneWidget);
    expect(find.text('Popular Articles'), findsOneWidget);
    expect(find.text('How do refunds work?'), findsOneWidget);
    expect(find.text('View All Articles'), findsNothing);
  });

  testWidgets('search filters local faq articles', (tester) async {
    await tester.pumpWidget(
      const GetMaterialApp(
        home: FaqsScreen(),
      ),
    );

    await tester.enterText(find.byType(EditableText), 'refund');
    await tester.pump();

    expect(find.text('Search Results'), findsOneWidget);
    expect(find.text('How do refunds work?'), findsOneWidget);
    expect(find.text('I lost an item in the ride'), findsNothing);
  });

  testWidgets('category tap filters articles for that category', (tester) async {
    await tester.pumpWidget(
      const GetMaterialApp(
        home: FaqsScreen(),
      ),
    );

    await tester.tap(find.text('Payments'));
    await tester.pump();

    expect(find.text('Payments Articles'), findsOneWidget);
    expect(find.text('How do refunds work?'), findsOneWidget);
    expect(find.text('What is a cancellation fee?'), findsOneWidget);
    expect(find.text('I lost an item in the ride'), findsNothing);
  });

  testWidgets('tapping refund article opens detail page', (tester) async {
    await tester.pumpWidget(
      const GetMaterialApp(
        home: FaqsScreen(),
      ),
    );

    await tester.ensureVisible(find.text('How do refunds work?'));
    await tester.tap(find.text('How do refunds work?'));
    await tester.pumpAndSettle();

    expect(find.text('How do refunds work?'), findsOneWidget);
    expect(find.text('When am I eligible for a refund?'), findsOneWidget);
    expect(find.text('Refund Timelines'), findsOneWidget);
    expect(find.text('Was this article helpful?'), findsOneWidget);
    expect(find.text('Related Articles'), findsOneWidget);
  });
}
