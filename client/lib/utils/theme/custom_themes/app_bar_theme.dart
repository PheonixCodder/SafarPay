import 'package:flutter/material.dart';

import '../../constants/colors.dart';

class SAppBarTheme {
  SAppBarTheme._();

  static const AppBarTheme lightAppBarTheme = AppBarTheme(
    elevation: 0,
    centerTitle: false,
    scrolledUnderElevation: 0,
    backgroundColor: SColors.transparent,
    surfaceTintColor: SColors.transparent,
    iconTheme: IconThemeData(color: SColors.black, size: 24),
    actionsIconTheme: IconThemeData(color: SColors.black, size: 24),
    titleTextStyle: TextStyle(
      fontSize: 18.0,
      fontWeight: FontWeight.w600,
      color: SColors.textPrimary,
    ),
  );
}
