import 'package:flutter/widgets.dart';

class SNavigationDestinationData {
  const SNavigationDestinationData({
    required this.icon,
    required this.activeIcon,
    required this.label,
  });

  final IconData icon;
  final IconData activeIcon;
  final String label;
}
