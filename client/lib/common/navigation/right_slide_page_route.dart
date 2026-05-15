import 'package:flutter/material.dart';

import '../../utils/constants/colors.dart';

class SRightSlidePageRoute<T> extends PageRouteBuilder<T> {
  SRightSlidePageRoute({
    required Widget page,
    super.settings,
    Duration duration = _defaultDuration,
    Curve curve = Curves.easeOutCubic,
  }) : super(
         transitionDuration: duration,
         reverseTransitionDuration: duration,
         pageBuilder: (context, animation, secondaryAnimation) => page,
         transitionsBuilder: (context, animation, secondaryAnimation, child) {
           final curvedAnimation = CurvedAnimation(
             parent: animation,
             curve: curve,
             reverseCurve: curve.flipped,
           );

           return FadeTransition(
             opacity: Tween<double>(
               begin: SOpacities.pageTransitionFadeStart,
               end: 1,
             ).animate(curvedAnimation),
             child: SlideTransition(
               position: Tween<Offset>(
                 begin: const Offset(1, 0),
                 end: Offset.zero,
               ).animate(curvedAnimation),
               child: child,
             ),
           );
         },
       );

  static const Duration _defaultDuration = Duration(milliseconds: 320);
}
