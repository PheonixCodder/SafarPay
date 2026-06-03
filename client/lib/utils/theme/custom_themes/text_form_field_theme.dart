import 'package:flutter/material.dart';

import '../../constants/colors.dart';
import '../../constants/sizes.dart';
import '../../constants/typography.dart';
import '../../helpers/helpers.dart';

class STextFormFieldTheme {
  STextFormFieldTheme._();

  static InputDecorationTheme appInputDecorationTheme = InputDecorationTheme(
    filled: true,
    fillColor: SColors.inputFill,
    errorMaxLines: 3,
    prefixIconColor: SColors.onSurfaceVariant,
    suffixIconColor: SColors.onSurfaceVariant,
    labelStyle: STypography.bodyMd,
    hintStyle: STypography.bodyMd.copyWith(color: SColors.onSurfaceVariant),
    errorStyle: STypography.labelSm.copyWith(color: SColors.error),
    floatingLabelStyle: STypography.labelMd.copyWith(
      color: SHelperFunctions.withOpacity(
        SColors.onSurface,
        SOpacities.stronger,
      ),
    ),
    border: OutlineInputBorder(
      borderRadius: BorderRadius.circular(SSizes.radiusPill),
      borderSide: BorderSide.none,
    ),
    enabledBorder: OutlineInputBorder(
      borderRadius: BorderRadius.circular(SSizes.radiusPill),
      borderSide: BorderSide.none,
    ),
    focusedBorder: OutlineInputBorder(
      borderRadius: BorderRadius.circular(SSizes.radiusPill),
      borderSide: const BorderSide(color: SColors.gold, width: 1.5),
    ),
    errorBorder: OutlineInputBorder(
      borderRadius: BorderRadius.circular(SSizes.radiusPill),
      borderSide: const BorderSide(color: SColors.error),
    ),
    focusedErrorBorder: OutlineInputBorder(
      borderRadius: BorderRadius.circular(SSizes.radiusPill),
      borderSide: const BorderSide(
        width: SSizes.inputDecorationFocusedErrorBorderWidth,
        color: SColors.error,
      ),
    ),
  );
}
