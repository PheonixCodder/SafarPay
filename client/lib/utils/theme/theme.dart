import 'package:flutter/material.dart';

import '../constants/colors.dart';
import 'custom_themes/app_bar_theme.dart';
import 'custom_themes/bottom_sheet_theme.dart';
import 'custom_themes/checkbox_theme.dart';
import 'custom_themes/chip_theme.dart';
import 'custom_themes/elevated_button_theme.dart';
import 'custom_themes/outlined_button_theme.dart';
import 'custom_themes/text_form_field_theme.dart';
import 'custom_themes/text_theme.dart';

class SAppTheme {
  SAppTheme._();

  static ThemeData lightTheme = ThemeData(
    useMaterial3: true,
    fontFamily: 'SF-Pro',
    brightness: Brightness.light,
    primaryColor: SColors.primary,
    scaffoldBackgroundColor: SColors.primaryBackground,
    colorScheme: ColorScheme.fromSeed(
      seedColor: SColors.primary,
      brightness: Brightness.light,
      primary: SColors.primary,
      secondary: SColors.secondary,
      tertiary: SColors.accent,
      surface: SColors.white,
      error: SColors.error,
    ),
    textTheme: STextTheme.lightTextTheme,
    elevatedButtonTheme: SElevatedButtonTheme.lightElevatedButtonTheme,
    appBarTheme: SAppBarTheme.lightAppBarTheme,
    bottomSheetTheme: SBottomSheetTheme.lightBottomSheetTheme,
    checkboxTheme: SCheckboxTheme.lightCheckboxTheme,
    chipTheme: SChipTheme.lightChipTheme,
    outlinedButtonTheme: SOutlinedButtonTheme.lightOutlinedButtonTheme,
    inputDecorationTheme: STextFormFieldTheme.lightInputDecorationTheme,
  );
}
