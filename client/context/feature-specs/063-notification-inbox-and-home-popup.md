# Feature Prompt: Notification Inbox and Home Popup

## Goal
Implement a real notification inbox for SafarPay using the existing `services/notification` microservice, then connect it to the passenger home app bar bell button and the existing Notifications screen.

## User Request
When the notification bell in `client/lib/features/home/screens/home/widgets/appbar.dart` is tapped, show a professional notification popup instead of a no-op. Search the backend first and use the existing notification service if present. If no service exists, identify whether a new service is needed. Integrate notifications across services using Kafka and the shared `libs/platform` infrastructure.

## Required Behavior
- Use the existing `services/notification` service.
- Persist notifications in the database so users have an inbox, unread count, read state, and history.
- Add APIs for listing notifications, unread count, marking a single notification read, and marking all as read.
- Consume relevant Kafka events from ride, bidding, communication, payment, and geospatial flows to create user-facing inbox records.
- Keep the notification service aligned with the clean architecture pattern used by the other services:
  - domain models stay pure
  - use cases own business behavior
  - infrastructure owns ORM, repositories, Kafka, and dependencies
  - routers stay thin
- Add the notification schema/table through Alembic migrations.
- Update Docker Compose so notification service has Postgres, Kafka, migration dependency, JWT config, and healthcheck.
- In Flutter:
  - add notification service API base URL
  - load unread count for the home bell
  - open a bottom-sheet notification popup from the bell
  - hide the badge when unread count is zero
  - replace static notification screen data with backend data
  - support loading, empty, error, retry, mark read, and mark all read states.

## Design Notes
- The popup should be compact, bottom-sheet based, and show the latest few notifications with a path to the full Notifications screen.
- The full Notifications screen should reuse the current filtering and timeline design, but use real API-backed data.
- Notification types should map to the existing client categories: trip, payment, offer, safety, and system.
- Events should be idempotent so repeated Kafka delivery does not duplicate inbox items.

## Verification
- Add backend tests for notification use cases and route scoping.
- Add a Flutter test for parsing backend notification payloads.
- Run focused backend tests, Flutter test, Python compile checks, and Flutter analysis.
