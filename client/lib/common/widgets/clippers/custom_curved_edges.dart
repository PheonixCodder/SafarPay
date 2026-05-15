import 'package:flutter/material.dart';

import '../../../utils/constants/sizes.dart';

class SCustomCurvedEdges extends CustomClipper<Path> {
  @override
  Path getClip(Size size) {
    final path = Path()..lineTo(0, size.height);

    final firstCurve = Offset(0, size.height - SSizes.curvedEdgeDepth);
    final lastCurve = Offset(SSizes.curvedEdgeHorizontalInset, size.height - SSizes.curvedEdgeDepth);
    path.quadraticBezierTo(
      firstCurve.dx,
      firstCurve.dy,
      lastCurve.dx,
      lastCurve.dy,
    );

    final secondFirstCurve = Offset(0, size.height - SSizes.curvedEdgeDepth);
    final secondLastCurve = Offset(
      size.width - SSizes.curvedEdgeHorizontalInset,
      size.height - SSizes.curvedEdgeDepth,
    );
    path.quadraticBezierTo(
      secondFirstCurve.dx,
      secondFirstCurve.dy,
      secondLastCurve.dx,
      secondLastCurve.dy,
    );

    final thirdFirstCurve = Offset(size.width, size.height - SSizes.curvedEdgeDepth);
    final thirdLastCurve = Offset(size.width, size.height);
    path.quadraticBezierTo(
      thirdFirstCurve.dx,
      thirdFirstCurve.dy,
      thirdLastCurve.dx,
      thirdLastCurve.dy,
    );

    path
      ..lineTo(size.width, 0)
      ..close();
    return path;
  }

  @override
  bool shouldReclip(covariant CustomClipper<Path> oldClipper) {
    return true;
  }
}
