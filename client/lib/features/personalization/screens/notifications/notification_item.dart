import 'package:flutter/material.dart';

enum SNotificationType {
  trip,
  payment,
  offer,
  safety,
  system,
}

class SNotificationItem {
  const SNotificationItem({
    required this.type,
    required this.icon,
    required this.title,
    required this.message,
    required this.timeAgo,
    required this.groupLabel,
    this.isUnread = false,
  });

  final SNotificationType type;
  final IconData icon;
  final String title;
  final String message;
  final String timeAgo;
  final String groupLabel;
  final bool isUnread;
}
