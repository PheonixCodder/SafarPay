import 'package:flutter/material.dart';

import '../../../utils/constants/colors.dart';
import '../../../utils/constants/sizes.dart';

class SCircularContainer extends StatelessWidget {
  const SCircularContainer({
    super.key,
    this.child,
    this.width = SSizes.circularContainerSize,
    this.height = SSizes.circularContainerSize,
    this.radius = SSizes.circularContainerRadius,
    this.margin = 0,
    this.padding = 0,
    this.backgroundColor = SColors.white,
  });

  final double? width;
  final double? height;
  final double radius;
  final double padding;
  final double margin;
  final Widget? child;
  final Color backgroundColor;

  @override
  Widget build(BuildContext context) {
    return Container(
      width: width,
      height: height,
      margin: EdgeInsets.all(margin),
      padding: EdgeInsets.all(padding),
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(radius),
        color: backgroundColor,
      ),
      child: child,
    );
  }
}
