import 'package:flutter/material.dart';

import '../../constants/colors.dart';

class SBottomSheetTheme {
  SBottomSheetTheme._();

  static const BottomSheetThemeData lightBottomSheetTheme =
      BottomSheetThemeData(
    showDragHandle: true,
    backgroundColor: SColors.white,
    modalBackgroundColor: SColors.white,
    constraints: BoxConstraints(minWidth: double.infinity),
    shape: RoundedRectangleBorder(
      borderRadius: BorderRadius.all(Radius.circular(16)),
    ),
  );
}
