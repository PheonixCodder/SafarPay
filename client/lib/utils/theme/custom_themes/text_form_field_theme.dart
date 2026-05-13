import 'package:flutter/material.dart';

import '../../constants/colors.dart';

class STextFormFieldTheme {
  STextFormFieldTheme._();

  static InputDecorationTheme lightInputDecorationTheme = InputDecorationTheme(
    errorMaxLines: 3,
    prefixIconColor: SColors.darkGrey,
    suffixIconColor: SColors.darkGrey,
    labelStyle: const TextStyle().copyWith(
      fontSize: 14,
      color: SColors.textPrimary,
    ),
    hintStyle: const TextStyle().copyWith(
      fontSize: 14,
      color: SColors.textSecondary,
    ),
    errorStyle: const TextStyle().copyWith(fontStyle: FontStyle.normal),
    floatingLabelStyle: const TextStyle().copyWith(
      color: SColors.textPrimary.withOpacity(0.8),
    ),
    border: OutlineInputBorder(
      borderRadius: BorderRadius.circular(14),
      borderSide: const BorderSide(width: 1, color: SColors.borderPrimary),
    ),
    enabledBorder: OutlineInputBorder(
      borderRadius: BorderRadius.circular(14),
      borderSide: const BorderSide(width: 1, color: SColors.borderPrimary),
    ),
    focusedBorder: OutlineInputBorder(
      borderRadius: BorderRadius.circular(14),
      borderSide: const BorderSide(width: 1, color: SColors.primary),
    ),
    errorBorder: OutlineInputBorder(
      borderRadius: BorderRadius.circular(14),
      borderSide: const BorderSide(width: 1, color: SColors.error),
    ),
    focusedErrorBorder: OutlineInputBorder(
      borderRadius: BorderRadius.circular(14),
      borderSide: const BorderSide(width: 2, color: SColors.warning),
    ),
  );
}
