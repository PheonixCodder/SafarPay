import 'package:client/common/navigation/right_slide_page_route.dart';
import 'package:client/utils/constants/sizes.dart';
import 'package:flutter/material.dart';
import 'package:get/get.dart';

import '../controllers/notifications_controller.dart';
import '../notifications.dart';
import 'notification_timeline_item.dart';
import 'notifications_empty_state.dart';

class SNotificationsPopup extends StatelessWidget {
  const SNotificationsPopup({
    super.key,
    required this.controller,
    required this.parentContext,
  });

  final SNotificationsController controller;
  final BuildContext parentContext;

  @override
  Widget build(BuildContext context) {
    return SafeArea(
      top: false,
      child: Padding(
        padding: const EdgeInsets.fromLTRB(
          SSizes.defaultSpace,
          SSizes.md,
          SSizes.defaultSpace,
          SSizes.defaultSpace,
        ),
        child: Obx(() {
          final previewItems = controller.items.take(5).toList(growable: false);
          return Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Row(
                children: [
                  Expanded(
                    child: Text(
                      'Notifications',
                      style: Theme.of(context).textTheme.headlineSmall,
                    ),
                  ),
                  if (controller.unreadCount.value > 0)
                    TextButton(
                      onPressed: controller.markAllRead,
                      child: const Text('Mark read'),
                    ),
                ],
              ),
              if (controller.isLoading.value)
                const Padding(
                  padding:
                      EdgeInsets.symmetric(vertical: SSizes.spaceBtwSections),
                  child: CircularProgressIndicator(),
                )
              else if (controller.errorMessage.value != null)
                Padding(
                  padding: const EdgeInsets.symmetric(vertical: SSizes.lg),
                  child: Column(
                    children: [
                      Text(
                        controller.errorMessage.value!,
                        style: Theme.of(context).textTheme.bodyMedium,
                        textAlign: TextAlign.center,
                      ),
                      const SizedBox(height: SSizes.sm),
                      OutlinedButton(
                        onPressed: controller.refreshInbox,
                        child: const Text('Try again'),
                      ),
                    ],
                  ),
                )
              else if (previewItems.isEmpty)
                const Padding(
                  padding: EdgeInsets.symmetric(vertical: SSizes.lg),
                  child: SNotificationsEmptyState(),
                )
              else
                ...previewItems.map(
                  (item) => Padding(
                    padding: const EdgeInsets.only(bottom: SSizes.sm),
                    child: GestureDetector(
                      child: SNotificationTimelineItem(item: item),
                    ),
                  ),
                ),
              const SizedBox(height: SSizes.sm),
              SizedBox(
                width: double.infinity,
                child: ElevatedButton(
                  onPressed: () {
                    Navigator.of(context).pop();
                    WidgetsBinding.instance.addPostFrameCallback(
                      (_) => Navigator.of(parentContext).push(
                        SRightSlidePageRoute(
                          page: const NotificationsScreen(),
                        ),
                      ),
                    );
                  },
                  child: const Text('View all notifications'),
                ),
              ),
            ],
          );
        }),
      ),
    );
  }
}
