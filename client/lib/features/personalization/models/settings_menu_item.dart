import 'package:flutter/material.dart';

class SSettingsMenuItem {
  const SSettingsMenuItem({
    required this.icon,
    required this.title,
    required this.subtitle,
    this.trailingText,
  });

  final IconData icon;
  final String title;
  final String subtitle;
  final String? trailingText;
}
