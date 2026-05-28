import 'package:get/get.dart';

import '../data/notifications_repository.dart';
import '../models/notification_item.dart';

class SNotificationsController extends GetxController {
  SNotificationsController({SNotificationsRepository? repository})
      : _repository = repository ?? SNotificationsRepository();

  final SNotificationsRepository _repository;

  final items = <SNotificationItem>[].obs;
  final isLoading = false.obs;
  final errorMessage = RxnString();
  final unreadCount = 0.obs;
  final totalCount = 0.obs;
  Future<void>? _refreshInFlight;

  @override
  void onInit() {
    super.onInit();
    refreshInbox();
  }

  Future<void> refreshInbox() async {
    final inFlight = _refreshInFlight;
    if (inFlight != null) return inFlight;
    final refresh = _refreshInboxInternal();
    _refreshInFlight = refresh;
    return refresh.whenComplete(() => _refreshInFlight = null);
  }

  Future<void> _refreshInboxInternal() async {
    isLoading.value = true;
    errorMessage.value = null;
    try {
      final page = await _repository.list();
      items.assignAll(page.items);
      unreadCount.value = page.unreadCount;
      totalCount.value = page.total;
    } catch (_) {
      errorMessage.value = 'Unable to load notifications right now.';
    } finally {
      isLoading.value = false;
    }
  }

  Future<void> refreshUnreadCount() async {
    try {
      unreadCount.value = await _repository.unreadCount();
    } catch (_) {
      // Keep the last known count; the inbox fetch will surface detailed errors.
    }
  }

  Future<void> markRead(SNotificationItem item) async {
    final id = item.id;
    if (id == null) return;
    await _repository.markRead(id);
    await refreshInbox();
  }

  Future<void> markAllRead() async {
    await _repository.markAllRead();
    await refreshInbox();
  }
}
