import 'package:flutter/material.dart';

import '../../constants/colors.dart';

class SCheckboxTheme {
  SCheckboxTheme._(); // To avoid creating instances

  // Customizable Light Checkbox Theme
  static CheckboxThemeData lightCheckboxTheme = CheckboxThemeData(
    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(4)),
    checkColor: MaterialStateProperty.resolveWith((states) {
      if (states.contains(MaterialState.selected)) {
        return SColors.white;
      } else {
        return SColors.black;
      }
    }),
    fillColor: MaterialStateProperty.resolveWith((states) {
      if (states.contains(MaterialState.selected)) {
        return SColors.primary;
      } else {
        return SColors.transparent;
      }
    }),
  );
}
