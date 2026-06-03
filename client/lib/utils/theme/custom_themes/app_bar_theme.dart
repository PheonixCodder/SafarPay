import 'package:flutter/material.dart';

import '../../constants/colors.dart';
import '../../constants/typography.dart';

class SAppBarTheme {
  SAppBarTheme._();

  static const AppBarTheme appAppBarTheme = AppBarTheme(
    elevation: 0,
    centerTitle: false,
    scrolledUnderElevation: 0,
    backgroundColor: SColors.transparent,
    surfaceTintColor: SColors.transparent,
    iconTheme: IconThemeData(color: SColors.onSurface, size: 24),
    actionsIconTheme: IconThemeData(color: SColors.onSurface, size: 24),
    titleTextStyle: STypography.titleMd,
  );
}
