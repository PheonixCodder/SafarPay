import 'package:flutter/material.dart';

import '../../constants/colors.dart';
import '../../constants/typography.dart';

class SElevatedButtonTheme {
  SElevatedButtonTheme._();

  static ElevatedButtonThemeData appElevatedButtonTheme =
      ElevatedButtonThemeData(
    style: ElevatedButton.styleFrom(
      elevation: 0,
      shadowColor: SColors.gold.withValues(alpha: SOpacities.goldGlow),
      foregroundColor: SColors.onPrimary,
      backgroundColor: SColors.primaryContainer,
      disabledForegroundColor: SColors.onSurfaceVariant,
      disabledBackgroundColor: SColors.buttonDisabled,
      padding: const EdgeInsets.symmetric(vertical: 18, horizontal: 24),
      textStyle: STypography.bodyLg.copyWith(
        fontWeight: FontWeight.w600,
        color: SColors.onPrimary,
      ),
      shape: const StadiumBorder(),
    ),
  );
}
