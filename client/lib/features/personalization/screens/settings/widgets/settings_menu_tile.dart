import 'package:flutter/material.dart';
import 'package:iconsax/iconsax.dart';

import '../../../../../utils/constants/colors.dart';
import '../../../models/settings_menu_item.dart';

class SSettingsMenuTile extends StatelessWidget {
  const SSettingsMenuTile({
    super.key,
    required this.item,
    this.onTap,
  });

  final SSettingsMenuItem item;
  final VoidCallback? onTap;

  @override
  Widget build(BuildContext context) {
    return ListTile(
      leading: Icon(item.icon, color: SColors.textPrimary),
      title: Text(item.title),
      subtitle: Text(item.subtitle),
      trailing: item.trailingText != null && item.trailingText!.isNotEmpty
          ? Text(item.trailingText!)
          : const Icon(Iconsax.arrow_right_3),
      onTap: onTap,
    );
  }
}
