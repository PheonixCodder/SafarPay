import 'package:flutter/material.dart';

import '../../../utils/constants/colors.dart';
import '../../../utils/constants/sizes.dart';
import '../../../utils/helpers/helpers.dart';
import 'circular_container.dart';
import 'curved_edges_widget.dart';

class SPrimaryHeaderContainer extends StatelessWidget {
  const SPrimaryHeaderContainer({
    super.key,
    required this.child,
    this.height,
  });

  final Widget child;
  final double? height;

  @override
  Widget build(BuildContext context) {
    return SCurvedEdgesWidget(
      child: SizedBox(
        height: height ?? SSizes.primaryHeaderHeight,
        child: Container(
          color: SColors.surfaceContainerHigh,
          child: Stack(
            children: [
              Positioned(
                top: SSizes.primaryHeaderCircleOneTop,
                right: SSizes.primaryHeaderCircleOneRight,
                child: SCircularContainer(
                  backgroundColor: SHelperFunctions.withOpacity(
                    SColors.textWhite,
                    SOpacities.successTint,
                  ),
                ),
              ),
              Positioned(
                top: SSizes.primaryHeaderCircleTwoTop,
                right: SSizes.primaryHeaderCircleTwoRight,
                child: SCircularContainer(
                  backgroundColor: SHelperFunctions.withOpacity(
                    SColors.textWhite,
                    SOpacities.successTint,
                  ),
                ),
              ),
              child,
            ],
          ),
        ),
      ),
    );
  }
}