import 'package:client/utils/constants/colors.dart';
import 'package:client/utils/constants/sizes.dart';
import 'package:flutter/material.dart';

class SRideSwitchTile extends StatelessWidget {
  const SRideSwitchTile({
    super.key,
    required this.label,
    required this.value,
    required this.onChanged,
  });

  final String label;
  final bool value;
  final ValueChanged<bool> onChanged;

  @override
  Widget build(BuildContext context) {
    return SwitchListTile(
      contentPadding: const EdgeInsets.symmetric(
        horizontal: SSizes.sm,
        vertical: SSizes.xs,
      ),
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(SSizes.cardRadiusSm),
        side: const BorderSide(color: SColors.borderSecondary),
      ),
      tileColor: SColors.lightContainer,
      title: Text(
        label,
        style: Theme.of(context).textTheme.bodyMedium?.copyWith(
              color: SColors.textPrimary,
              fontWeight: FontWeight.w700,
            ),
      ),
      value: value,
      onChanged: onChanged,
    );
  }
}
