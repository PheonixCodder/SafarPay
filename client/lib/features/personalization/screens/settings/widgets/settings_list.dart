import 'package:flutter/material.dart';

import '../../../../../utils/constants/sizes.dart';
import '../../../models/settings_menu_item.dart';
import 'settings_menu_tile.dart';

class SSettingsList extends StatelessWidget {
  const SSettingsList({
    super.key,
    required this.items,
    this.onItemTap,
  });

  final List<SSettingsMenuItem> items;
  final VoidCallback? Function(SSettingsMenuItem item, int index)? onItemTap;

  @override
  Widget build(BuildContext context) {
    return ListView.separated(
      shrinkWrap: true,
      physics: const NeverScrollableScrollPhysics(),
      itemCount: items.length,
      separatorBuilder: (context, index) =>
          const SizedBox(height: SSizes.spaceBtnItems),
      itemBuilder: (context, index) => SSettingsMenuTile(
        item: items[index],
        onTap: onItemTap?.call(items[index], index),
      ),
    );
  }
}
