import 'package:client/features/personalization/screens/help_support/screens/something_else/models/support_ticket_models.dart';
import 'package:client/features/personalization/screens/help_support/screens/something_else/something_else.dart';
import 'package:flutter/widgets.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:get/get.dart';

void main() {
  test('support ticket request serializes to backend contract', () {
    const request = SSupportTicketCreateRequest(
      description: 'The driver took the wrong route.',
      relatedRideId: 'ride-001',
      priority: SSupportTicketPriority.normal,
      attachments: [
        SSupportTicketAttachment(
          type: SSupportTicketAttachmentType.image,
          fileName: 'route.png',
          mimeType: 'image/png',
          sizeBytes: 1200,
        ),
      ],
    );

    expect(request.toJson(), {
      'description': 'The driver took the wrong route.',
      'related_ride_id': 'ride-001',
      'priority': 'NORMAL',
      'attachments': [
        {
          'type': 'IMAGE',
          'file_name': 'route.png',
          'mime_type': 'image/png',
          'size_bytes': 1200,
        },
      ],
    });
  });

  testWidgets('something else screen renders ticket form and attachment actions',
      (tester) async {
    await tester.pumpWidget(
      const GetMaterialApp(
        home: SomethingElseScreen(),
      ),
    );

    expect(find.text('Tell us more'), findsOneWidget);
    expect(find.text('Describe your issue'), findsOneWidget);
    expect(find.text('Select a related ride (optional)'), findsOneWidget);
    expect(find.text('Upload Image'), findsOneWidget);
    expect(find.text('Upload File'), findsOneWidget);
    expect(find.text('Record Audio'), findsOneWidget);
    expect(find.text('Submit Ticket'), findsOneWidget);
  });

  testWidgets('empty issue does not submit ticket', (tester) async {
    await tester.pumpWidget(
      const GetMaterialApp(
        home: SomethingElseScreen(),
      ),
    );

    await tester.ensureVisible(find.text('Submit Ticket'));
    await tester.tap(find.text('Submit Ticket'));
    await tester.pump();

    expect(find.text('Describe your issue to submit a ticket.'), findsOneWidget);
    expect(find.text('Ticket Created Successfully!'), findsNothing);
  });

  testWidgets('submitting issue opens ticket success screen', (tester) async {
    await tester.pumpWidget(
      const GetMaterialApp(
        home: SomethingElseScreen(),
      ),
    );

    await tester.enterText(find.byType(EditableText), 'I need help with a ride.');
    await tester.ensureVisible(find.text('Submit Ticket'));
    await tester.tap(find.text('Submit Ticket'));
    await tester.pumpAndSettle();

    expect(find.text('Ticket Created Successfully!'), findsOneWidget);
    expect(find.text('SUP-82571'), findsOneWidget);
    expect(find.text('Within 15 minutes'), findsOneWidget);
    expect(find.text('Go to My Tickets'), findsOneWidget);
    expect(find.text('Back to Home'), findsOneWidget);
  });
}
