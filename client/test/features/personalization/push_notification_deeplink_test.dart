import 'package:client/features/rides/navigation/ride_navigation_policy.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  group('sRideIdFromNotificationDeeplink', () {
    test('extracts passenger ride tracking ride id', () {
      expect(
        sRideIdFromNotificationDeeplink('safarpay://rides/ride-001'),
        'ride-001',
      );
    });

    test('extracts driver request ride id', () {
      expect(
        sRideIdFromNotificationDeeplink(
          'safarpay://driver/requests/ride-002',
        ),
        'ride-002',
      );
    });

    test('extracts communication ride id', () {
      expect(
        sRideIdFromNotificationDeeplink(
          'safarpay://communication/rides/ride-003',
        ),
        'ride-003',
      );
    });
  });

  group('communication notification helpers', () {
    test('detects incoming ride call notification data', () {
      expect(
        sIsIncomingRideCallNotificationData({
          'notification_kind': 'communication_call',
          'call_id': 'call-001',
        }),
        isTrue,
      );
      expect(
        sCallIdFromNotificationData({
          'notification_kind': 'communication_call',
          'call_id': 'call-001',
        }),
        'call-001',
      );
    });

    test('ignores non-call notification data', () {
      expect(
        sIsIncomingRideCallNotificationData({
          'notification_kind': 'communication_message',
        }),
        isFalse,
      );
      expect(
        sCallIdFromNotificationData({
          'notification_kind': 'communication_message',
        }),
        isNull,
      );
    });
  });
}
