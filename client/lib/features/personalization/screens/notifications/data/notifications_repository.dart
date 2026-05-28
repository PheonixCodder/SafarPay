import 'package:client/utils/constants/api_constants.dart';
import 'package:client/utils/http/client.dart';

import '../models/notification_item.dart';

class SNotificationsPage {
  const SNotificationsPage({
    required this.items,
    required this.total,
    required this.unreadCount,
  });

  final List<SNotificationItem> items;
  final int total;
  final int unreadCount;
}

class SNotificationsRepository {
  Future<SNotificationsPage> list({
    int limit = 30,
    int offset = 0,
    bool unreadOnly = false,
  }) async {
    final response = await SHttpClient.get(
      '/notifications?limit=$limit&offset=$offset&unread_only=$unreadOnly',
      service: SApiService.notification,
      requiresAuth: true,
    );
    final data = response['data'];
    final items = data is List
        ? data
            .whereType<Map<String, dynamic>>()
            .map(SNotificationItem.fromJson)
            .toList(growable: false)
        : <SNotificationItem>[];
    return SNotificationsPage(
      items: items,
      total: response['total'] as int? ?? items.length,
      unreadCount: response['unread_count'] as int? ?? 0,
    );
  }

  Future<int> unreadCount() async {
    final response = await SHttpClient.get(
      '/notifications/unread-count',
      service: SApiService.notification,
      requiresAuth: true,
    );
    return response['unread_count'] as int? ?? 0;
  }

  Future<void> markRead(String notificationId) async {
    await SHttpClient.post(
      '/notifications/$notificationId/read',
      service: SApiService.notification,
      requiresAuth: true,
    );
  }

  Future<void> markAllRead() async {
    await SHttpClient.post(
      '/notifications/read-all',
      service: SApiService.notification,
      requiresAuth: true,
    );
  }
}
