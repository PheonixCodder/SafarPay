import 'package:flutter/material.dart';

import 'colors.dart';

/// Midnight Elite typography — source: [DESIGN.md].
class STypography {
  STypography._();

  static const String plusJakarta = 'PlusJakartaSans';
  static const String inter = 'Inter';

  static const TextStyle displayLg = TextStyle(
    fontFamily: plusJakarta,
    fontSize: 40,
    fontWeight: FontWeight.w700,
    height: 48 / 40,
    letterSpacing: -0.8,
    color: SColors.onSurface,
  );

  static const TextStyle headlineLg = TextStyle(
    fontFamily: plusJakarta,
    fontSize: 32,
    fontWeight: FontWeight.w700,
    height: 40 / 32,
    letterSpacing: -0.32,
    color: SColors.onSurface,
  );

  static const TextStyle headlineLgMobile = TextStyle(
    fontFamily: plusJakarta,
    fontSize: 28,
    fontWeight: FontWeight.w700,
    height: 36 / 28,
    color: SColors.onSurface,
  );

  static const TextStyle titleMd = TextStyle(
    fontFamily: plusJakarta,
    fontSize: 22,
    fontWeight: FontWeight.w600,
    height: 28 / 22,
    color: SColors.onSurface,
  );

  static const TextStyle bodyLg = TextStyle(
    fontFamily: inter,
    fontSize: 16,
    fontWeight: FontWeight.w400,
    height: 24 / 16,
    color: SColors.onSurface,
  );

  static const TextStyle bodyMd = TextStyle(
    fontFamily: inter,
    fontSize: 14,
    fontWeight: FontWeight.w400,
    height: 20 / 14,
    color: SColors.onSurface,
  );

  static const TextStyle labelMd = TextStyle(
    fontFamily: inter,
    fontSize: 12,
    fontWeight: FontWeight.w600,
    height: 16 / 12,
    letterSpacing: 0.6,
    color: SColors.onSurfaceVariant,
  );

  static const TextStyle labelSm = TextStyle(
    fontFamily: inter,
    fontSize: 11,
    fontWeight: FontWeight.w500,
    height: 14 / 11,
    color: SColors.onSurfaceVariant,
  );

  static TextStyle navigationLabel({Color? color}) => labelMd.copyWith(
        letterSpacing: 1.2,
        color: color ?? SColors.onSurfaceVariant,
      );

  static TextTheme toTextTheme() {
    return TextTheme(
      displayLarge: displayLg,
      headlineLarge: headlineLg,
      headlineMedium: headlineLgMobile,
      headlineSmall: titleMd,
      titleLarge: titleMd,
      titleMedium: titleMd.copyWith(fontSize: 18),
      titleSmall: bodyLg.copyWith(fontWeight: FontWeight.w600),
      bodyLarge: bodyLg,
      bodyMedium: bodyMd,
      bodySmall: bodyMd.copyWith(color: SColors.onSurfaceVariant),
      labelLarge: labelMd,
      labelMedium: labelMd,
      labelSmall: labelSm,
    );
  }
}
