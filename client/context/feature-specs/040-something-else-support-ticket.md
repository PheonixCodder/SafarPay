# Something Else Support Ticket Prompt

Create the Help Support `Something else` page to match the provided reference image.

## Entry Point

- The page is opened from `client/lib/features/personalization/screens/help_support/help_support.dart` through the existing Help & Support option list.
- Target screen:
  - `client/lib/features/personalization/screens/help_support/screens/something_else/something_else.dart`

## Required UI

- Use the existing shared app bar:
  - `client/lib/common/widgets/appbar/appbar.dart`
- Match the reference below the app bar:
  - `Tell us more` title
  - helper text: `Please provide more details about your issue.`
  - required issue textarea with counter
  - optional related ride card
  - optional attachment tiles:
    - Upload Image
    - Upload File
    - Record Audio
  - full-width `Submit Ticket` button
- On success, show a ticket-created screen:
  - success illustration
  - `Ticket Created Successfully!`
  - helper text
  - card with ticket id and expected response
  - `Go to My Tickets`
  - `Back to Home`

## API Layer

- Create a repository using `client/lib/utils/http/client.dart`.
- Use typed request and response models under:
  - `client/lib/features/personalization/screens/help_support/screens/something_else/models`
- Backend will be created later, so keep the real call in place and use a demo response for now.
- Future backend contract:
  - `POST /support/tickets`
  - service: `SApiService.gateway`
  - auth required
  - request body:
    - `description`
    - `related_ride_id`
    - `priority`
    - `attachments`
  - response body:
    - `ticket_id`
    - `status`
    - `expected_response_minutes`
    - `message`

## Constraints

- Use existing colors and sizing tokens.
- Follow the existing feature folder structure.
- Keep each file focused on one primary widget.
- Do not introduce backend assumptions beyond the explicit request/response contract.
- No raw `Colors.*` in touched UI files.

## Acceptance Criteria

- The placeholder `SomethingElseScreen` is replaced.
- Submitting an empty issue shows validation.
- Submitting valid text shows the success screen with demo ticket `SUP-82571`.
- Attachment tiles render and update UI state when used.
- Repository has a real `SHttpClient.post` call commented in place and a demo response active.
- Targeted tests and analyzer pass.
