import 'package:flutter/material.dart';

import '../../constants/colors.dart';
import '../../constants/typography.dart';
import '../../helpers/helpers.dart';

class SOutlinedButtonTheme {
  SOutlinedButtonTheme._();

  static final OutlinedButtonThemeData appOutlinedButtonTheme =
      OutlinedButtonThemeData(
    style: OutlinedButton.styleFrom(
      foregroundColor: SColors.onSurface,
      side: BorderSide(
        color: SHelperFunctions.withOpacity(
          SColors.white,
          SOpacities.outlineButtonStroke,
        ),
      ),
      padding: const EdgeInsets.symmetric(vertical: 16, horizontal: 20),
      textStyle: STypography.bodyMd.copyWith(fontWeight: FontWeight.w600),
      shape: const StadiumBorder(),
    ),
  );
}
