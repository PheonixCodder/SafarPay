import 'package:flutter/material.dart';

import '../../../../../utils/constants/sizes.dart';

class SRideRouteDot extends StatelessWidget {
  const SRideRouteDot({
    super.key,
    required this.color,
  });

  final Color color;

  @override
  Widget build(BuildContext context) {
    return Container(
      width: SSizes.tripsRouteDotSize,
      height: SSizes.tripsRouteDotSize,
      decoration: BoxDecoration(color: color, shape: BoxShape.circle),
    );
  }
}
