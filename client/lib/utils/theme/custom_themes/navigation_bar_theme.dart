import 'package:flutter/material.dart';

import '../../constants/colors.dart';
import '../../constants/typography.dart';

class SNavigationBarTheme {
  SNavigationBarTheme._();

  static NavigationBarThemeData appNavigationBarTheme = NavigationBarThemeData(
    backgroundColor: SColors.surfaceContainerHigh,
    indicatorColor: SColors.primaryContainer.withValues(alpha: 0.2),
    elevation: 8,
    shadowColor: SColors.pureBlack.withValues(alpha: 0.3),
    labelTextStyle: WidgetStateProperty.resolveWith((states) {
      if (states.contains(WidgetState.selected)) {
        return STypography.labelSm.copyWith(color: SColors.gold);
      }
      return STypography.labelSm;
    }),
    iconTheme: WidgetStateProperty.resolveWith((states) {
      if (states.contains(WidgetState.selected)) {
        return const IconThemeData(color: SColors.gold, size: 24);
      }
      return const IconThemeData(color: SColors.onSurfaceVariant, size: 24);
    }),
  );
}
