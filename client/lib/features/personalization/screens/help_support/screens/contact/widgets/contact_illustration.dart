import 'package:flutter/material.dart';
import 'package:iconsax/iconsax.dart';

import '../../../../../../../utils/constants/colors.dart';
import '../../../../../../../utils/constants/sizes.dart';
import '../../../../../../../utils/helpers/helpers.dart';

class SContactIllustration extends StatelessWidget {
  const SContactIllustration({super.key});

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      height: 230,
      child: Stack(
        alignment: Alignment.center,
        children: [
          CustomPaint(
            size: const Size(250, 205),
            painter: _ContactIllustrationPainter(),
          ),
          Positioned(
            top: 18,
            left: 48,
            child: _ContactBubble(icon: Iconsax.call),
          ),
          Positioned(
            top: 8,
            child: _ContactBubble(icon: Iconsax.camera),
          ),
          Positioned(
            top: 34,
            right: 42,
            child: _ContactBubble(icon: Iconsax.message_text),
          ),
          Positioned(
            top: 74,
            left: 28,
            child: _ContactBubble(icon: Iconsax.message),
          ),
          Positioned(
            bottom: 28,
            child: Column(
              children: [
                Container(
                  width: 58,
                  height: 78,
                  decoration: BoxDecoration(
                    color: SColors.textPrimary,
                    borderRadius: BorderRadius.circular(24),
                  ),
                  child: Align(
                    alignment: Alignment.topCenter,
                    child: Container(
                      width: 42,
                      height: 42,
                      margin: const EdgeInsets.only(top: 6),
                      decoration: BoxDecoration(
                        color: SColors.white,
                        borderRadius: BorderRadius.circular(20),
                      ),
                    ),
                  ),
                ),
                Container(
                  width: 92,
                  height: 92,
                  decoration: const BoxDecoration(
                    color: SColors.info,
                    borderRadius: BorderRadius.only(
                      topLeft: Radius.circular(44),
                      topRight: Radius.circular(44),
                      bottomLeft: Radius.circular(10),
                      bottomRight: Radius.circular(10),
                    ),
                  ),
                ),
              ],
            ),
          ),
          Positioned(
            bottom: 44,
            left: 54,
            child: Container(
              width: 50,
              height: 62,
              decoration: BoxDecoration(
                color: SColors.darkerGrey,
                borderRadius: BorderRadius.circular(8),
              ),
            ),
          ),
        ],
      ),
    );
  }
}

class _ContactBubble extends StatelessWidget {
  const _ContactBubble({required this.icon});

  final IconData icon;

  @override
  Widget build(BuildContext context) {
    return Container(
      width: 58,
      height: 58,
      decoration: BoxDecoration(
        color: SColors.white,
        shape: BoxShape.circle,
        border: Border.all(color: SColors.borderSecondary),
        boxShadow: [
          BoxShadow(
            color: SHelperFunctions.withOpacity(
              SColors.pureBlack,
              SOpacities.light,
            ),
            blurRadius: 12,
            offset: const Offset(0, 6),
          ),
        ],
      ),
      child: Icon(icon, color: SColors.textPrimary, size: SSizes.iconMd),
    );
  }
}

class _ContactIllustrationPainter extends CustomPainter {
  @override
  void paint(Canvas canvas, Size size) {
    final accentPaint = Paint()
      ..color = SHelperFunctions.withOpacity(SColors.accent, 0.55);
    final linePaint = Paint()
      ..color = SColors.borderPrimary
      ..style = PaintingStyle.stroke
      ..strokeWidth = 1.4;

    canvas.drawCircle(
      Offset(size.width * 0.50, size.height * 0.56),
      84,
      accentPaint,
    );
    canvas.drawCircle(
      Offset(size.width * 0.84, size.height * 0.18),
      34,
      linePaint,
    );
    canvas.drawCircle(
      Offset(size.width * 0.90, size.height * 0.20),
      26,
      linePaint,
    );

    final plantPaint = Paint()
      ..color = SColors.white
      ..style = PaintingStyle.fill;
    final plantStroke = Paint()
      ..color = SColors.borderPrimary
      ..style = PaintingStyle.stroke
      ..strokeWidth = 1.3;

    for (final center in [
      Offset(size.width * 0.79, size.height * 0.72),
      Offset(size.width * 0.84, size.height * 0.62),
      Offset(size.width * 0.90, size.height * 0.72),
    ]) {
      canvas.drawOval(
        Rect.fromCenter(center: center, width: 18, height: 38),
        plantPaint,
      );
      canvas.drawOval(
        Rect.fromCenter(center: center, width: 18, height: 38),
        plantStroke,
      );
    }

    canvas.drawLine(
      Offset(size.width * 0.16, size.height * 0.92),
      Offset(size.width * 0.86, size.height * 0.92),
      linePaint,
    );
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => false;
}
