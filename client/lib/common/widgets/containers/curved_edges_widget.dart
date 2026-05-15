import 'package:flutter/material.dart';

import '../clippers/custom_curved_edges.dart';

class SCurvedEdgesWidget extends StatelessWidget {
  const SCurvedEdgesWidget({
    super.key,
    required this.child,
  });

  final Widget child;

  @override
  Widget build(BuildContext context) {
    return ClipPath(
      clipper: SCustomCurvedEdges(),
      child: child,
    );
  }
}
