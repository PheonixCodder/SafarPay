import 'package:flutter/material.dart';
import 'package:get/get.dart';

class SAuthNavigation {
  SAuthNavigation._();

  static const Duration _duration = Duration(milliseconds: 350);
  static const Curve _curve = Curves.easeOutCubic;
  static const Offset _beginOffset = Offset(0.06, 0);

  static Future<T?>? to<T>(Widget page) {
    final context = Get.context;
    if (context == null) return null;

    return toFrom<T>(context, page);
  }

  static Future<T?> toFrom<T>(BuildContext context, Widget page) {
    return Navigator.of(context).push<T>(pageRoute<T>(page));
  }

  static Future<T?>? offAll<T>(Widget page) {
    final context = Get.context;
    if (context == null) return null;

    return offAllFrom<T>(context, page);
  }

  static Future<T?> offAllFrom<T>(BuildContext context, Widget page) {
    return Navigator.of(context).pushAndRemoveUntil<T>(
      pageRoute<T>(page),
      (_) => false,
    );
  }

  static Route<T> pageRoute<T>(Widget page) {
    return PageRouteBuilder<T>(
      transitionDuration: _duration,
      reverseTransitionDuration: _duration,
      pageBuilder: (_, __, ___) => page,
      transitionsBuilder: (_, animation, __, child) {
        final curvedAnimation = CurvedAnimation(
          parent: animation,
          curve: _curve,
        );

        return FadeTransition(
          opacity: curvedAnimation,
          child: SlideTransition(
            position: Tween<Offset>(
              begin: _beginOffset,
              end: Offset.zero,
            ).animate(curvedAnimation),
            child: child,
          ),
        );
      },
    );
  }
}
