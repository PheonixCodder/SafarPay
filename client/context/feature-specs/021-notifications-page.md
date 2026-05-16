# Prompt: Notifications Page

Create a professional Notifications page for the SafarPay Flutter client and open it from Settings.

## Goal

When the rider taps `Notifications` in `client/lib/features/personalization/screens/settings/settings.dart`, open a new notifications screen with the same right-slide transition used by Settings subpages.

## Requirements

- Read `client/AGENTS.md` and the context files before editing.
- Add the page under `client/lib/features/personalization/screens/notifications`.
- Use the approved Timeline Feed direction, not a boxy category-card grid.
- Keep demo notifications in a separate mapped content file.
- Add screen-local widgets under `notifications/widgets`.
- Follow the one-primary-widget-per-file pattern.
- Use `SAppBar`, `SRightSlidePageRoute`, `SColors`, `SSizes`, `SOpacities`, `SHelperFunctions`, `STexts`, and Iconsax.
- Match the existing Settings/Profile personalization visual language.
- Add local interactive filtering for common ride-hailing notification categories.
- Include demo notification types for trips, payments, offers, safety, and system/account updates.
- Do not add backend calls, push notification setup, or persisted read/unread state in this unit.
- Keep `User Info` and `Privacy & Security` navigation unchanged.
- Update context docs, the saved implementation plan, progress, and decision log.

## Acceptance Criteria

1. Tapping `Notifications` opens `NotificationsScreen`.
2. The page enters with `SRightSlidePageRoute` and back navigation returns to Settings.
3. Demo notification rows are rendered from typed mapped content.
4. Filter chips update the visible list locally.
5. Empty filtered states render without layout overflow.
6. The page uses a polished timeline feed design rather than heavy boxed category cards.
7. Other Settings rows do not accidentally navigate.
