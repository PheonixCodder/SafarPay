import 'package:flutter/material.dart';
import 'package:get/get.dart';

import '../../../../common/widgets/appbar/appbar.dart';
import '../../../../utils/constants/colors.dart';
import '../../../../utils/constants/sizes.dart';
import '../../../../utils/constants/texts.dart';
import 'controllers/notifications_controller.dart';
import 'models/notification_item.dart';
import 'widgets/notification_filter_chips.dart';
import 'widgets/notification_section_label.dart';
import 'widgets/notification_timeline_item.dart';
import 'widgets/notifications_load_error.dart';
import 'widgets/notifications_empty_state.dart';
import 'widgets/notifications_header.dart';

class NotificationsScreen extends StatefulWidget {
  const NotificationsScreen({super.key});

  @override
  State<NotificationsScreen> createState() => _NotificationsScreenState();
}

class _NotificationsScreenState extends State<NotificationsScreen> {
  SNotificationType? _selectedType;
  late final SNotificationsController _controller;

  @override
  void initState() {
    super.initState();
    _controller = Get.isRegistered<SNotificationsController>()
        ? Get.find<SNotificationsController>()
        : Get.put(SNotificationsController(), permanent: true);
    WidgetsBinding.instance.addPostFrameCallback(
      (_) => _controller.refreshInbox(),
    );
  }

  static const List<SNotificationFilterOption> _filters = [
    SNotificationFilterOption(
      label: STexts.notificationsFilterAll,
      type: null,
    ),
    SNotificationFilterOption(
      label: STexts.notificationsFilterTrips,
      type: SNotificationType.trip,
    ),
    SNotificationFilterOption(
      label: STexts.notificationsFilterPayments,
      type: SNotificationType.payment,
    ),
    SNotificationFilterOption(
      label: STexts.notificationsFilterOffers,
      type: SNotificationType.offer,
    ),
    SNotificationFilterOption(
      label: STexts.notificationsFilterSafety,
      type: SNotificationType.safety,
    ),
    SNotificationFilterOption(
      label: STexts.notificationsFilterSystem,
      type: SNotificationType.system,
    ),
  ];

  List<SNotificationItem> get _filteredItems {
    if (_selectedType == null) return _controller.items;
    return _controller.items
        .where((item) => item.type == _selectedType)
        .toList(growable: false);
  }

  int get _unreadCount {
    return _controller.unreadCount.value;
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: SColors.primaryBackground,
      appBar: const SAppBar(
        showBackArrow: true,
        title: Text(STexts.notificationsPageTitle),
      ),
      body: Obx(
        () {
          final filteredItems = _filteredItems;
          return RefreshIndicator(
            onRefresh: _controller.refreshInbox,
            child: SingleChildScrollView(
              physics: const AlwaysScrollableScrollPhysics(),
              child: Padding(
                padding: const EdgeInsets.all(SSizes.defaultSpace),
                child: Column(
                  children: [
                    SNotificationsHeader(
                      totalCount: _controller.totalCount.value,
                      unreadCount: _unreadCount,
                    ),
                    const SizedBox(height: SSizes.spaceBtnItems),
                    SNotificationFilterChips(
                      options: _filters,
                      selectedType: _selectedType,
                      onSelected: (type) =>
                          setState(() => _selectedType = type),
                    ),
                    const SizedBox(height: SSizes.spaceBtnItems),
                    if (_controller.isLoading.value)
                      const Padding(
                        padding: EdgeInsets.symmetric(
                          vertical: SSizes.spaceBtwSections,
                        ),
                        child: CircularProgressIndicator(),
                      )
                    else if (_controller.errorMessage.value != null)
                      SNotificationsLoadError(
                        message: _controller.errorMessage.value!,
                        onRetry: _controller.refreshInbox,
                      )
                    else if (filteredItems.isEmpty)
                      const SNotificationsEmptyState()
                    else
                      ..._buildGroupedNotifications(filteredItems),
                    const SizedBox(height: SSizes.spaceBtwSections),
                  ],
                ),
              ),
            ),
          );
        },
      ),
    );
  }

  List<Widget> _buildGroupedNotifications(List<SNotificationItem> items) {
    final widgets = <Widget>[];
    String? activeGroup;

    for (final item in items) {
      if (item.groupLabel != activeGroup) {
        activeGroup = item.groupLabel;
        widgets.add(SNotificationSectionLabel(label: item.groupLabel));
      }

      widgets
        ..add(SNotificationTimelineItem(item: item))
        ..add(const SizedBox(height: SSizes.sm));
    }

    if (widgets.isNotEmpty) widgets.removeLast();
    return widgets;
  }
}
