import 'package:flutter/material.dart';

import '../../constants/colors.dart';
import '../../constants/sizes.dart';
import '../../helpers/helpers.dart';

class SChipTheme {
  SChipTheme._(); // Private constructor to avoid instantiation

  static ChipThemeData lightChipTheme = ChipThemeData(
    disabledColor: SHelperFunctions.withOpacity(
      SColors.grey,
      SOpacities.chipDisabled,
    ),
    labelStyle: const TextStyle(color: SColors.textPrimary),
    selectedColor: SColors.primary,
    padding: const EdgeInsets.symmetric(
      horizontal: SSizes.chipPaddingHorizontal,
      vertical: SSizes.chipPaddingVertical,
    ),
    checkmarkColor: SColors.white,
  );
}
