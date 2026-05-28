import 'package:flutter/material.dart';
import 'package:iconsax/iconsax.dart';

enum SNotificationType {
  trip,
  payment,
  offer,
  safety,
  system,
}

class SNotificationItem {
  const SNotificationItem({
    this.id,
    required this.type,
    IconData? icon,
    required this.title,
    required this.message,
    required this.timeAgo,
    required this.groupLabel,
    this.createdAt,
    this.readAt,
    this.deeplink,
    this.metadata = const {},
    this.isUnread = false,
  }) : icon = icon ?? Iconsax.notification_status;

  final String? id;
  final SNotificationType type;
  final IconData icon;
  final String title;
  final String message;
  final String timeAgo;
  final String groupLabel;
  final DateTime? createdAt;
  final DateTime? readAt;
  final String? deeplink;
  final Map<String, dynamic> metadata;
  final bool isUnread;

  factory SNotificationItem.fromJson(Map<String, dynamic> json) {
    final type = _parseType(json['type'] as String?);
    final createdAt = DateTime.tryParse(json['created_at'] as String? ?? '');
    final readAt = DateTime.tryParse(json['read_at'] as String? ?? '');
    return SNotificationItem(
      id: json['id'] as String?,
      type: type,
      icon: iconForType(type),
      title: json['title'] as String? ?? 'SafarPay update',
      message: json['message'] as String? ?? '',
      timeAgo: _timeAgo(createdAt),
      groupLabel: _groupLabel(createdAt),
      createdAt: createdAt,
      readAt: readAt,
      deeplink: json['deeplink'] as String?,
      metadata: (json['metadata'] as Map?)?.cast<String, dynamic>() ?? const {},
      isUnread: json['is_unread'] as bool? ?? readAt == null,
    );
  }

  static IconData iconForType(SNotificationType type) {
    return switch (type) {
      SNotificationType.trip => Iconsax.car,
      SNotificationType.payment => Iconsax.receipt_2,
      SNotificationType.offer => Iconsax.ticket_discount,
      SNotificationType.safety => Iconsax.shield_tick,
      SNotificationType.system => Iconsax.notification_status,
    };
  }

  static SNotificationType _parseType(String? value) {
    return SNotificationType.values.firstWhere(
      (type) => type.name == value,
      orElse: () => SNotificationType.system,
    );
  }

  static String _timeAgo(DateTime? createdAt) {
    if (createdAt == null) return '';
    final diff = DateTime.now().difference(createdAt.toLocal());
    if (diff.inMinutes < 1) return 'Now';
    if (diff.inMinutes < 60) return '${diff.inMinutes}m';
    if (diff.inHours < 24) return '${diff.inHours}h';
    if (diff.inDays == 1) return 'Yesterday';
    if (diff.inDays < 7) return '${diff.inDays}d';
    return '${createdAt.day}/${createdAt.month}/${createdAt.year}';
  }

  static String _groupLabel(DateTime? createdAt) {
    if (createdAt == null) return 'Earlier';
    final local = createdAt.toLocal();
    final now = DateTime.now();
    final today = DateTime(now.year, now.month, now.day);
    final day = DateTime(local.year, local.month, local.day);
    final diff = today.difference(day).inDays;
    if (diff == 0) return 'Today';
    if (diff == 1) return 'Yesterday';
    if (diff < 7) return 'This week';
    return 'Earlier';
  }
}
