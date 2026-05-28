import 'package:client/features/personalization/screens/notifications/models/notification_item.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  test('notification item parses backend payload', () {
    final item = SNotificationItem.fromJson({
      'id': 'notification-1',
      'type': 'trip',
      'title': 'Driver assigned',
      'message': 'Your driver is heading to pickup.',
      'created_at': DateTime.now().toUtc().toIso8601String(),
      'read_at': null,
      'is_unread': true,
      'metadata': {'ride_id': 'ride-1'},
      'deeplink': 'safarpay://rides/ride-1',
    });

    expect(item.id, 'notification-1');
    expect(item.type, SNotificationType.trip);
    expect(item.isUnread, isTrue);
    expect(item.metadata['ride_id'], 'ride-1');
  });
}
