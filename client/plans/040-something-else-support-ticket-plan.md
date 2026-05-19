# Something Else Support Ticket Plan

## Goal

Build the Help Support `Something else` ticket creation flow with a reference-matched form, success state, typed models, and a future-ready `SHttpClient` repository.

## Implementation Steps

1. Add tests first.
   - Model serialization.
   - Form renders required fields and attachment actions.
   - Empty issue blocks submission.
   - Valid issue opens success screen with demo response.

2. Add models.
   - `SSupportTicketCreateRequest`
   - `SSupportTicketCreateResponse`
   - `SSupportTicketAttachment`
   - `SSupportTicketAttachmentType`
   - `SSupportTicketPriority`

3. Add repository.
   - `SSupportTicketRepository.createTicket`.
   - Keep real `SHttpClient.post('/support/tickets', service: SApiService.gateway, requiresAuth: true)` commented.
   - Return demo ticket response while backend is unavailable.

4. Add controller.
   - Own `TextEditingController`.
   - Track description, selected ride, attachments, loading, error.
   - Validate required description.
   - Submit through repository and navigate success on completion.

5. Build UI.
   - Replace placeholder form.
   - Add local widgets for issue field, related ride card, attachment tiles, submit button, success illustration, and ticket summary card.
   - Add success screen and local My Tickets screen.

6. Update docs.
   - `context/progress-tracker.md`
   - `context/project-overview.md`
   - `context/ui-context.md`

7. Verify.
   - `flutter test test/personalization/something_else_ticket_test.dart --no-pub`
   - `flutter analyze lib/features/personalization/screens/help_support/screens/something_else test/personalization/something_else_ticket_test.dart --no-pub`
   - Attempt `dart format`; report timeout if it persists.

## Acceptance Checks

- The form and success screen match the reference layout.
- API models use snake_case JSON.
- Demo submission works without backend.
- Tests and analyzer pass.
