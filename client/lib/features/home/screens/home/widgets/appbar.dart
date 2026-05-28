import 'package:client/common/widgets/appbar/appbar.dart';
import 'package:client/common/widgets/notification.dart';
import 'package:client/features/personalization/screens/notifications/controllers/notifications_controller.dart';
import 'package:client/features/personalization/screens/notifications/widgets/notifications_popup.dart';
import 'package:client/utils/constants/colors.dart';
import 'package:client/utils/constants/texts.dart';
import 'package:flutter/material.dart';
import 'package:get/get.dart';

class SHomeAppBar extends StatelessWidget {
  const SHomeAppBar({
    super.key,
  });

  @override
  Widget build(BuildContext context) {
    final controller = Get.put(SNotificationsController(), permanent: true);
    return SAppBar(
      title: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            STexts.homeAppbarTitle,
            style: Theme.of(context).textTheme.labelMedium,
          ),
          Text(
            STexts.homeAppbarSubTitle,
            style: Theme.of(context).textTheme.headlineMedium,
          ),
        ],
      ),
      actions: [
        Obx(
          () => SNotificationCounterIcon(
            count: controller.unreadCount.value,
            onPressed: () {
              controller.refreshInbox();
              showModalBottomSheet<void>(
                context: context,
                isScrollControlled: true,
                backgroundColor: SColors.white,
                shape: const RoundedRectangleBorder(
                  borderRadius: BorderRadius.vertical(top: Radius.circular(24)),
                ),
                builder: (_) => SNotificationsPopup(
                  controller: controller,
                  parentContext: context,
                ),
              );
            },
            iconColor: SColors.primary,
          ),
        ),
      ],
    );
  }
}
