import 'package:flutter/material.dart';
import 'package:iconsax/iconsax.dart';

import '../../../../../../../utils/constants/colors.dart';
import '../../../../../../../utils/constants/sizes.dart';

class SFaqSearchField extends StatelessWidget {
  const SFaqSearchField({
    super.key,
    this.onChanged,
  });

  final ValueChanged<String>? onChanged;

  @override
  Widget build(BuildContext context) {
    return TextField(
      onChanged: onChanged,
      textInputAction: TextInputAction.search,
      decoration: InputDecoration(
        hintText: 'Search help articles...',
        prefixIcon: const Icon(
          Iconsax.search_normal,
          size: SSizes.iconSm,
          color: SColors.textSecondary,
        ),
        filled: true,
        fillColor: SColors.white,
        contentPadding: const EdgeInsets.symmetric(
          horizontal: SSizes.md,
          vertical: SSizes.md,
        ),
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(SSizes.inputFieldRadius),
          borderSide: const BorderSide(color: SColors.borderSecondary),
        ),
        enabledBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(SSizes.inputFieldRadius),
          borderSide: const BorderSide(color: SColors.borderSecondary),
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(SSizes.inputFieldRadius),
          borderSide: const BorderSide(color: SColors.primary),
        ),
      ),
    );
  }
}
