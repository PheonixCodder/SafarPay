import 'package:iconsax/iconsax.dart';

import 'notification_item.dart';

class SNotificationsContent {
  SNotificationsContent._();

  static const List<SNotificationItem> items = [
    SNotificationItem(
      type: SNotificationType.trip,
      icon: Iconsax.car,
      title: 'Driver is arriving',
      message: 'Ali is 3 minutes away from your pickup at Johar Town.',
      timeAgo: '2m',
      groupLabel: 'Today',
      isUnread: true,
    ),
    SNotificationItem(
      type: SNotificationType.payment,
      icon: Iconsax.receipt_2,
      title: 'Payment completed',
      message: 'Rs. 860 was paid for your City ride ending at Gulberg.',
      timeAgo: '18m',
      groupLabel: 'Today',
      isUnread: true,
    ),
    SNotificationItem(
      type: SNotificationType.safety,
      icon: Iconsax.shield_tick,
      title: 'Share your trip status',
      message: 'Send your live ride link to a trusted contact before pickup.',
      timeAgo: '42m',
      groupLabel: 'Today',
    ),
    SNotificationItem(
      type: SNotificationType.offer,
      icon: Iconsax.ticket_discount,
      title: 'Weekend ride offer',
      message: 'Save 15% on your next City ride before Sunday night.',
      timeAgo: '1h',
      groupLabel: 'Today',
    ),
    SNotificationItem(
      type: SNotificationType.trip,
      icon: Iconsax.location_tick,
      title: 'Ride completed',
      message: 'Your trip to European School of Excellence is complete.',
      timeAgo: 'Yesterday',
      groupLabel: 'Yesterday',
    ),
    SNotificationItem(
      type: SNotificationType.system,
      icon: Iconsax.notification_status,
      title: 'Notifications enabled',
      message: 'You will receive ride, payment, safety, and account updates.',
      timeAgo: 'Yesterday',
      groupLabel: 'Yesterday',
    ),
    SNotificationItem(
      type: SNotificationType.payment,
      icon: Iconsax.wallet_check,
      title: 'Cash payment recorded',
      message: 'Your driver collected Rs. 430 for the completed ride.',
      timeAgo: 'Mon',
      groupLabel: 'This week',
    ),
    SNotificationItem(
      type: SNotificationType.system,
      icon: Iconsax.security_user,
      title: 'Account security reminder',
      message: 'Keep your phone number updated to secure OTP verification.',
      timeAgo: 'Mon',
      groupLabel: 'This week',
    ),
  ];
}
