# Foreground Overlay Suppression Plan (078)

## Plan

1. **Verify Files**: Identify the exact location of `_showForegroundNotification` in `client/lib/features/personalization/screens/notifications/controllers/push_notification_controller.dart`.
2. **Implement Check**:
   - Add a check for `Get.isRegistered<SDriverRequestsController>()` inside `_showForegroundNotification` where the kind is `SNotificationRouteKind.driverRequests`.
   - If true, early return to suppress both the native overlay and the local notification alert.
3. **Execute & Safety Check**: Save the code and ensure it builds correctly.
