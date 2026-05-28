# Plan: Notification Inbox and Home Popup

## Scope
Build the notification inbox end to end using the existing notification microservice and connect it to the Flutter home app bar bell plus the existing Notifications screen.

## Backend
1. Extend `services/notification` domain models with notification type, title, metadata, source event fields, deeplink, read state, and idempotency key.
2. Add application schemas for:
   - send notification request
   - notification response
   - paginated/list response
   - unread count response
3. Add use cases for:
   - creating/sending notifications
   - listing current-user notifications
   - unread count
   - mark one read
   - mark all read
   - creating notifications from Kafka events
4. Add notification ORM and repository in infrastructure with user-scoped queries and idempotent creation.
5. Add API routes under `/api/v1/notification`:
   - `GET /notifications`
   - `GET /notifications/unread-count`
   - `POST /notifications/{notification_id}/read`
   - `POST /notifications/read-all`
6. Keep legacy `/api/v1/notifications` compatibility for existing service clients.
7. Add a Kafka consumer for ride, bidding, payment, communication, and geospatial topics.
8. Add migration `0016_notification_inbox` for the `notification.notifications` table and enums.
9. Import notification ORM models in Alembic env.
10. Update Docker Compose so the notification service depends on Postgres, Kafka, and migrations.
11. Ensure bidding `bid.placed` events include enough passenger identity for passenger offer notifications.

## Flutter
1. Add `SApiService.notification` and `SAFARPAY_NOTIFICATION_BASE_URL`.
2. Convert notification items from static UI-only data to backend-parsed models while preserving existing type/icon behavior.
3. Add a notifications repository for list, unread count, mark read, and mark all read.
4. Add a GetX notifications controller for inbox state.
5. Update the home app bar bell to:
   - load real unread count
   - hide badge at zero
   - open a notification bottom sheet
6. Add a professional bottom-sheet popup with preview items, empty/error/loading states, mark-all-read, and a button to open the full Notifications screen.
7. Update the full Notifications screen to use backend data while keeping filters, grouped timeline, pull-to-refresh, and empty/error states.

## Tests and Checks
1. Backend:
   - `uv run pytest tests\notification -q`
   - compile changed notification service modules
   - compile changed bidding use case module
2. Flutter:
   - notification model parsing test
   - `flutter analyze`
3. Restore generated Flutter plugin files if Flutter tooling dirties them.

## Rollout Notes
- Rebuild the notification service image.
- Run migrations before testing the app.
- Kafka must be running for cross-service event-generated notifications.
