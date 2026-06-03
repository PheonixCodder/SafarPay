import 'package:flutter/material.dart';

import '../../constants/colors.dart';
import '../../constants/sizes.dart';

class SBottomSheetTheme {
  SBottomSheetTheme._();

  static const BottomSheetThemeData appBottomSheetTheme = BottomSheetThemeData(
    showDragHandle: true,
    backgroundColor: SColors.surfaceContainer,
    modalBackgroundColor: SColors.surfaceContainer,
    constraints: BoxConstraints(minWidth: double.infinity),
    shape: RoundedRectangleBorder(
      borderRadius: BorderRadius.vertical(
        top: Radius.circular(SSizes.sheetRadiusXl),
      ),
    ),
  );
}
