import 'package:flutter/material.dart';

import '../../constants/colors.dart';
import '../../constants/sizes.dart';
import '../../constants/typography.dart';
import '../../helpers/helpers.dart';

class SChipTheme {
  SChipTheme._();

  static ChipThemeData appChipTheme = ChipThemeData(
    disabledColor: SHelperFunctions.withOpacity(
      SColors.surfaceContainerHighest,
      SOpacities.chipDisabled,
    ),
    labelStyle: STypography.bodyMd,
    selectedColor: SColors.primaryContainer,
    padding: const EdgeInsets.symmetric(
      horizontal: SSizes.chipPaddingHorizontal,
      vertical: SSizes.chipPaddingVertical,
    ),
    checkmarkColor: SColors.onPrimary,
    side: BorderSide(
      color: SHelperFunctions.withOpacity(
        SColors.white,
        SOpacities.outlineButtonStroke,
      ),
    ),
    shape: const StadiumBorder(),
  );
}
