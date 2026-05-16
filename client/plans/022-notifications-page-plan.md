# Notifications Page Plan

## Summary

Add a Settings subpage for Notifications using the approved timeline feed direction. The page opens from the Settings `Notifications` row, renders typed demo notifications from mapped data, and supports local category filtering.

## Implementation

- Create `NotificationsScreen` under `features/personalization/screens/notifications`.
- Store demo notifications in typed mapped content with `SNotificationItem`, `SNotificationType`, and `SNotificationsContent`.
- Build focused screen-local widgets:
  - `SNotificationsHeader` for the summary count and accent icon.
  - `SNotificationFilterChips` for local category filtering.
  - `SNotificationSectionLabel` for grouped date labels.
  - `SNotificationTimelineItem` for compact timeline rows.
  - `SNotificationsEmptyState` for filters without items.
- Wire `SettingsScreen` so only the account-settings `Notifications` row opens `NotificationsScreen` with `SRightSlidePageRoute`.
- Add reusable labels to `STexts` and notification dimensions to `SSizes`.
- Update `client/AGENTS.md`, context docs, progress, and decision log.

## Verification

- Run `dart format` on touched Dart files.
- Run targeted `dart analyze` on notifications, settings, and touched constants.
- Attempt `flutter analyze --no-pub` when tooling responds.
- Verify Settings `Notifications` opens the new page and back returns to Settings.
- Verify `User Info` and `Privacy & Security` still open their existing pages.
- Search touched Dart files for raw `Colors.*`, stale `T*` names, and hard-coded asset paths.

## Assumptions

- Demo notifications are local-only placeholders.
- No backend persistence, push notification registration, or read/unread mutation is introduced in this unit.
