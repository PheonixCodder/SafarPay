import 'package:flutter/material.dart';

import '../../constants/colors.dart';

class SChipTheme {
  SChipTheme._(); // Private constructor to avoid instantiation

  static ChipThemeData lightChipTheme = ChipThemeData(
    disabledColor: SColors.grey.withOpacity(0.4),
    labelStyle: const TextStyle(color: SColors.textPrimary),
    selectedColor: SColors.primary,
    padding: const EdgeInsets.symmetric(horizontal: 12.0, vertical: 12),
    checkmarkColor: SColors.white,
  );
}
