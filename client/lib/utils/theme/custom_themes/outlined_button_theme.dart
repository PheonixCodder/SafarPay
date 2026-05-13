import 'package:flutter/material.dart';

import '../../constants/colors.dart';

/* -- Light & Dark Outlined Button Themes -- */
class SOutlinedButtonTheme {
  SOutlinedButtonTheme._(); // To avoid creating instances

  /* -- Light Theme -- */
  static final OutlinedButtonThemeData lightOutlinedButtonTheme =
      OutlinedButtonThemeData(
    style: OutlinedButton.styleFrom(
      elevation: 0,
      foregroundColor: SColors.textPrimary,
      side: const BorderSide(color: SColors.primary),
      textStyle: const TextStyle(
        fontSize: 16,
        color: SColors.textPrimary,
        fontWeight: FontWeight.w600,
      ),
      padding: const EdgeInsets.symmetric(vertical: 16, horizontal: 20),
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
    ),
  );
}
