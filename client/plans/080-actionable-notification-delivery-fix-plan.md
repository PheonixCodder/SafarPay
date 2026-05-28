# Actionable Notification Delivery Fix Plan (080)

## Plan

1. **Verify Backend Logic**: Inspect `push_client.py` in the notification service.
2. **Implement Fix**:
   - Refactor `_is_actionable_notification(notification)` in `services/notification/notification/infrastructure/push_client.py` so that it returns `True` **only** for `driver_ride_request` (using `_is_driver_ride_request(notification)`).
   - This keeps the visual `"notification"` payload block intact for `communication_call` and `communication_message` so the Android/iOS OS automatically displays the alert tray notification even if the app is closed.
3. **Verify Tests**: Run backend tests for the notification service to ensure no regression.
