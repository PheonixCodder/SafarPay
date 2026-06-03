import 'package:flutter/material.dart';

import '../constants/colors.dart';
import 'custom_themes/app_bar_theme.dart';
import 'custom_themes/bottom_sheet_theme.dart';
import 'custom_themes/card_theme.dart';
import 'custom_themes/checkbox_theme.dart';
import 'custom_themes/chip_theme.dart';
import 'custom_themes/divider_theme.dart';
import 'custom_themes/elevated_button_theme.dart';
import 'custom_themes/navigation_bar_theme.dart';
import 'custom_themes/outlined_button_theme.dart';
import 'custom_themes/text_form_field_theme.dart';
import 'custom_themes/text_theme.dart';

class SAppTheme {
  SAppTheme._();

  static const ColorScheme _colorScheme = ColorScheme(
    brightness: Brightness.dark,
    primary: SColors.primary,
    onPrimary: SColors.onPrimary,
    primaryContainer: SColors.primaryContainer,
    onPrimaryContainer: SColors.onPrimaryContainer,
    secondary: SColors.secondary,
    onSecondary: SColors.onSecondary,
    secondaryContainer: SColors.secondaryContainer,
    onSecondaryContainer: SColors.onSecondaryContainer,
    tertiary: SColors.tertiary,
    onTertiary: SColors.onTertiary,
    tertiaryContainer: SColors.tertiaryContainer,
    onTertiaryContainer: SColors.onTertiaryContainer,
    error: SColors.error,
    onError: SColors.onError,
    errorContainer: SColors.errorContainer,
    onErrorContainer: SColors.onErrorContainer,
    surface: SColors.surface,
    onSurface: SColors.onSurface,
    onSurfaceVariant: SColors.onSurfaceVariant,
    outline: SColors.outline,
    outlineVariant: SColors.outlineVariant,
    shadow: SColors.pureBlack,
    scrim: SColors.pureBlack,
    inverseSurface: SColors.inverseSurface,
    onInverseSurface: SColors.onInverseSurface,
    inversePrimary: SColors.inversePrimary,
    surfaceTint: SColors.surfaceTint,
  );

  static ThemeData appTheme = ThemeData(
    useMaterial3: true,
    brightness: Brightness.dark,
    colorScheme: _colorScheme,
    scaffoldBackgroundColor: SColors.background,
    textTheme: STextTheme.appTextTheme,
    elevatedButtonTheme: SElevatedButtonTheme.appElevatedButtonTheme,
    outlinedButtonTheme: SOutlinedButtonTheme.appOutlinedButtonTheme,
    appBarTheme: SAppBarTheme.appAppBarTheme,
    bottomSheetTheme: SBottomSheetTheme.appBottomSheetTheme,
    checkboxTheme: SCheckboxTheme.appCheckboxTheme,
    chipTheme: SChipTheme.appChipTheme,
    inputDecorationTheme: STextFormFieldTheme.appInputDecorationTheme,
    cardTheme: SCardTheme.appCardTheme,
    dividerTheme: SDividerTheme.appDividerTheme,
    navigationBarTheme: SNavigationBarTheme.appNavigationBarTheme,
    splashColor: SColors.gold.withValues(alpha: SOpacities.tinted),
    highlightColor: SColors.gold.withValues(alpha: SOpacities.soft),
  );

  @Deprecated('Use SAppTheme.appTheme')
  static ThemeData get lightTheme => appTheme;
}
