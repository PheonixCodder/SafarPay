import 'package:flutter/material.dart';

import '../../../../../utils/constants/colors.dart';
import '../../../../../utils/constants/sizes.dart';
import '../../../../../utils/helpers/helpers.dart';
import '../notification_item.dart';

class SNotificationFilterOption {
  const SNotificationFilterOption({
    required this.label,
    required this.type,
  });

  final String label;
  final SNotificationType? type;
}

class SNotificationFilterChips extends StatelessWidget {
  const SNotificationFilterChips({
    super.key,
    required this.options,
    required this.selectedType,
    required this.onSelected,
  });

  final List<SNotificationFilterOption> options;
  final SNotificationType? selectedType;
  final ValueChanged<SNotificationType?> onSelected;

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      height: SSizes.notificationFilterHeight,
      child: ListView.separated(
        scrollDirection: Axis.horizontal,
        itemCount: options.length,
        separatorBuilder: (context, index) => const SizedBox(width: SSizes.sm),
        itemBuilder: (context, index) {
          final option = options[index];
          final isSelected = option.type == selectedType;

          return ChoiceChip(
            label: Text(option.label),
            selected: isSelected,
            showCheckmark: false,
            labelStyle: Theme.of(context).textTheme.labelLarge?.copyWith(
                  color: isSelected ? SColors.white : SColors.textSecondary,
                  fontWeight: isSelected ? FontWeight.w700 : FontWeight.w500,
                ),
            selectedColor: SColors.primary,
            backgroundColor: SColors.white,
            side: BorderSide(
              color: isSelected
                  ? SColors.primary
                  : SHelperFunctions.withOpacity(
                      SColors.borderSecondary,
                      SOpacities.strong,
                    ),
            ),
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(SSizes.radiusFull),
            ),
            onSelected: (_) => onSelected(option.type),
          );
        },
      ),
    );
  }
}
