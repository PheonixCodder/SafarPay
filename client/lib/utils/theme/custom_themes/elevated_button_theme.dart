import 'package:flutter/material.dart';

import '../../constants/colors.dart';

class SElevatedButtonTheme {
  SElevatedButtonTheme._();

  static ElevatedButtonThemeData lightElevatedButtonTheme =
      ElevatedButtonThemeData(
    style: ElevatedButton.styleFrom(
      elevation: 0,
      foregroundColor: SColors.white,
      backgroundColor: SColors.buttonPrimary,
      disabledForegroundColor: SColors.textSecondary,
      disabledBackgroundColor: SColors.buttonDisabled,
      side: const BorderSide(color: SColors.primary),
      padding: const EdgeInsets.symmetric(vertical: 18),
      textStyle: const TextStyle(
        fontSize: 18,
        fontWeight: FontWeight.w600,
        color: SColors.textPrimary,
      ),
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
    ),
  );
}
