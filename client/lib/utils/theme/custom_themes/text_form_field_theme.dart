import 'package:flutter/material.dart';

import '../../constants/colors.dart';
import '../../constants/sizes.dart';
import '../../helpers/helpers.dart';

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
      color: SHelperFunctions.withOpacity(
        SColors.textPrimary,
        SOpacities.stronger,
      ),
    ),
    border: OutlineInputBorder(
      borderRadius: BorderRadius.circular(SSizes.inputDecorationRadius),
      borderSide: const BorderSide(
        width: SSizes.inputDecorationBorderWidth,
        color: SColors.borderPrimary,
      ),
    ),
    enabledBorder: OutlineInputBorder(
      borderRadius: BorderRadius.circular(SSizes.inputDecorationRadius),
      borderSide: const BorderSide(
        width: SSizes.inputDecorationBorderWidth,
        color: SColors.borderPrimary,
      ),
    ),
    focusedBorder: OutlineInputBorder(
      borderRadius: BorderRadius.circular(SSizes.inputDecorationRadius),
      borderSide: const BorderSide(
        width: SSizes.inputDecorationBorderWidth,
        color: SColors.primary,
      ),
    ),
    errorBorder: OutlineInputBorder(
      borderRadius: BorderRadius.circular(SSizes.inputDecorationRadius),
      borderSide: const BorderSide(
        width: SSizes.inputDecorationBorderWidth,
        color: SColors.error,
      ),
    ),
    focusedErrorBorder: OutlineInputBorder(
      borderRadius: BorderRadius.circular(SSizes.inputDecorationRadius),
      borderSide: const BorderSide(
        width: SSizes.inputDecorationFocusedErrorBorderWidth,
        color: SColors.warning,
      ),
    ),
  );
}
