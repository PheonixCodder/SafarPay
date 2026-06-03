import 'package:flutter/material.dart';

import '../../constants/colors.dart';

class SCheckboxTheme {
  SCheckboxTheme._();

  static CheckboxThemeData appCheckboxTheme = CheckboxThemeData(
    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(4)),
    checkColor: WidgetStateProperty.resolveWith((states) {
      if (states.contains(WidgetState.selected)) {
        return SColors.onPrimary;
      }
      return SColors.onSurfaceVariant;
    }),
    fillColor: WidgetStateProperty.resolveWith((states) {
      if (states.contains(WidgetState.selected)) {
        return SColors.primaryContainer;
      }
      return SColors.transparent;
    }),
    side: const BorderSide(color: SColors.outline),
  );
}
