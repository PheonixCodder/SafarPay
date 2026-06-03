import 'package:flutter/material.dart';

import '../../constants/colors.dart';
import '../../helpers/helpers.dart';

class SDividerTheme {
  SDividerTheme._();

  static DividerThemeData appDividerTheme = DividerThemeData(
    color: SHelperFunctions.withOpacity(SColors.outline, SOpacities.divider),
    thickness: 1,
    space: 1,
  );
}
