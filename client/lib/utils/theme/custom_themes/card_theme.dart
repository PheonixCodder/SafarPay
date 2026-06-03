import 'package:flutter/material.dart';

import '../../constants/colors.dart';
import '../../constants/sizes.dart';

class SCardTheme {
  SCardTheme._();

  static CardThemeData appCardTheme = CardThemeData(
    color: SColors.surfaceContainer,
    elevation: 0,
    margin: EdgeInsets.zero,
    shape: RoundedRectangleBorder(
      borderRadius: BorderRadius.circular(SSizes.cardRadiusLg),
      side: const BorderSide(color: SColors.outlineVariant, width: 0.5),
    ),
  );
}
